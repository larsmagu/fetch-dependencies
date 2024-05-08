import os
import json
import requests

def get_npm_package_info(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        package_data = response.json()
        if 'license' in package_data:
            return package_data['license']
    return None

def get_composer_package_info(package_name):
    url = f"https://repo.packagist.org/p/{package_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        package_data = response.json()
        if 'package' in package_data and 'license' in package_data['package']:
            return package_data['package']['license']
    return None

def get_composer_dependency_info(lock_file):
    dependency_info = {}

    if os.path.exists(lock_file):
        with open(lock_file) as f:
            data = json.load(f)
            if 'packages' in data:
                for package in data['packages']:
                    name = package.get('name', '')
                    license = package.get('license', 'No license specified')
                    dependency_info[name] = license

    return dependency_info

def get_composer_json_dependency_info(json_file):
    dependency_info = {}

    if os.path.exists(json_file):
        with open(json_file) as f:
            data = json.load(f)
            if 'require' in data:
                for dep, version in data['require'].items():
                    license = get_composer_package_info(dep)
                    if license is not None:
                        dependency_info[dep] = license
                    else:
                        dependency_info[dep] = 'License not found'

    return dependency_info

def get_production_dependencies(repo_path):
    dependencies = []

    # Check for package.json and fetch dependencies if present
    package_json_file = os.path.join(repo_path, 'package.json')
    if os.path.exists(package_json_file):
        with open(package_json_file) as f:
            data = json.load(f)
            if 'dependencies' in data:
                for dep, version in data['dependencies'].items():
                    license = get_npm_package_info(dep)
                    if license is not None:
                        dependencies.append(f"{dep} ({license})")
                    else:
                        dependencies.append(f"{dep} (License not found)")

    # Check for composer.json and fetch dependencies if present
    composer_json_file = os.path.join(repo_path, 'composer.json')
    if os.path.exists(composer_json_file):
        composer_lock_file = os.path.join(repo_path, 'composer.lock')
        # Fetch dependencies and licenses from composer.lock
        lock_dependency_info = get_composer_dependency_info(composer_lock_file)
        # Fetch dependencies and licenses from composer.json
        json_dependency_info = get_composer_json_dependency_info(composer_json_file)
        for dep, license in json_dependency_info.items():
            if dep in lock_dependency_info:
                dependencies.append(f"{dep} ({lock_dependency_info[dep]})")
            else:
                dependencies.append(f"{dep} ({license})")

    return dependencies

def main():
    repos_folder = os.path.expanduser('PATH/TO/REPOS')  # Replace with your absolute path
    dependency_repo_map = {}

    # Iterate through repositories
    for repo_name in os.listdir(repos_folder):
        repo_path = os.path.join(repos_folder, repo_name)
        if os.path.isdir(repo_path):
            # Get production dependencies for each repository
            dependencies = get_production_dependencies(repo_path)
            # Update dependency_repo_map with repositories for each dependency
            for dependency in dependencies:
                if dependency not in dependency_repo_map:
                    dependency_repo_map[dependency] = {repo_name}
                else:
                    dependency_repo_map[dependency].add(repo_name)

    # Print the dependencies and the repositories where they are used
    print("Production dependencies and the repositories where they are used:")
    for dependency, repositories in dependency_repo_map.items():
        print(f"{dependency}: {', '.join(repositories)}")

if __name__ == "__main__":
    main()

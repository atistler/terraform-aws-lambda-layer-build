# Builds a zip file from the source_dir or source_file.
# Installs dependencies with poetry/pip automatically.

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import json

from contextlib import contextmanager


@contextmanager
def cd(path):
    """
    Changes the working directory.

    """

    cwd = os.getcwd()
    print('cd', path)
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def cp(src, dst):
    """
    Copys a file from source to dest
    """
    shutil.copy(src, dst)


def format_command(command):
    """
    Formats a command for displaying on screen.

    """

    args = []
    for arg in command:
        if ' ' in arg:
            args.append('"' + arg + '"')
        else:
            args.append(arg)
    return ' '.join(args)


def list_files(top_path):
    """
    Returns a sorted list of all files in a directory.

    """

    results = []

    for root, dirs, files in os.walk(top_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, top_path)
            results.append(relative_path)

    results.sort()
    return results


def run(*args, **kwargs):
    """
    Runs a command.

    """

    print(format(format_command(args)))
    sys.stdout.flush()
    subprocess.check_call(args, **kwargs)


@contextmanager
def tempdir():
    """
    Creates a temporary directory and then deletes it afterwards.

    """

    path = tempfile.mkdtemp(prefix='terraform-aws-lambda-', dir='tmp')
    print(path)
    try:
        yield path
    finally:
        print("not removing")
        # shutil.rmtree(path)


def create_zip_file(source_dir, target_file):
    """
    Creates a zip file from a directory.

    """

    target_file = os.path.abspath(target_file)
    target_dir = os.path.dirname(target_file)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_base, _ = os.path.splitext(target_file)
    shutil.make_archive(
        target_base,
        format='zip',
        root_dir=source_dir,
    )


def dequote(value):
    """
    Handles quotes around values in a shell-compatible fashion.

    """
    return ' '.join(shlex.split(value))


filename = dequote(sys.argv[1])
runtime = dequote(sys.argv[2])
package_manager = dequote(sys.argv[3])
package_lock_file = dequote(sys.argv[4])
yum_packages = json.loads(sys.argv[5])
absolute_filename = os.path.abspath(filename)

# Create a temporary directory for building the archive,
# so no changes will be made to the source directory.
with tempdir() as temp_dir:
    if runtime.startswith('python'):
        if package_manager != 'poetry':
            print("Invalid package_manager: {} for runtime {}".format(package_manager, runtime))
            sys.exit(1)
        if not package_lock_file.endswith('poetry.lock'):
            print("Invalid package_lock_file for package_manager poetry, must use poetry.lock, not {}".format(
                package_lock_file))
            sys.exit(1)
        if not os.path.isfile(package_lock_file):
            print("package_lock_file does not exist: {}".format(package_lock_file))
            sys.exit(1)
        pyproject_file = os.path.join(os.path.dirname(package_lock_file), 'pyproject.toml')
        if not os.path.isfile(pyproject_file):
            print("Could not find pyproject.toml file in same directory as package_lock_file: {}".format(pyproject_file))
        runtime_dir = os.path.join(temp_dir, 'python/lib/{}/site-packages/'.format(runtime))
        print("Creating runtime directory: {}".format(runtime_dir))
        os.makedirs(runtime_dir)
        print("Copying {} to {}".format(package_lock_file, os.path.join(runtime_dir, 'poetry.lock')))
        cp(package_lock_file, runtime_dir)
        print("Copying {} to {}".format(pyproject_file, runtime_dir))
        cp(pyproject_file, runtime_dir)
    if runtime.startswith('node'):
        if package_manager != 'npm' and package_manager != 'yarn':
            print("Invalid package_manager: {} for runtime {}".format(package_manager, runtime))
            sys.exit(1)
        if package_manager == 'npm' and not package_lock_file.endswith('package-lock.json'):
            print("Invalid package_lock_file for package_manager npm, must use package-lock.json, not {}".format(
                package_lock_file))
            sys.exit(1)
        if package_manager == 'yarn' and not package_lock_file.endswith('yarn.lock'):
            print("Invalid package_lock_file for package_manager yarn, must use yarn.lock, not {}".format(
                package_lock_file))
        if not os.path.isfile(package_lock_file):
            print("package_lock_file does not exist: {}".format(package_lock_file))
            sys.exit(1)
        package_json_file = os.path.join(os.path.dirname(package_lock_file), 'package.json')
        if not os.path.isfile(package_json_file):
            print("Could not find package.json file in same directory as package_lock_file: {}".format(package_json_file))
        runtime_dir = os.path.join(temp_dir, 'nodejs')
        print("Creating runtime directory: {}".format(runtime_dir))
        os.makedirs(runtime_dir)
        print("Copying {} to {}".format(package_lock_file, os.path.join(runtime_dir, 'poetry.lock')))
        cp(package_lock_file, runtime_dir)
        print("Copying {} to {}".format(package_json_file, runtime_dir))
        cp(package_json_file, runtime_dir)
    with cd(runtime_dir):
        if package_manager == 'poetry':
            run('poetry export -f requirements.txt -o requirements.txt', shell=True)
            if runtime.startswith('python3'):
                pip_cmd = 'pip3'
            else:
                pip_cmd = 'pip2'
            install_cmd = '{} install --prefix= -r requirements.txt --target .'.format(pip_cmd)
        elif package_manager == 'yarn':
            install_cmd = 'yarn install --production'
        elif package_manager == 'npm':
            install_cmd = 'npm install --production'

        docker_cmd = 'docker run --rm -v "$PWD":/var/task lambci/lambda:build-{}'.format(runtime)
        yum_cmd = ''
        if yum_packages:
            yum_cmd = 'yum install -y {} && '.format(' '.join(yum_packages))
        run('{} {} {}'.format(docker_cmd, yum_cmd, install_cmd), shell=True)

    # Zip up the temporary directory and write it to the target filename.
    # This will be used by the Lambda function as the source code package.
    create_zip_file(temp_dir, absolute_filename)
    print('Created {}'.format(absolute_filename))

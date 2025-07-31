from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_programming.path import DevPathHandler
from yta_temp import Temp
from typing import Union

import subprocess
import sys


PROJECT_ROOT = DevPathHandler.get_project_abspath()
LOCKFILE = f'{PROJECT_ROOT}poetry.lock'
# TODO: Maybe make this a temp (?)
BACKUP_LOCKFILE = f'{PROJECT_ROOT}poetry.lock.testing_backup'

class Dependency:
    """
    Class to wrap functionality related to
    managing dependencies.

    Use if carefully.
    """

    @staticmethod
    def is_installed(
        name: str
    ) -> bool:
        """
        Check if the dependency with the given
        'name' is installed or not.
        """
        return PythonValidator.is_dependency_installed(name)

    @staticmethod
    def install(
        name: str,
        version_range: Union[str, None] = None
    ) -> int:
        """
        Try to install the dependency with the
        given 'name' using pip. It will use the
        'version_range' specificator if provided,
        that must be something like 
        ">=2.0.0,<3.0.0".

        Command used:
        - `pip install -y {name}{version_range}`
        """
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)
        ParameterValidator.validate_string('version_range', version_range, do_accept_empty = False)

        name = (
             f'{name}{version_range}'
             if version_range is not None else
             name
        )

        return subprocess.check_call([sys.executable, '-m', 'pip', 'install', name])

    @staticmethod
    def uninstall(
        name: str
    ) -> int:
        """
        Try to uninstall the dependency with the
        given 'name'.

        Command used:
        - `pip uninstall -y {name}`
        """
        ParameterValidator.validate_mandatory_string('name', name, do_accept_empty = False)

        return subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', name])

    @staticmethod
    def create_backup() -> str:
        """
        Create a backup with the current status of
        the project, containing all the dependencies
        and their versions, to be able to install it
        again, and return the absolute path to the
        backup file that has been written.

        Command used:
        - `pip freeze`
        """
        # TODO: Careful, we have an issue with the 
        # WIP_FOLDER and this is returning an absolute
        # path...
        filename = Temp.get_wip_filename('pip_backup.txt')

        # Using 'pip freeze > {filename}' is not
        # possible as a subprocess
        return FileHandler.write_str(
            filename,
            subprocess.check_output([sys.executable, '-m', 'pip', 'freeze', '>', filename]).decode('utf-8')
        )
    
    @staticmethod
    def restore_backup(
        filename: str
    ) -> int:
        """
        Restore a backup and reinstall all the
        dependencies with the version that was
        written in the backup file with the
        'filename' given.

        Command used:
        - `pip install --force-reinstall -r {filename}`
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        # TODO: This is too slow, I think it is
        # reinstalling all the packages not only
        # the differents...
        return subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '-r', filename])

# TODO: Test this new class, please
# TODO: This has been created to be able
# to install optional dependencies for
# testing and then go back to the previous
# virtual environment to not affect to the
# project, but needs time and work...
class Poetry:
    """
    Class to wrap functionality with poetry
    related to the management of dependencies.

    Use it carefully.
    """

    # TODO: Create general 'get_dependencies' method

    def get_group_dependencies(
        group_name: str
    ):
        """
        Get the dependencies that are set in the
        'pyproject.toml' file inside the group
        with the 'group_name' given.

        You can iterate the result by using the
        '.items()' in a for loop.

        This method will read the section that has
        the next header:

        - `[tool.poetry.group.{group_name}.dependencies]`
        """
        ParameterValidator.validate_mandatory_string('group_name', group_name, do_accept_empty = False)

        # Read '[tool.poetry.group.{group_name}.dependencies]'
        return FileHandler.read_toml('pyproject.toml').get("tool", {}).get("poetry", {}).get("group", {}).get(group_name, []).get("dependencies", [])

    def create_lock_file(
    ) -> int:
        """
        Create a lock file by reading the
        'pyproject.toml' current file.

        Command used:
        - `poetry lock`
        """
        return subprocess.check_call([sys.executable, '-m', 'poetry', 'lock'])

    def create_lock_file_backup(
    ) -> int:
        """
        Create a backup of the current poetry
        lock file to be able to restore it in
        a near future.

        Command used:
        - `poetry install --with testing`
        """
        if not FileHandler.file_exists(LOCKFILE):
            Poetry.create_lock_file()

        FileHandler.copy_file(LOCKFILE, BACKUP_LOCKFILE)

        subprocess.check_call([sys.executable, '-m', 'poetry', 'install', '--with', 'testing'])

    def restore_lockfile_backup(
        filename: str
        # TODO: Return bool (?)
    ) -> bool:
        """
        Restore the environment by using the
        lock file with the given 'filename'.
        It will remove the current virtual
        environment and create a new one from
        the lock file.
        """
        if not FileHandler.file_exists(LOCKFILE):
            raise Exception(f'No "{filename}" lock file found, we cannot restore the backup.')

        FileHandler.copy_file(BACKUP_LOCKFILE, LOCKFILE)
        Poetry.remove_virtual_environment('python')
        Poetry.install_virtual_environment()

        return True

    def install_virtual_environment(
    ) -> int:
        """
        Read the 'poetry.lock' file to install all
        the dependencies specified in the file.

        Command used:
        - `poetry install`
        """
        return subprocess.check_call([sys.executable, '-m', 'poetry', 'install'])

    def remove_virtual_environment(
        environment_name: str
    ) -> int: 
        """
        Remove the virtual envinronment with the
        given 'environment_name'.

        Command used:
        - `poetry env remove {environment_name}`
        """
        ParameterValidator.validate_mandatory_string('environment_name', environment_name, do_accept_empty = False)

        return subprocess.check_call([sys.executable, '-m', 'poetry', 'env', 'remove', environment_name])
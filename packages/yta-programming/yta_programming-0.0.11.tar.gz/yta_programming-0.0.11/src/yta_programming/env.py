from yta_programming.path import DevPathHandler
from yta_validation.parameter import ParameterValidator
from dotenv import load_dotenv
from typing import Union

import os


class Environment:
    """
    Class to handle the environment of the project in
    which you are executing this code perfectly.
    """

    @staticmethod
    def load_current_project_dotenv(
    ):
        """
        Load the current project environment '.env' configuration
        file. The current project is the one in which the code
        is being executed (the code in which you call this method,
        not the library in which it is written).

        Any project in which you are importing this library, the
        '.env' file on its main folder will be loaded.
        """
        load_dotenv(os.path.join(DevPathHandler.get_project_abspath(), '.env'))

    @staticmethod
    def get_current_project_env(
        variable: str,
        default_value: Union[str, bool, float, int, None] = None
    ):
        """
        Load the current project environment '.env' configuration
        file and get the value of the 'variable' if existing.

        This method makes a 'load_dotenv' call within the current
        project absolute path any time you call it, so it ensures
        the value is correctly loaded if available.

        You don't need to do 'load_dotenv()' to call this method,
        it will do for you =).
        """
        ParameterValidator.validate_mandatory_string('variable', variable, do_accept_empty = False)
        
        Environment.load_current_project_dotenv()

        return os.getenv(variable, default_value)

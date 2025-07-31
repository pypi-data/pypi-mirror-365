from yta_file.filename import FilenameHandler
from yta_file.path import PathHandler
from typing import Union

import inspect
import sys
import os


class DevPathHandler:
    """
    Class to encapsulate methods related to paths that are
    related with the python code.

    TODO: Check if we can merge it with the PathHandler in
    'yta_file'.
    """
    
    @staticmethod
    def get_code_abspath(
        code
    ) -> str:
        """
        Returns the abspath of the file in which the code is written.
        The 'code' parameter must be a module, class, method, function,
        traceback, frame or code object to be correctly inspected.
        """
        return FilenameHandler.sanitize(inspect.getfile(code))

    @staticmethod
    def get_code_filename(
        code
    ) -> str:
        """
        Returns the filename in which the code is written. The 'code' 
        parameter must be a module, class, method, function, traceback, 
        frame or code object to be correctly inspected.

        This method will include the filename with the extension.
        """
        return FilenameHandler.get_filename(inspect.getfile(code))

    @staticmethod
    def get_project_abspath(
    ) -> str:
        """
        Returns the absolute path of the current project (the
        one that is being executed and using this library.

        The absolute path returned ends in '/' and has been
        sanitized.
        """
        return f'{FilenameHandler.sanitize(os.getcwd())}/'

    @staticmethod
    def get_current_file_abspath(
        parent_levels: int = 0
    ) -> str:
        """
        Returns the absolute path of the file that is currently
        being executed (in which the code is written). If 
        'parent_levels' provided, it will return the abspath
        to the parent folder that corresponds to the level
        requested.

        The absolute path is returned ending in '/' and has
        been sanitized.
        """
        abspath = FilenameHandler.sanitize(os.path.dirname(os.path.abspath(sys.argv[0])))

        return (
            PathHandler.get_abspath_parent_folder(abspath, parent_levels)
            if parent_levels > 0 else
            f'{abspath}/'
        )
    
    # TODO: This code is not actually about a path but
    # about the python code... Maybe I should create a
    # 'code.py' file (?)
    def get_current_code_function_name(
    ) -> Union[str, None]:
        """
        Get the name of the function in which the code is
        currently being executed. This could be None if
        the code is not inside a function.

        TODO: Check this better, do tests and refactor if
        needed. I don't know what happens when in a class
        but no in a method. Is it possible (?)
        """
        caller_frame = inspect.currentframe()
        # As this is a reusable function, we need to jump
        # to the code that actually called this function
        caller_frame = (
            caller_frame.f_back
            if caller_frame is not None else
            None
        )

        return (
            caller_frame.f_code.co_name
            if caller_frame is not None else
            None
        )
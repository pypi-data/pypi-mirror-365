from typing import Union


def requires_dependency(
    module: str,
    library_name: Union[str, None] = None,
    package_name: Union[str, None] = None
):
    """
    A decorator to include a library/module as optional
    but required to be able to do some functionality.
    Those libraries will not be included as main 
    dependencies in the poetry file, but will appear as
    optional.

    The 'module' is the name with which it is imported
    in the project. The 'library_name' is the name of
    the project in which you are using it (the one the
    'pyproject.toml' file belongs to) and the
    'package_name' is the name you need to use when
    installing (that is set as optional in the .toml
    file).

    You must declare those libraries within the
    'pyproject.toml' file like this:

    `[tool.poetry.group.optional]
    optional = true
    [tool.poetry.group.optional.dependencies]
    faster_whisper = ">=1.0.2,<2.0.0"`

    Example of use:
    - "@requires_dependency('pillow', 'yta_file', 'pillow')"
    """
    def decorator(
        func
    ):
        def wrapper(
            *args,
            **kwargs
        ):
            try:
                __import__(module)
            except ImportError:
                message = f'The function "{func.__name__}" needs the "{module}" installed.'

                message = (
                    f'{message} You can install it with this command: pip install {library_name}[{package_name}]'
                    if package_name else
                    message
                )

                raise ImportError(message)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
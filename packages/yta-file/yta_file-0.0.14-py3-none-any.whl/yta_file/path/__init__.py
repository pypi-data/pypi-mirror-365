"""
TODO: This could be mixed with the 'filename' functionality
as it is similar but we treat it as paths and filenames while
they are the same (a filename is a relative path)
"""
from yta_file.filename import FilenameHandler
from yta_validation.parameter import ParameterValidator
from pathlib import Path

import os


class PathHandler:
    """
    Class to wrap functionality about paths.
    """

    @staticmethod
    def get_abspath_parent_folder(
        abspath: str,
        levels: int = 1
    ) -> str:
        """
        Iterates over the provided 'abspath' and goes to the parent
        folder that is 'levels' levels above. This method will
        return the new abspath sanitized and ended in '/'.
        """
        ParameterValidator.validate_mandatory_string('abspath', abspath, do_accept_empty = False)
        ParameterValidator.validate_mandatory_number('levels', levels)

        # TODO: Handle when 'levels' is greater than possible
        if levels <= 0:
            return abspath

        for _ in range(levels):
            abspath = os.path.dirname(abspath)

        return f'{FilenameHandler.sanitize(abspath)}/'

    @staticmethod
    def create_file_abspath(
        file_abspath: str
    ) -> str:
        """
        This method will create the folders needed to be able to
        create the provided 'file_abspath'. This will create
        all the folders until reaching the file level.

        @param
            **file_abspath**
            File absolute path that we need to be able to work with
            that file. This must include filename and extension.
        """
        ParameterValidator.validate_mandatory_string('file_abspath', file_abspath, do_accept_empty = False)

        if (
            not ':/' in file_abspath or
            file_abspath.endswith('/')
        ):
            raise Exception('No valid absolute path provided.')

        Path(PathHandler.get_abspath_parent_folder(file_abspath)).mkdir(parents = True, exist_ok = True)

        return file_abspath

    @staticmethod
    def is_abspath(
        filename: str
    ) -> bool:
        """
        Checks if the provided 'filename' is an absolute path or not,
        returning True if yes or False if not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        # TODO: Please, improve this with a library or something
        # Check this: https://stackoverflow.com/questions/3320406/how-to-check-if-a-path-is-absolute-path-or-relative-path-in-a-cross-platform-way
        return (
            ':\\' in filename or
            ':/' in filename
        ) 

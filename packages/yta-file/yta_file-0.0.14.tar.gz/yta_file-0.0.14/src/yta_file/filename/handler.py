from yta_file.filename.utils import sanitize_filename
from yta_file.filename.dataclasses import Filename
from yta_constants.file import FileType, FileExtension
from yta_validation.parameter import ParameterValidator


class FilenameHandler:
    """
    Class to encapsulate and simplify the way we handle
    filenames.
    """

    def sanitize(
        filename: str
    ) -> str:
        """
        Check the provided 'filename' and transform any backslash
        character into a normal slash ('/'), returning the new
        string.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return sanitize_filename(filename)
    
    @staticmethod
    def parse(
        filename: str
    ) -> Filename:
        """
        Parse the provided 'filename' and return it as a
        Filename dataclass instance if valid or will raise
        an Exception if invalid.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        try:
            return Filename(filename)
        except:
            raise Exception('The provided "filename" is not a valid filename.')
    
    @staticmethod
    def is_filename(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a string (the path or file name)
        followed by a dot ('.') also followed by a string (the
        extension).

        Values that will be accepted:
        'C://Users/Dani/documents/test.png', 'test.jpg'.

        Values that will not be accepted:
        '.jpg', 'solounstring'
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).is_filename
    
    @staticmethod
    def is_filename_only(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a single string with no dot nor 
        extension.

        Values that will be accepted:
        'solounstring'

        Values that will not be accepted:
        '.jpg', 'C://Users/Dani/documents/test.png', 'test.jpg'
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).is_file_name_only
    
    @staticmethod
    def is_extension_only(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a valid filename,
        which must be a single string with no dot nor 
        extension.

        Values that will be accepted:
        '.jpg'

        Values that will not be accepted:
        'solounstring', 'C://Users/Dani/documents/test.png', 'test.jpg'
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).is_extension_only
    
    @staticmethod
    def get_filename(
        filename: str
    ) -> str:
        """
        Get the full filename (which includes the file name, the
        dot and the extension) but removing the rest of the path
        if existing.

        This method will return, for example, 'file.txt'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).filename
    
    @staticmethod
    def get_original_filename(
        filename: str
    ) -> str:
        """
        Get the file name part only preserving the path if
        existing but removing the dot and the extension.

        This method will return, for example, 
        'C://Users/test/documents/test'
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).original_file_name
    
    @staticmethod
    def get_file_name(
        filename: str
    ) -> str:
        """
        Get the file name part only but removing the path
        if existing, the dot and the extension.

        This method will return, for example, 'test'.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).file_name
    
    @staticmethod
    def get_extension(
        filename: str
    ) -> str:
        """
        Get the extension of the provided 'filename' (if
        existing) without the dot '.'.

        TODO: Is this description above right? Should this
        method return a FileExtension enum instead of str?
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).extension
    
    @staticmethod
    def get_filename_and_extension(
        filename: str
    ) -> tuple[str, str]:
        """
        Get the file name and the extension of the given 'filename'
        which can be an absolute or relative path.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename: Filename = FilenameHandler.parse(filename)

        return (
            filename.file_name,
            filename.extension
        )
        
    @staticmethod
    def is_of_type(
        filename: str,
        type: FileType
    ) -> bool:
        """
        Checks if the provided 'filename' is a valid filename and if 
        its type is the given 'type' or not (based on the extension).
        This method will return True if the 'filename' is valid and
        belongs to the provided 'type', or False if not. It will raise
        a Exception if something is bad formatted or missing.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename: Filename = FilenameHandler.parse(filename)
        type = FileType.to_enum(type)

        return type.is_filename_valid(filename.filename)

    @staticmethod
    def has_extension(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' has an extension or
        not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FilenameHandler.parse(filename).has_extension
    
    @staticmethod
    def has_the_extension(
        filename: str,
        extension: FileExtension 
    ) -> bool:
        """
        Check if the provided 'filename' has the given 
        'extension' or not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename: Filename = FilenameHandler.parse(filename)

        if not filename.has_extension:
            return False
        
        extension = FileExtension.to_enum(extension)

        # TODO: Maybe use the original filename instead?
        return extension.is_filename_valid(filename.filename)
    
    @staticmethod
    def force_extension(
        filename: str,
        extension: str
    ) -> str:
        """
        Force the given 'filename' to have the also provided
        'extension' by detecting the original extension and
        replacing it.

        This method will return the same string if no extension
        detected.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('extension', extension, do_accept_empty = True)

        # TODO: What if extension is very strange?

        return FilenameHandler.parse(filename).original_file_name_with_extension(extension)
    
    @staticmethod
    def get_filename_without_extension(
        filename: str
    ) -> str:
        """
        Get the filename (without the path if existing) without
        the extension.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        
        return FilenameHandler.parse(filename).file_name
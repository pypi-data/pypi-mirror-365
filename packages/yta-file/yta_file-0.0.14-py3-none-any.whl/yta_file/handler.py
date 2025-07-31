from yta_file.filename.utils import sanitize_filename
from yta_constants.file import FileSearchOption, FileEncoding, FileOpenMode, FileType
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union
from pathlib import Path

import shutil
import os
import json
import io
import glob


class FileHandler:
    """
    Magic class to handle operations with files
    and folders: deleting, creating, listing, etc.
    """

    @staticmethod
    def list_items(
        abspath: str,
        option: FileSearchOption = FileSearchOption.FILES_AND_FOLDERS,
        pattern: str = '*',
        do_recursive: bool = False
    ) -> list:
        """
        List what is inside the provided 'abspath'. This method will list files and
        folders, files or only folders attending to the provided 'option'. It will
        also filter the files/folders that fit the provided 'pattern' (you can use
        '*' as wildcard, so for example '*.jpg' will list all images). This method
        can also be used in a recursive way if 'recursive' parameter is True, but
        take care of memory consumption and it would take its time to perform.

        This method returns a list with all existing elements absolute paths 
        sanitized.
        """
        ParameterValidator.validate_mandatory_string('abspath', abspath, do_accept_empty = False)
        
        abspath = sanitize_filename(abspath)
        abspath = (
            f'{abspath}/'
            if not abspath.endswith('/') else
            abspath
        )

        # This below get files and folders
        files_and_folders = [
            sanitize_filename(f)
            for f in glob.glob(pathname = abspath + pattern, recursive = do_recursive)
        ]

        return {
            FileSearchOption.FILES_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileHandler.is_file(f)
            ],
            FileSearchOption.FOLDERS_ONLY: lambda: [
                f
                for f in files_and_folders
                if FileHandler.is_folder(f)
            ],
            FileSearchOption.FILES_AND_FOLDERS: lambda: files_and_folders
        }[option]()

    @staticmethod
    def rename_file(
        origin_filename: str,
        destination_filename: str,
    ):
        """
        Renames the 'origin_filename' to the 'destination_filename'.
        If 'replace_if_existing' is True, it will replace the destination
        file if possible and allowed. If it is False, it will fail.

        TODO: Remove 'replace_if_existing' if not used.
        """
        ParameterValidator.validate_mandatory_string('origin_filename', origin_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('destination_filename', destination_filename, do_accept_empty = False)
        
        # TODO: Implement a parameter to force overwritting
        # the destination file or not.
        
        return shutil.move(origin_filename, destination_filename)

    @staticmethod
    def copy_file(
        origin_filename: str,
        destination_filename: str
    ):
        """
        Makes a copy of the provided 'origin_filename' and 
        stores it as 'destination_filename'.

        The destination folder must exist.
        """
        ParameterValidator.validate_mandatory_string('origin_filename', origin_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_string('destination_filename', destination_filename, do_accept_empty = False)

        return shutil.copyfile(origin_filename, destination_filename)
    
    # Reading and writing operations below
    @staticmethod
    def read_json(
        filename: str
    ) -> dict:
        """
        Reads the provided 'filename' and returns the information 
        as a json (if possible).

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        if (
            not PythonValidator.is_string(filename) or
            not FileHandler.file_exists(filename)
        ):
            raise Exception('The provided "filename" is not a valid string or filename.')
        
        with open(filename, encoding = 'utf-8') as json_file:
            return json.load(json_file)
        
        return FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.READ_ONLY,
            function = lambda file: json.load(file)
        )
        
    @staticmethod
    def read_str_lines(
        filename: str,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8
    ) -> list[str]:
        """
        Read the content of the provided 'filename'
        if valid and return it as it decomposed in
        lines.

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        return FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.READ_ONLY,
            function = lambda file: file.readlines()
        )
        
    @staticmethod
    def read_str(
        filename: str,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8
    ) -> str:
        """
        Read the content of the provided 'filename'
        if valid and return it as it is.

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        return FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.READ_ONLY,
            function = lambda file: file.read()
        )

    @staticmethod
    def read_binary(
        filename: str,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8
    ) -> bytes:
        """
        Read the content of the provided 'filename'
        if valid and return it as it is.

        Parameters
        ----------
        filename : str
            File path from which we want to read the information.
        """
        return FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.READ_ONLY_BINARY,
            function = lambda file: file.read()
        )

    @staticmethod
    @requires_dependency('tomli', 'yta_file', 'tomli')
    def read_toml(
        filename: str
        # TODO: Fix the return, is it a dict (?)
    ) -> any:
        """
        Read the content of the provided 'filename'
        if valid, that must be a toml file, and
        return it as XXXX.

        Parameters
        ----------
        filename : str
            File path from which we want to read
            the information.
        """
        import tomli

        return FileHandler._open_file(
            filename = filename,
            encoding = None,
            mode = FileOpenMode.READ_ONLY_BINARY,
            function = lambda file: tomli.load(file)
        )
    
    @staticmethod
    def write_str(
        filename: str,
        text: str,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8,
    ) -> str:
        """
        Write the provided 'text' in the given 'filename'
        with the also provided 'encoding'.
        This method returns the filename when done.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = True)

        FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.WRITE_ONLY,
            function = lambda file: file.write(text)
        )
    
        return filename
    
    @staticmethod
    def write_json(
        filename: str,
        json_content: dict,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8,
    ) -> str:
        """
        Write the provided 'json_content' in the given 'filename'
        with the also provided 'encoding'.

        This method returns the filename when done.
        """
        ParameterValidator.validate_mandatory_dict('json', json_content)

        FileHandler.write_str(
            filename = filename,
            text = json.dumps(json_content, indent = 4),
            encoding = encoding
        )
    
        return filename
    
    @staticmethod
    def write_binary(
        filename: str,
        binary_data: bytes
    ) -> str:
        """
        Write the provided 'binary_data' in the 'filename'
        file. It replaces the previous content if existing.

        This method returns the filename when done.
        """
        ParameterValidator.validate_mandatory('binary_data', binary_data)

        FileHandler._open_file(
            filename = filename,
            encoding = None,
            mode = FileOpenMode.WRITE_ONLY_BINARY,
            function = lambda file: file.write(binary_data)
        )
    
        return filename
    
    @staticmethod
    def append_str(
        filename: str,
        text: str,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8,
    ) -> str:
        """
        Write or append the provided 'text' in the given
        'filename' with the also provided 'encoding'.

        This method returns the filename when done.
        """
        ParameterValidator.validate_mandatory_string('text', text, do_accept_empty = True)

        FileHandler._open_file(
            filename = filename,
            encoding = encoding,
            mode = FileOpenMode.APPEND_ONLY,
            function = lambda file: file.write(text)
        )
    
        return filename
    
    @staticmethod
    def append_json(
        filename: str,
        json_content: dict,
        encoding: Union[FileEncoding, str, None] = FileEncoding.UTF8,
    ) -> str:
        """
        Write or append the provided 'json_content' in the
        given 'filename' with the also provided 'encoding'.

        This method returns the filename when done.
        """
        ParameterValidator.validate_mandatory_dict('json', json_content)

        FileHandler.append_str(
            filename = filename,
            text = json.dumps(json_content, indent = 4),
            encoding = encoding
        )

        return filename
    
    @staticmethod
    def append_binary(
        filename: str,
        binary_data: bytes
    ) -> str:
        """
        Write or append the provided 'binary_data' in
        the file with the given 'filename' file name.

        This method returns the filename when done.
        """
        # TODO: Maybe create 'validate_mandatory_bytes' that
        # checks that it is bytes and mandatory (?)
        ParameterValidator.validate_mandatory('binary_data', binary_data)

        FileHandler._open_file(
            filename = filename,
            encoding = None,
            mode = FileOpenMode.APPEND_ONLY_BINARY,
            function = lambda file: file.write(binary_data)
        )

        return filename
    
    def _open_file(
        filename: str,
        encoding: Union[FileEncoding, str, None],
        mode: Union[FileOpenMode, str],
        function: callable
    ) -> any:
        """
        *For internal use only*

        Validate the provided parameters, raising exception
        if not valid, and executes the given 'function' on
        the file opened.

        Open a file with context and operate with it. Check
        these options for the 'function 'parameter':
        - lambda file: file.readlines())
        - lambda file: len(f.readlines())
        - lambda file: json.load(file)

        This method returns whatever the 'function' you
        passed is returning.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        encoding = (
            None
            if encoding is None else
            FileEncoding.to_enum(encoding).value
        )

        if (
            mode not in FileOpenMode.get_options_that_create_file()
            and not FileHandler.file_exists(filename)
        ):
            raise Exception('The given "filename" file does not exist and the given mode is not able to create it by itself.')

        mode = FileOpenMode.to_enum(mode).value
        
        with open(
            file = filename,
            mode = mode,
            encoding = encoding
        ) as file:
            return function(file)
        
    @staticmethod
    def write_file_by_chunks_from_response(
        response: 'Response',
        output_filename: str
    ) -> str:
        """
        Iterates over the provided 'response' and writes its content
        chunk by chunk in the also provided 'output_filename'.

        TODO: If you find a better way to handle this you are free to
        create new methods and move them into a new file.

        This method returns the filename that has been
        written.
        """
        ParameterValidator.validate_mandatory_instance_of('response', response, 'Response')
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        CHUNK_SIZE = 32768

        def write_chunks_to_file(f):
            # TODO: Make this method work with a common Iterator parameter
            # and not an specific response, please
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

        FileHandler._open_file(
            filename = output_filename,
            encoding = None,
            mode = FileOpenMode.WRITE_ONLY_BINARY,
            function = write_chunks_to_file
        )

        return output_filename
    # Reading and writing operations above

    @requires_dependency('pillow', 'yta_file', 'pillow')
    @requires_dependency('pydub', 'yta_file', 'pydub')
    @requires_dependency('moviepy', 'yta_file', 'moviepy')
    @staticmethod
    def parse_file_content(
        file_content: Union[bytes, bytearray, io.BytesIO],
        file_type: FileType
    ) -> Union['VideoFileClip', str, 'AudioSegment', 'Image.Image']:
        """
        Parse the provided 'file_content' with the given
        'file_type' and return that content able to be
        handled.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        from moviepy import VideoFileClip
        from pydub import AudioSegment
        from PIL import Image

        ParameterValidator.validate_mandatory_instance_of(file_content, [bytes, bytearray, io.BytesIO])
        
        file_type = FileType.to_enum(file_type)
        
        if PythonValidator.is_instance_of(file_content, [bytes, bytearray]):
            # If bytes, load as a file in memory
            file_content = io.BytesIO(file_content)

        parse_fn = {
            FileType.VIDEO: lambda file_content: VideoFileClip(file_content),
            FileType.SUBTITLE: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileType.TEXT: lambda file_content: file_content.getvalue().decode('utf-8'),
            FileType.AUDIO: lambda file_content: AudioSegment.from_file(file_content),
            FileType.IMAGE: lambda file_content: Image.open(file_content)
        }.get(file_type, None)

        return (
            parse_fn(file_content)
            if parse_fn else
            None
        )

    @requires_dependency('pillow', 'yta_file', 'pillow')
    @requires_dependency('pydub', 'yta_file', 'pydub')
    @requires_dependency('moviepy', 'yta_file', 'moviepy')
    @staticmethod
    def parse_filename(
        filename: str,
    ) -> Union['VideoFileClip', str, 'AudioSegment', 'Image.Image']:
        """
        Identify the provided 'filename' extension and open
        it according to the detected file type.

        This method is capable to detect videos, subtitles,
        audio, text and images.
        """
        from moviepy import VideoFileClip
        from pydub import AudioSegment
        from PIL import Image

        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        reader_fn = {
            FileType.VIDEO: lambda filename: VideoFileClip(filename),
            FileType.SUBTITLE: lambda filename: FileHandler.read_str(filename),
            FileType.TEXT: lambda filename: FileHandler.read_str(filename),
            FileType.AUDIO: lambda filename: AudioSegment.from_file(filename),
            FileType.IMAGE: lambda filename: Image.open(filename)
        }.get(FileType.get_type_from_filename(filename), None)

        return (
            reader_fn(filename)
            if reader_fn else
            None
        )
    
    # Validation methods below
    @staticmethod
    def is_file(
        filename: str
    ) -> bool:
        """
        Checks if the provided 'filename' is an existing and
        valid file. It returns True if yes or False if not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        
        filename = sanitize_filename(filename)
        filename: Path = Path(filename)

        try:
            return (
                filename.exists()
                and filename.is_file()
            )
        except:
            # TODO: Maybe print stack (?)
            return False

    # TODO: Maybe move these 'is_xxx' methods below to
    # a FileValidator instead of FileHandler class (?)
    @staticmethod
    def is_file_of_type(
        filename: str,
        file_type: FileType
    ) -> bool:
        """
        Check if the provided 'filename' is of the also
        provided 'file_type'. This will check the condition
        according to the filename extension, not according
        to the content.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        file_type = FileType.to_enum(file_type)

        return FileType.get_type_from_filename(filename) == file_type

    @staticmethod
    def is_audio_file(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is an audio file
        based on the filename extension.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FileHandler.is_file_of_type(filename, FileType.AUDIO)

    @staticmethod
    def is_image_file(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is an image file
        based on the filename extension.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return FileHandler.is_file_of_type(filename, FileType.IMAGE)

    @staticmethod
    def is_video_file(
        filename: str
    ) -> bool:
        """
        Check if the provided 'filename' is a video file
        based on the filename extension.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        
        return FileHandler.is_file_of_type(filename, FileType.VIDEO)

    @staticmethod
    def is_folder(
        filename: str
    ) -> bool:
        """
        Checks if the provided 'filename' is an existing and
        valid folder. It returns True if yes or False if not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename = sanitize_filename(filename)
        filename: Path = Path(filename)

        try:
            return (
                filename.exists()
                and filename.is_dir()
            )
        except:
            # TODO: Maybe print stack (?)
            return False

    @staticmethod
    def file_exists(
        filename: str
    ) -> bool:
        """
        Checks if the provided 'filename' file or folder exist. It
        returns True if existing or False if not. This method
        sanitizes the provided 'filename' before checking it.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename = sanitize_filename(filename)

        try:
            return Path(filename).exists()
        except:
            # TODO: Maybe print stack (?)
            return False
        
    # Deleting methods below
    @staticmethod
    def delete_file(
        filename: str
    ) -> bool:
        """
        Deletes the provided 'filename' if existing.

        TODO: Maybe can be using other method that generally
        delete files (?) Please, do if possible
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        if not FileHandler.is_file(filename):
            # TODO: Maybe raise an Exception (?)
            return False
        
        try:
            os.remove(filename)
        except:
            return False

        return True

    @staticmethod
    def delete_files(
        foldername: str,
        pattern = '*'
    ) -> bool:
        """
        Delete all the files in the 'folder' provided that match
        the provided 'pattern'. The default pattern removes all
        existing files, so please use this method carefully.
        """
        ParameterValidator.validate_mandatory_string('foldername', foldername, do_accept_empty = False)

        # TODO: Make some risky checkings  about removing '/', '/home', etc.
        files = FileHandler.list_items(foldername, FileSearchOption.FILES_ONLY, pattern)
        # TODO: Check what happens if deleting folders with files inside
        
        try:
            for file in files:
                os.remove(file)
        except:
            return False

        return True

    @staticmethod
    def create_folder(
        filename: str
    ) -> bool:
        """
        Create a folder with the given 'filename'. This method
        returns True when the folder has been removed 
        sucessfully or False when not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        try:
            os.mkdir(filename)
        except:
            # TODO: Maybe give reason or raise exception (?)
            return False
        
        return True

    @staticmethod
    def delete_folder(
        filename: str,
        do_delete_files: bool = False
    ) -> bool:
        """
        Delete the folder with the given 'filename' only if it
        is completely empty. If 'do_delete_files' is False, it
        will be deleted only if there are no files inside. If
        'do_delete_files' is True, it will delete all the files
        inside and then the folder.
         
        This method returns True when the folder has been
        removed successfully or False when not.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        if not FileHandler.is_folder(filename):
            return False
        
        try:
            # TODO: This will remove the folder only if empty,
            # should we adapt the code to be able to force?
            if do_delete_files:
                # TODO: Sorry, this is very dangerous
                #shutil.rmtree(filename)
                pass

            os.rmdir(filename)
        except:
            # TODO: Maybe give reason or raise exception (?)
            return False
        
        return True
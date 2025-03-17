#
# 
#

import json
from pathlib import Path
import subprocess

from megacodist.types import Json


class FFprobeNotFoundError(Exception):
    """Exception raised when ffprobe command is not found."""
    pass


class FFprobeExecutionError(Exception):
    """Exception raised when ffprobe command execution fails."""
    def __init__(self, message, ffmpeg_output=None):
        super().__init__(message)
        self.ffmpeg_output = ffmpeg_output


class EmptyMetadataError(Exception):
    """Exception raised when the metadata JSON object is empty."""
    pass


class FFmetadata:
    """
    A class to extract metadata from multimedia files using FFmpeg.
    """
    def __init__(self, filename: str):
        """
        Initializes the `FFmetadata` object.

        Args:
            filename: The path to the multimedia file.

        ###Exceptions
        * `FileNotFoundError`: If the multimedia file is not found.
        * `FFprobeNotFoundError`: If ffprobe executable is not found.
        * `FFprobeExecutionError`: If ffprobe command execution fails.
        * `json.JSONDecodeError`: If ffprobe output cannot be parsed as JSON.
        * `EmptyMetadataError`: If the parsed JSON metadata is empty.
        """
        self._filename = filename
        """The file name of the multimedia file to retrieve its metadata."""
        self._metadata = self._readMetadata()

    def _readMetadata(self, streams: bool = True) -> Json:
        """Reads metadata of a multimedia file using FFprobe. If `streams`
        is `True`, it retrieves metadata for all streams as well.

        ### Exceptions:
        * `FileNotFoundError`: If the multimedia file is not found.
        * `FFprobeNotFoundError`: If ffprobe executable is not found.
        * `FFprobeExecutionError`: If ffprobe command execution fails.
        * `json.JSONDecodeError`: If ffprobe output cannot be parsed as JSON.
        * `EmptyMetadataError`: If the parsed JSON metadata is empty.
        """
        # Checking if the multimedia file exists...
        if not Path(self._filename).exists():
            raise FileNotFoundError(
                f'Multimedia file not found: {self._filename}')
        # Constructing the command...
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',]
        if streams:
            cmd.append('-show_streams')
        cmd.append(self._filename)
        # Running the command...
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                universal_newlines=True,
                encoding='utf-8',)
            out, err = p.communicate()
        except FileNotFoundError as excp:
            raise FFprobeNotFoundError('ffprobe command not found. Make '
                'sure FFmpeg is installed and ffprobe is in your PATH.'
                ) from excp
        # Handling command execution failure...
        if p.returncode != 0:
            errMsg = f'FFprobe command failed with exit code {p.returncode}.'
            if err:
                errMsg += f'\nFFmpeg output:\n{err}'
            raise FFprobeExecutionError(errMsg, ffmpeg_output=err)
        # Reading the output...
        try:
            metadata: Json = json.loads(out)
        except json.JSONDecodeError as excp:
            # Handling JSON decoding failure...
            errMsg = 'Could not decode FFprobe JSON output. '
            if err: # Include FFmpeg stderr in the error message for debugging
                errMsg += f'FFmpeg output (stderr):\n{err}'
            else:
                errMsg += 'Check FFmpeg output for potential errors.'
            raise json.JSONDecodeError(errMsg, excp.doc, excp.pos) from excp
        # Handling empty JSON object...
        if not metadata:
            raise EmptyMetadataError('FFprobe returned empty JSON metadata. '
                "This might indicate an issue with the file or ffprobe's "
                'ability to read it.')
        #
        return metadata

    @property
    def duration(self) -> float | None:
        """Gets the duration of the multimedia file in seconds, or None
        if not available.
        """
        try:
            return float(self._metadata['format']['duration']) # type: ignore
        except (KeyError, TypeError):
            return None

    @property
    def bitrate(self) -> int | None:
        """Gets the bitrate of the multimedia file in bits per second,
        or None if not available.
        """
        try:
            return int(self._metadata['format']['bit_rate']) # type: ignore
        except (KeyError, TypeError):
            return None
    
    @property
    def nStreams(self) -> int | None:
        """Gets the number of streams in the multimedia file, or None
        if not available.
        """
        try:
            return int(self._metadata['format']['nb_streams']) # type: ignore
        except (KeyError, TypeError):
            return None

    @property
    def formatName(self) -> str | None:
        """Gets the short name of the format of the multimedia file, or
        None if not available.
        """
        try:
            return self._metadata['format']['format_name'] # type: ignore
        except (KeyError, TypeError):
            return None

    @property
    def formatLongName(self) -> str | None:
        """Gets the long name of the format of the multimedia file, or
        None if not available.
        """
        try:
            return self._metadata['format']['format_long_name'] # type: ignore
        except (KeyError, TypeError):
            return None

    @property
    def size(self) -> int | None:
        """Gets the size of the multimedia file in bytes, or None if
        not available.
        """
        try:
            return int(self._metadata['format']['size']) # type: ignore
        except (KeyError, TypeError):
            return None

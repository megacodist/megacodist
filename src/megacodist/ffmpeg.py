#
# 
#

import json
import subprocess


class FFmetadata:
    """
    A class to extract metadata from multimedia files using FFmpeg.
    """
    def __init__(self, filename: str):
        """
        Initializes the `FFmetadata` object.

        Args:
            filename: The path to the multimedia file.
        """
        self._filename = filename
        """The file name of the multimedia file to retrieve its metadata."""
        self._metadata = self._readMetadata()

    def _readMetadata(self, streams: bool = True):
        """
        Reads metadata of a multimedia file using FFprobe. If `streams`
        is `True`, it retrieves metadata for all streams as well.

        ### Exceptions:
        * subprocess.CalledProcessError: If ffprobe command fails.
        * FileNotFoundError: If ffprobe executable is not found.
        * json.JSONDecodeError: If ffprobe output cannot be parsed as JSON.
        """
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
            out, excp = p.communicate()
        except subprocess.CalledProcessError as excp:
            raise excp
        except FileNotFoundError as excp:
            excp.args = ('ffprobe command not found',)
            raise excp
        # Reading the output...
        try:
            return json.loads(out)
        except json.JSONDecodeError as excp:
            excp.args = ('Could not decode FFprobe JSON output. Check FFmpeg output',)
            raise excp

    @property
    def duration(self) -> float | None:
        """Gets the duration of the multimedia file in seconds, or None if not available."""
        try:
            return float(self._metadata['format']['duration'])
        except (KeyError, TypeError):
            return None

    @property
    def bitrate(self) -> int | None:
        """Gets the bitrate of the multimedia file in bits per second, or None if not available."""
        try:
            return int(self._metadata['format']['bit_rate'])
        except (KeyError, TypeError):
            return None
    
    @property
    def nStreams(self) -> int | None:
        """Gets the number of streams in the multimedia file, or None if not available."""
        try:
            return int(self._metadata['format']['nb_streams'])
        except (KeyError, TypeError):
            return None

    @property
    def formatName(self) -> str | None:
        """Gets the short name of the format of the multimedia file, or None if not available."""
        try:
            return self._metadata['format']['format_name']
        except (KeyError, TypeError):
            return None

    @property
    def formatLongName(self) -> str | None:
        """Gets the long name of the format of the multimedia file, or None if not available."""
        try:
            return self._metadata['format']['format_long_name']
        except (KeyError, TypeError):
            return None

    @property
    def size(self) -> int | None:
        """Gets the size of the multimedia file in bytes, or None if not available."""
        try:
            return int(self._metadata['format']['size'])
        except (KeyError, TypeError):
            return None

"""This module exposes some APIs for file system-related tasks.
"""

from os import PathLike, fspath
import subprocess


def CheckDirCaseSen(dir: PathLike) -> bool | None:
    """Checks the case sensitivity of a folder on Windows 10+ NTFS
    file system. It returns False, if the folder is not case sensitive,
    (default in Windows) otherwise True.
    """
    dirPath = fspath(dir)
    args = [
        'fsutil.exe',
        'file',
        'queryCaseSensitiveInfo',
        dirPath]
    popen = subprocess.Popen(
        args,
        universal_newlines=True,
        encoding='utf-8',
        bufsize=1,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    result = popen.stdout.readlines()
    if len(result) > 1:
        return
    result = result[0].strip()
    if not result.startswith('Case sensitive attribute on directory '):
        return
    result = result[38:-1]
    if result.endswith('disabled'):
        return False
    elif result.endswith('enabled'):
        return True
    else:
        return

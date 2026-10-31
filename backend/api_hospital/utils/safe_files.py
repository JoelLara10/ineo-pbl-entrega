"""Constrain clinical and backup files to one trusted directory."""
from pathlib import Path

from werkzeug.security import safe_join


def confined_file(directory, filename):
    """Reject paths and symlinks instead of silently rewriting their names."""
    if (not isinstance(filename, str) or not filename or filename in {'.', '..'}
            or any(char in filename for char in ('/', '\\', ':', '\x00'))):
        raise ValueError('Nombre de archivo inválido')
    joined = safe_join(str(directory), filename)
    if joined is None:
        raise ValueError('Nombre de archivo inválido')
    root = Path(directory).resolve()
    candidate = Path(joined)
    if candidate.is_symlink() or candidate.resolve().parent != root:
        raise ValueError('Nombre de archivo inválido')
    return candidate

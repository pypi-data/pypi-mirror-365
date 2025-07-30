"""Utility functions for reqtracker.

This module provides helper functions for package name resolution
and import-to-package mapping.
"""

import re
import sys


def get_package_name(import_name: str) -> str:
    """Get the package name for a given import name.

    Args:
        import_name: The name used in import statements.

    Returns:
        The corresponding package name for pip installation.
        Returns the import name itself if no mapping is found.

    Examples:
        >>> get_package_name("cv2")
        "opencv-python"
        >>> get_package_name("numpy")
        "numpy"
    """
    from src.reqtracker.mappings import IMPORT_TO_PACKAGE

    # Check if we have a known mapping
    if import_name in IMPORT_TO_PACKAGE:
        return IMPORT_TO_PACKAGE[import_name]

    # No mapping found, return as-is
    return import_name


def is_standard_library(module_name: str) -> bool:
    """Check if a module is part of Python's standard library.

    Args:
        module_name: Name of the module to check.

    Returns:
        True if the module is in the standard library.
    """
    # Check built-in modules first
    top_level = module_name.split(".")[0]
    if top_level in sys.builtin_module_names:
        return True

    # Check for internal C extension modules (start with underscore)
    if top_level.startswith("_"):
        return True

    # Comprehensive list of Python standard library modules
    stdlib_modules = {
        # Built-in modules
        "os",
        "sys",
        "re",
        "json",
        "csv",
        "math",
        "random",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "pathlib",
        "typing",
        "logging",
        "unittest",
        "doctest",
        "argparse",
        "configparser",
        "subprocess",
        "threading",
        "multiprocessing",
        "asyncio",
        "urllib",
        "http",
        "email",
        "html",
        "xml",
        "sqlite3",
        "hashlib",
        "hmac",
        "secrets",
        "uuid",
        "pickle",
        "shelve",
        "tempfile",
        "shutil",
        "glob",
        "fnmatch",
        "linecache",
        "operator",
        "copy",
        "copyreg",
        "enum",
        "types",
        "weakref",
        "contextlib",
        "abc",
        "dataclasses",
        "importlib",
        "ast",
        "inspect",
        "traceback",
        "warnings",
        "io",
        "time",
        "platform",
        "socket",
        "struct",
        "array",
        "queue",
        "heapq",
        "bisect",
        "decimal",
        "fractions",
        "statistics",
        "string",
        "textwrap",
        "unicodedata",
        "codecs",
        "locale",
        "gettext",
        "base64",
        "binascii",
        "zlib",
        "gzip",
        "bz2",
        "lzma",
        "zipfile",
        "tarfile",
        # Additional standard library modules that were missing
        "calendar",
        "mimetypes",
        "encodings",
        "quopri",
        "ipaddress",
        "stringprep",
        "compression",
        "socks",
        "winreg",
        "simplejson",  # This might be third-party, but often bundled
        # Network and encoding modules
        "ssl",
        "ftplib",
        "poplib",
        "imaplib",
        "smtplib",
        "telnetlib",
        "nntplib",
        "mailcap",
        "mailbox",
        "mhlib",
        "rfc822",
        "MimeWriter",
        "mimify",
        "netrc",
        "xdrlib",
        "plistlib",
        # System-specific modules
        "pwd",
        "grp",
        "crypt",
        "spwd",
        "pty",
        "fcntl",
        "pipes",
        "posixfile",
        "resource",
        "nis",
        "syslog",
        "commands",
        "dl",
        "termios",
        "tty",
        "rlcompleter",
        # Windows-specific
        "msvcrt",
        "winsound",
        "_winapi",
        # Development and debugging
        "trace",
        "tabnanny",
        "py_compile",
        "compileall",
        "dis",
        "pickletools",
    }

    return top_level in stdlib_modules


def normalize_package_name(name: str) -> str:
    """Normalize package name according to PEP 503.

    Args:
        name: Package name to normalize.

    Returns:
        Normalized package name.

    Examples:
        >>> normalize_package_name("Django")
        "django"
        >>> normalize_package_name("python-dateutil")
        "python-dateutil"
    """
    # PEP 503 normalization: lowercase and replace underscore/dots with hyphens
    return re.sub(r"[-_.]+", "-", name).lower()

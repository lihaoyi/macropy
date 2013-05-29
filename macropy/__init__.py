
# pep 396 compatible version string [ http://www.python.org/dev/peps/pep-0396 ]
from .version import version as _version
__version__ = ".".join(map(str, _version))

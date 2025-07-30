# flake8: noqa
# Apply compatibility patches first
from .compatibility import patch_basicsr
patch_basicsr()

from .archs import *
from .data import *
from .models import *
from .utils import *
from .version import *

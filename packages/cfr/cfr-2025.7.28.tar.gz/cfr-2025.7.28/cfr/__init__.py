from .climate import ClimateField
from .proxy import ProxyRecord, ProxyDatabase
from .reconjob import ReconJob
from .reconres import ReconRes
from .ts import EnsTS
from .gcm import GCMCase, GCMCases
from . import utils
from . import psm

try:
    from . import ml
except:
    pass

try:
    import graphem
except:
    pass

from .visual import (
    set_style,
    showfig,
    closefig,
    savefig,
)
set_style(style='journal', font_scale=1.2)

# get the version
from importlib.metadata import version
__version__ = version('cfr')


# mute future warnings from pkgs like pandas
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
        
# mute the numpy warnings
warnings.simplefilter('ignore', category=RuntimeWarning)
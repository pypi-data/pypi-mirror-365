'''
 hydrocivil: a package for hydrological methods in civil and enviromental engineering.
 For more information see: https://github.com/lucasglasner/hydrocivil

 Author: Lucas Glasner (lgvivanco96@gmail.com)
 Create Time: 2024-09-DD 16:42:58
 Modified by: Lucas Glasner, 
 Modified time: 2024-10-DD 18:49:12
 Dependencies: numpy, pandas, scipy, matplotlib, rioxarray, rasterio, xarray,
 shapely, geopandas, networkx, whitebox_workflows (optional).
'''


# Core functionality
from . import (
    abstractions,
    channels,
    geomorphology,
    unithydrographs,
    rain,
    watersheds,
    reservoirs
)

# Direct class imports
from .global_vars import _has_whitebox
from .watersheds import RiverBasin, HydroDEM
from .rain import RainStorm
from .reservoirs import Reservoir
from .channels import RiverReach
from .unithydrographs import LumpedUnitHydrograph

# Utilities
from . import (
    misc,
    web
)

# GIS
if _has_whitebox:
    from . import wb_tools
    from .wb_tools import wbe


__version__ = "1.0.9"
__author__ = "Lucas Glasner"
__email__ = "lgvivanco96@gmail.com"
__license__ = "MIT"

from typing import List
__all__: List[str] = [
    'HydroDEM',
    'RiverBasin',
    'LumpedUnitHydrograph',
    'RainStorm',
    'Reservoir',
    'RiverReach',
]

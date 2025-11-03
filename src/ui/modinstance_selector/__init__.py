"""
Copyright (c) Cutleast
"""

from .base_selector_widget import BaseSelectorWidget
from .modorganizer_selector_widget import ModOrganizerSelectorWidget
from .vortex_selector_widget import VortexSelectorWidget
from .limo_selector_widget import LimoSelectorWidget

INSTANCE_WIDGETS: list[type[BaseSelectorWidget]] = [
    VortexSelectorWidget,
    ModOrganizerSelectorWidget,
    LimoSelectorWidget
]
"""
List of available instance widgets.
"""

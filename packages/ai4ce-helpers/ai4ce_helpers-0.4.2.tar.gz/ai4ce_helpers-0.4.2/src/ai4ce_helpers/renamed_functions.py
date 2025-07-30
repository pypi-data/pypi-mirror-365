from .functions import get_mission_orbit
from deprecated import deprecated
import warnings

@deprecated(reason="This function is deprecated. Please use get_mission_orbit() instead.", category=DeprecationWarning)
def get_mission_info(project_id: int) -> dict:
    warnings.warn("This function is deprecated. Please use get_mission_orbit() instead.", DeprecationWarning, stacklevel=2)
    return get_mission_orbit(project_id)
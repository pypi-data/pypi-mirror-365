from .functions import get_mission_orbit
from deprecated import deprecated

@deprecated(reason="This function is deprecated. Please use get_mission_orbit() instead.", category=DeprecationWarning)
def get_mission_info(project_id: int) -> dict:
    return get_mission_orbit(project_id)
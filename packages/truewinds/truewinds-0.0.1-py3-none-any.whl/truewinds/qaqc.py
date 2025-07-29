import numpy as np

class FLAG:
    GOOD: int = 1
    PROBABLY_OK: int = 2
    PROBABLY_BAD: int = 3
    BAD: int = 4
    MISSING_VALUE: int = 9

def flag_course_over_ground(cog):
    flag = np.where((cog < 0) | (cog > 360), FLAG.BAD, FLAG.GOOD)
    return flag

def flag_speed_over_ground(sog, operator_min: float | None = None, operator_max: float | None = None):
    flag = np.full_like(sog, FLAG.GOOD).astype(int)
    if operator_min is not None and operator_max is not None:
        flag = np.where((sog <= operator_min) | (sog >= operator_max), FLAG.PROBABLY_OK, FLAG.GOOD)
    flag = np.where(sog < 0, FLAG.BAD, flag)
    return flag

def flag_true_heading(hdg):
    flag = np.where((hdg < 0) | (hdg > 360), FLAG.BAD, FLAG.GOOD)
    return flag

def flag_relative_wind_direction(rwd):
    flag = np.where((rwd < 0) | (rwd > 360), FLAG.BAD, FLAG.GOOD)
    return flag

def flag_relative_wind_speed(rws, operator_min: float | None = None, operator_max: float | None = None):
    flag = np.full_like(rws, FLAG.GOOD).astype(int)
    if operator_min is not None and operator_max is not None:
        flag = np.where((rws <= operator_min) | (rws >= operator_max), FLAG.PROBABLY_OK, FLAG.GOOD)
    flag = np.where(rws < 0, FLAG.BAD, flag)
    return flag

import numpy as np
from numpy.typing import ArrayLike

from truewinds.core import deg2rad, rad2deg
from truewinds.qaqc import (flag_course_over_ground,
                            flag_speed_over_ground,
                            flag_true_heading,
                            flag_relative_wind_speed,
                            flag_relative_wind_direction)


def true_winds(cog: float | ArrayLike,
               sog: float | ArrayLike,
               hdg: float | ArrayLike,
               rwd: float | ArrayLike,
               rws: float | ArrayLike,
               zlr: float = 0.0,
               return_flags: bool = True,
               verbose: bool = False) -> dict[str, float | int | ArrayLike]:
    """
    Compute true wind direction and true wind speed from a moving reference frame, such as a vessel or mobile platform.

    This function is a vectorized adaptation of the original True Winds Python code written by Mylene Remigio
    and is based on the work of Smith et al. 1999. To use the original code, please use the legacy module.

    :param cog: Course over ground in degrees.
        Most often derived from a NMEA0183 VTG message.
    :param sog: Speed over ground.
        Most often derived from a NMEA0183 VTG message.
        Units for speed over ground much match relative wind speed (rws) units.
    :param hdg: The true heading of the vessel or platform in degrees.
        Most often derived from a NMEA0183 HDG message.
    :param rwd: Relative wind direction in degrees. Derived from an anemometer on the platform.
    :param rws: Relative wind speed in the same units as speed over ground (sog).
        Derived from an anemometer on the platform.
    :param zlr: The clockwise angle between the bow of the platform and the anemometer reference line in degrees.
        Default is 0.0 degrees.
    :param return_flags: If True, flags are returned with the true wind dictionary.
    :return: A dictionary containing true wind direction and true wind speed
    """

    if np.all([isinstance(v, float | int) for v in [cog, sog, hdg, rwd, rws, zlr]]):
        return_singleton = True
    else:
        return_singleton = False

    # Convert to Numpy arrays if the inputs are not already arrays.
    cog = np.asarray(cog)
    sog = np.asarray(sog)
    hdg = np.asarray(hdg)
    rwd = np.asarray(rwd)
    rws = np.asarray(rws)

    # Flag data
    flag_cog = flag_course_over_ground(cog)
    flag_sog = flag_speed_over_ground(sog)
    flag_hdg = flag_true_heading(hdg)
    flag_rwd = flag_relative_wind_direction(rwd)
    flag_rws = flag_relative_wind_speed(rws)

    if verbose is True:
        num_bad_cog = np.sum(flag_cog == 4)
        num_bad_sog = np.sum(flag_sog == 4)
        num_bad_hdg = np.sum(flag_hdg == 4)
        num_bad_rwd = np.sum(flag_rwd == 4)
        num_bad_rws = np.sum(flag_rws == 4)
        bad_zlr = True if (zlr <0) or (zlr > 360) else False
        msg = f"# Bad cog: {num_bad_cog}\n# Bad sog: {num_bad_sog}\n# Bad hdg: {num_bad_hdg}\n# Bad rwd: {num_bad_rwd}\n# Bad rws: {num_bad_rws}\n# Bad zlr: {bad_zlr}"
        print(msg)

    # NaN bad data
    cog = np.where(flag_cog == 4, np.nan, cog)
    sog = np.where(flag_sog == 4, np.nan, sog)
    hdg = np.where(flag_hdg == 4, np.nan, hdg)
    rwd = np.where(flag_rwd == 4, np.nan, rwd)
    rws = np.where(flag_rws == 4, np.nan, rws)

    # Convert course over ground to math coordinates and ensure it is in the range [0, 360].
    mcog = 90 - cog
    mcog = np.where(mcog <= 0, mcog + 360, mcog)

    # Compute apparent wind direction and ensure it is in the range [0, 360].
    awd = hdg + rwd + zlr
    awd = awd % 360

    # Convert apparent wind direction to math coordinates and ensure it is in the range [0, 360].
    mawd = 270 - awd
    mawd = np.where(mawd <= 0, mawd + 360, mawd)
    mawd = np.where(mawd > 360, mawd - 360, mawd)

    # Compute true wind speed.
    x = rws * np.cos(deg2rad(mawd)) + sog * np.cos(deg2rad(mcog))
    y = rws * np.sin(deg2rad(mawd)) + sog * np.sin(deg2rad(mcog))
    tws = np.sqrt(x*x + y*y)

    # Compute true wind direction.
    mtwd = np.where((np.abs(x) > 1e-05), rad2deg(np.arctan2(y, x)), 180 - (90 * y) / np.abs(y))
    mtwd = np.where((np.abs(x) <= 1e-05) & (np.abs(y) <= 1e-05), 270,
                    mtwd)  # If both x, y are near 0, set math direction to 270.
    calm = np.where((np.abs(x) > 1e-05) & (np.abs(y) > 1e-05), 1,
                    0)  # Calm flag of 1 (True) indicates conditions are calm.
    twd = 270 - mtwd
    twd = np.where(twd < 0, np.abs(twd % -360) * calm, twd)
    twd = np.where(twd > 360, (twd % 360) * calm, twd)
    twd = np.where((calm == 1) & (twd < 1e-05), 360, twd)

    tw = {'true_wind_direction': twd,
          'true_wind_speed': tws}

    flags = {'flag_sog': flag_sog,
             'flag_cog': flag_cog,
             'flag_hdg': flag_hdg,
             'flag_rwd': flag_rwd,
             'flag_rws': flag_rws}

    if return_singleton is True:
        tw = {k: float(v) for k, v in tw.items()}
        flags = {k: int(v) for k, v in flags.items()}

    if return_flags is True:
        tw_flags = tw | flags
        return tw_flags
    else:
        return tw

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord

def transform_coordinate(observed_time, desired_time, ra, dec, pm_ra_cosdec, pm_dec):
    original = SkyCoord(ra=ra, dec =dec, pm_ra_cosdec = pm_ra_cosdec, pm_dec = pm_dec, unit = "deg", frame = "icrs", obstime = Time(observed_time))
    transformed = original.apply_space_motion(Time(observed_time))
    print(transformed)

transform_coordinate("2017-12-18 01:12:07.3", "2025-08-04 01:12:07.3", 243.585, 0.7785, -64.3, 5.2)

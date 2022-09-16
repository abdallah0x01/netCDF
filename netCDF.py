from netCDF4 import Dataset
import numpy as np
import os


def getCartizian(filename):
    # angle in degree lists
    radial_azims_degs = []
    radial_elev_degs = []

    # reading netCDF file
    data = Dataset(filename)

    # variables
    site_alt: object = data.variables['siteAlt'][:]  # Altitude of site above mean sea level
    site_lon = data.variables['siteLon'][:]  # Longitude of site
    site_lat = data.variables['siteLat'][:]  # Latitude of site
    radial_azims = data.variables['radialAzim']  # Radial azimuth angle
    radial_elev = data.variables['radialElev']  # Radial elevation angle
    radial_time = data.variables['radialTime']  # Time of radial

    # convert rad to degree
    for rad_angle in radial_azims:
        radial_azims_deg = np.degrees(rad_angle)
        radial_azims_degs.append(radial_azims_deg)

    for rad_angle in radial_elev:
        radial_elev_deg = np.degrees(rad_angle)
        radial_elev_degs.append(radial_elev_deg)

    # calculate r and rho
    r = np.sqrt(site_lon ** 2 + site_lat ** 2 + site_alt ** 2)
    rho = np.sqrt(site_lon ** 2 + site_lat ** 2)

    # convert to cartizan coordinates
    for radial_elev_deg, radial_azims_degs in zip(radial_elev_degs, radial_azims_degs):
        x = np.round(np.real(r * np.sin(radial_elev_deg)
                             * np.cos(radial_azims_degs)), 3)
        y = np.round(np.real(r * np.sin(radial_elev_deg)
                             * np.sin(radial_azims_degs)), 3)
        z = np.round(np.real((r * np.cos(radial_elev_deg))), 3)
        print(f'({x}, {y}, {z})')


for current_dir, dir_names, file_names in os.walk(os.getcwd()):
    for file_name in file_names:
        firstpart, ext = os.path.splitext(file_names)
        ext = ext.strip('.')
        if ext == 'nc':
            getCartizian(file_name)

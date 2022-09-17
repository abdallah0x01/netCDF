from netCDF4 import Dataset
import numpy as np
import os
import time
import csv

def getCSV(x, y, z, t):
    '''this function create csv file with cartizian coorninates'''
    with open('netCDF.csv','a') as file:
        field_names = ['x', 'y', 'z', 't']
        writer = csv.DictWriter(file,fieldnames=field_names)
        writer.writeheader()
        writer.writerow({'x':x,'y':y,'z':z,'t':t})




def getCartizian(filename):
    """This function takes nc file and then converts polar coordinates to cartizian coordiantes and takes epoch time
    then convert it to local time """
    # reading netCDF file
    data = Dataset(filename)

    # variables
    radial_azims_degs = []
    radial_elev_degs = []
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

    # r = np.sqrt(site_lon ** 2 + site_lat ** 2 + site_alt ** 2)
    # rho = np.sqrt(site_lon ** 2 + site_lat ** 2)

    for radial_elev_deg, radial_azims_deg, radial_time_epoch\
    in zip(radial_elev_degs, radial_azims_degs, radial_time):
        # calculate to cartizan coordinates
        x = np.round(np.real(1 * np.sin(radial_elev_deg)
                             * np.cos(radial_azims_deg)), 3)
        y = np.round(np.real(1 * np.sin(radial_elev_deg)
                             * np.sin(radial_azims_deg)), 3)
        z = np.round(np.real((1 * np.cos(radial_elev_deg))), 3) # I think I need to add site_alt on the z value
        # calculate local time
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(radial_time_epoch)))
        getCSV(x, y, z, t)
    print('cvs file created')
        
        # print(f'({x}, {y}, {z}, {t})')


# loop through all nc files in directory where script exist
for current_dir, dir_names, file_names in os.walk(os.getcwd()):
    for file_name in file_names:
        firstpart, ext = os.path.splitext(file_name)
        ext = ext.strip('.')
        if ext == 'nc':
            getCartizian(file_name)
            
            


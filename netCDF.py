from math import radians
from netCDF4 import Dataset
from numpy import round,degrees,sin,cos
import os
import time
import csv
class ConvertCoordinates:
    
    
    def initiatFile(self,firstpart:str):
        '''This function just create empty CSV file format'''
        self.file = open(f'{firstpart}.csv','a')
        writer = csv.writer(self.file)
        writer.writerow(list(range(0,750)))


    def addRecords(self, lis:list):
        '''This function add cartizian coordinates to CSV file'''
        writer = csv.writer(self.file)
        writer.writerow(lis)
        
    def getCartizian(self,filename:str):
        """This function takes nc file and then converts polar coordinates to cartizian coordiantes and convert epoch time to local time """
        
        print(f'Converting {filename} into CSV, please wait a while')
        
        # convert rad to degree
        for rad_angle in self.radial_azims:
            radial_azims_deg = degrees(rad_angle)
            self.radial_azims_degs.append(radial_azims_deg)

        for rad_angle in self.radial_elev:
            radial_elev_deg = degrees(rad_angle)
            self.radial_elev_degs.append(radial_elev_deg)
            ###############################################
            
        for radial_elev_deg, radial_azims_deg, radial_time_epoch\
        in zip(self.radial_elev_degs, self.radial_azims_degs, self.radial_time):
            for pin in self.pins_list:
            # calculate local time
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(radial_time_epoch)))
                # calculate to cartizan coordinates
                x = round((pin * self.pin_width * sin(radial_elev_deg)
                                    * cos(radial_azims_deg) + self.site_lon ).real,3)
                
                y = round((pin * self.pin_width * sin(radial_elev_deg)
                                    * sin(radial_azims_deg)+ self.site_lat).real, 3)  
                
                z = round((pin * self.pin_width * cos(radial_elev_deg) + self.site_alt).real, 3) 
                
                v = round(self.velocity[radians(radial_azims_deg)][pin],3)
                coor = f'p: {pin}, x: {x}, y: {y}, z: {z}, t: {t}, v: {v})'
                self.coor_list.append(coor)
            self.addRecords(self.coor_list)
            self.coor_list.clear()
            
    def __init__(self,file_name:str):
        
        self.data = Dataset(file_name)  # reading netCDF file
        self.pin_width = 10
        self.coor_list = []
        self.coor = ''
        self.file = None
        self.radial_azims_degs = []
        self.radial_elev_degs = []
        self.site_alt = self.data.variables['siteAlt'][:]  # Altitude of site above mean sea level
        self.site_lon = self.data.variables['siteLon'][:]  # Longitude of site
        self.site_lat = self.data.variables['siteLat'][:]  # Latitude of site
        self.radial_azims = self.data.variables['radialAzim']  # Radial azimuth angle
        self.radial_elev = self.data.variables['radialElev']  # Radial elevation angle
        self.radial_time = self.data.variables['radialTime']  # Time of radial
        self.velocity = self.data.variables['V'] 
        self.pins_list = list(range(0,750))
        if not os.path.exists(f'{firstpart}.csv'):
            self.initiatFile(firstpart) # initiating CSV file
        else:
            os.remove(f'{firstpart}.csv')
            self.initiatFile(firstpart) 
        self.getCartizian(file_name) # calculating cartizian coordiantes
            
# loop through all nc files in directory where script exist
for file_name in os.listdir():
    
        firstpart, ext = os.path.splitext(file_name)
        ext = ext.strip('.')
        if ext == 'nc':
            ConvertCoordinates(file_name)
            
print('Done')
            
from concurrent.futures import process
from math import degrees
import time
from netCDF4 import Dataset
import numpy as np
import os
import csv
import multiprocessing as mp

start = time.perf_counter() # count from start
# some global variables
nc_files = []
processes = []

class ConvertCoordinates:
    '''this is the main class'''
    def __init__(self,file_name:str,pin_width:int):
        
        self.data = Dataset(file_name)  # reading netCDF file
        self.coor_list = []
        self.coor = ''
        self.file = None
        self.pin_width = pin_width
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
        self.first_part = file_name.strip('.nc')
        
        if not os.path.exists(f'{self.first_part}.csv'):
            self.initiatFile(self.first_part) # initiating CSV file

        elif os.path.exists(f'{self.first_part}.csv'):
            os.remove(f'{self.first_part}.csv')
            self.initiatFile(self.first_part) 
        self.getCartizian(file_name) # calculating cartizian coordiantes
    
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
        
        for radial_elev, radial_azims, radial_time_epoch\
        in zip(self.radial_elev, self.radial_azims, self.radial_time):
            
            for pin in range(7, 8):
            # calculate local time
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(radial_time_epoch)))
                # calculate to cartizan coordinates
                if  270 >= degrees(radial_azims) >= 90:
                    self.site_lon *=  -1
                    self.site_alt *=  -1
                    

                x = np.round((((pin * self.pin_width * np.sin(radial_elev) 
                                    * np.cos(radial_azims)) + self.site_lon * 1000 ).real) / 1000,3)
                y = np.round(((pin * self.pin_width * np.sin(radial_elev)
                                    * np.sin(radial_azims) + self.site_lat * 1000).real) / 1000, 3)  
                z = np.round(((pin * self.pin_width * np.cos(radial_elev) + self.site_alt * 1000).real) / 1000, 3) 
                v = self.velocity[radial_azims][pin]
                
                if type(v) == np.float32:
                    v = "{:.3f}".format(v)
                else:
                    v = 'NAN'
                    
                coor = f'p: {pin},pin_w: {self.pin_width}, Long: {x}, Lat: {y}, Alt: {z}, t: {t}, V: {v})'
                self.coor_list.append(coor)

            self.addRecords(self.coor_list)
            self.coor_list.clear()

def get_files():
    for file_name in os.listdir():
        firstpart, ext = os.path.splitext(file_name)
        ext = ext.strip('.')
        if ext == 'nc':
            nc_files.append(file_name)
        
    
get_files()

if __name__ == '__main__':
        for file in nc_files:
            pin_width = int(input(f'Enter pin width of file {file} : '))

        for file in nc_files:
            # mulitprocessing for multiple files in same time
            p = mp.Process(target=ConvertCoordinates,args=(file,pin_width))
            processes.append(p)
            p.start()
            
        for p in processes :
                p.join()

        end = time.perf_counter()
        print(f'Finished in in {round(end - start,2)}s')







     
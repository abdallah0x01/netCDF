from math import degrees, radians
import multiprocessing as mp
from netCDF4 import Dataset
import numpy as np
import time
import csv
import os

start = time.perf_counter() # count time from start
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
        self.lat = 0
        self.long = 0
        self.pin_width = pin_width
        self.radial_azims_degs = []
        self.radial_elev_degs = []
        self.site_alt = np.round(self.data.variables['siteAlt'][:], 3)  # Altitude of site above mean sea level
        self.site_lon = np.round(self.data.variables['siteLon'][:], 3)  # Longitude of site
        self.site_lat = np.round(self.data.variables['siteLat'][:], 3)  # Latitude of site
        self.radial_azims = self.data.variables['radialAzim']  # Radial azimuth angle
        self.radial_elev = self.data.variables['radialElev']  # Radial elevation angle
        self.radial_time = self.data.variables['radialTime']  # Time of radial
        self.velocity = self.data.variables['V']  
        self.total_power = self.data.variables['T'] 
        self.spectrum_width = self.data.variables['W'] 
        self.reflectivity = self.data.variables['Z'] 
        self.polarization_diversity = self.data.variables['ZDR'] 

        self.pins_list = list(range(0,750))
        self.first_part = file_name.strip('.nc')
        
        if not os.path.exists(f'{self.first_part}.csv'):
            self.initiatFile(self.first_part) # initiating CSV file

        elif os.path.exists(f'{self.first_part}.csv'):
            os.remove(f'{self.first_part}.csv') # removes csv file if already exists then initiates it again 
            self.initiatFile(self.first_part) 
        self.getCartizian(file_name) # calculating cartizian coordiantes
    
    def initiatFile(self,firstpart:str):
        '''This function just creates empty CSV file format'''
        self.file = open(f'{firstpart}.csv','a')
        writer = csv.writer(self.file)
        writer.writerow(list(range(0,750)))

    def addRecords(self, lis:list):
        '''This function adds cartizian records to CSV file'''
        writer = csv.writer(self.file)
        writer.writerow(lis)


    def checkAzimSign(self, lat, long, azims_degree):
        ''' check the sign of azim angle then return lat and long'''
        if azims_degree <= 360:
                if  90 >= azims_degree >= 0:
                   
                    lat += self.site_lat
                    long += self.site_lon

            
                elif  180 >= azims_degree >= 90:
                    lat *=  -1
                    lat += self.site_lat
                    long += self.site_lon

                elif  270 >= azims_degree >= 180:
                    lat *=  -1
                    lat += self.site_lat
                    long *=  -1
                    long += self.site_lon

                elif  360 >= azims_degree >= 270:
                    lat += self.site_lat
                    long *=  -1
                    long += self.site_lon

                return lat, long

        elif azims_degree > 360:
                return self.checkAzimSign(lat, long, azims_degree - 360)
                    
                
    def formatNum(self,*nums):
        '''this function format all numbers for 3 digits after floating point if the type is float and if it is NAN it make it NAN'''
        rounded_numbers = []
        for num in nums:
            if (type(num) == np.float32) | (type(num) == np.float64):
                 num = "{:.3f}".format(num)
            else:
                num = 'NaN'
            
            rounded_numbers.append(num)
        return rounded_numbers

        
    def getCartizian(self,filename:str):
        """This function takes nc file and then converts polar coordinates to cartizian coordiantes and convert epoch time to local time """
        
        print(f'Converting {filename} into CSV')
        
        for radial_elev, radial_azims, radial_time_epoch\
        in zip(self.radial_elev, self.radial_azims, self.radial_time):
            
            for pin in self.pins_list:
                # calculate local time
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(radial_time_epoch)))
                # calculate to cartizan coordinates
                    
                lat = ((pin * (self.pin_width / 1000) * np.sin(radial_elev) 
                                    * np.cos(radial_azims) ).real / 110.574) # in degree


                long = ((pin * (self.pin_width / 1000) * np.sin(radial_elev)
                                    * np.sin(radial_azims) ).real) / 110.32 * np.cos(radians(lat)) # in degree


                alt = ((pin * (self.pin_width / 1000) * np.cos(radial_elev) + self.site_alt).real)


                v = self.velocity[radial_azims][pin]
                p = self.total_power[radial_azims][pin]
                w = self.spectrum_width[radial_azims][pin]
                z = self.reflectivity[radial_azims][pin]
                zdr = self.polarization_diversity[radial_azims][pin]

       
                rounded_v, rounded_p, rounded_w, rounded_z, rounded_zdr = self.formatNum( v, p, w, z, zdr)
                
                
               
                # check for sign of lat and lon    
                lat, long = self.checkAzimSign(lat, long, degrees(radial_azims)) 
                # round lat, long and alt
                rounded_lat = round(lat, 3)
                rounded_long = round(long, 3)
                rounded_alt = round(alt, 3)
                


                coor = f'p: {pin},pin_w: {self.pin_width}, Lat: {rounded_lat}, Long: {rounded_long}, Alt: {rounded_alt}, t: {t}, V: {rounded_v}, T:{rounded_p}, W:{rounded_w}, Z:{rounded_z}, ZDR:{rounded_zdr})'
                self.coor_list.append(coor)

            self.addRecords(self.coor_list)
            self.coor_list.clear()

def get_files():
    '''gets nc files in directory and append them to nc_files list'''
    for file_name in os.listdir():
        firstpart, ext = os.path.splitext(file_name)
        ext = ext.strip('.')
        if ext == 'nc':
            nc_files.append(file_name)
        
if __name__ == '__main__':
        get_files()
        
        for file in nc_files:
            pin_width = int(input(f'Enter pin width of file {file} : '))
        print('\n')

        for file in nc_files:
            # mulitprocessing for multiple files in same time
            p = mp.Process(target=ConvertCoordinates,args=(file,pin_width))
            processes.append(p)
            p.start()
            
        for p in processes :
                p.join()

        end = time.perf_counter()
        print(f'Finished in in {round(end - start,2)}s')

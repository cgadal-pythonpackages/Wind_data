# @Author: gadal
# @Date:   2018-11-09T14:00:41+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-10-11T14:44:36+02:00

from ecmwfapi import ECMWFDataServer
import os
import numpy as np
from math import atan2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .Wind_treatment import wind_rose, flux_rose, PDF_flux, Wind_to_flux
from itertools import islice

area_ref = [-17.25,11.25]


def format_area(point_coordinates):
    return '{:02.2f}'.format(point_coordinates[0]) + '/' + '{:02.2f}'.format(point_coordinates[1])

def format_time(date):
    return '{:04d}'.format(date[0]) + '-' + '{:02d}'.format(date[1]) + '-' + '{:02d}'.format(date[2])

def file_lenght(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

class Wind_data:
    """ Classe  définissant une donnée de vents. Elle est définie par:
    _ son nom (nom de la zone)
    _ les bornes de la grille (point Nord/Ouest, point Sud/Ouest)
    _ les coordonnées de chaque point de la grille
    _ les données de vents temporelles (U et V)
    _ date de début et date de fin de la forme AAAA/MM/JJ
    """

    def __init__(self, name, grid_bounds, years, grid = 0.75):
        self.name = name
        self.grid_bounds = grid_bounds
        self.years = years
        self.grib_name = None
        self.coordinates = None
        self.grid = grid
        if self.grid_bounds != None:
            self.lat = np.arange(self.grid_bounds[0][0], self.grid_bounds[1][0] - self.grid, -self.grid)
            self.lon = np.arange(self.grid_bounds[0][1], self.grid_bounds[1][1] + self.grid, self.grid)

        ####### numpy arrays [3D arrays, x,y,t]
        self.Uwind = None
        self.Vwind = None
        self.Ustrength = None
        self.Uorientation = None
        self.Qx = None
        self.Qy = None
        self.Qstrength = None
        self.Qorientation = None

    def Getting_wind_data(self, Nsplit, area_wanted  = None, dates = None, quick_option = True):
        if area_wanted is None:
            area_wanted = self.grid_bounds
        if dates is None:
            dates = self.years
        name = self.name
        self.Update_grib_name()

        if quick_option == True :
            area_wanted[0][0] = area_wanted[0][0] - (area_wanted[0][0] - area_ref[0])%(self.grid)
            area_wanted[0][1] = area_wanted[0][1] - (area_wanted[0][1] - area_ref[1])%(self.grid)
            area_wanted[1][0] = area_wanted[1][0] - (area_wanted[1][0] - area_ref[0])%(self.grid)
            area_wanted[1][1] = area_wanted[1][1] - (area_wanted[1][1] - area_ref[1])%(self.grid)


        area = format_area(area_wanted[0]) + '/' + format_area(area_wanted[1])
        print('Area is :' + area)


        Nyear = dates[1][0] - dates[0][0]
        Dyear = round(Nyear/Nsplit)
        year_list = [dates[1][0] if i == (Nsplit) else dates[0][0] + i*Dyear  for i in range(Nsplit + 1)]
        name_file = []

        for i in range(Nsplit):
            d1 = [year_list[i]+1, 1, 1]
            d2 = [year_list[i+1],12,31]
            if i == 0:
                d1[0] = dates[0][0]
                d1[1] = dates[0][1]
                d1[2] = dates[0][2]
            elif i == Nsplit -1 :
                d2[1] = dates[1][1]
                d2[2] = dates[1][2]
            print(str(d1) + ' to ' + str(d2))

            date = format_time(d1) + '/to/' + format_time(d2)
            name_file.append('interim_' + format_time(d1) + 'to' + format_time(d2) + '_'+ name + '.grib')


            server = ECMWFDataServer()
            Dic = {
            #Specify ERA-interim archives. Don't change it
                'dataset'   : "interim",
                'class'     : "ei",
                'stream'    : "oper",
                'expver' : 'l',
            #Specify type of data : an for analysis, fc for forecast for example.
                'type'      : "an",
            #Specify the variables you want: lat (114.202)/ lon (115.202)/10m u wind component(166.128)/ 10m v wind component(167.128).
            #For all parameters see http://apps.ecmwf.int/codes/grib/param-db
                'param'     : "114.202/115.202/165.128/166.128",
                'levtype'   : "sfc",

            #Specify time and space grids
                'step'      : "0",
                'grid'      : str(self.grid) + '/' + str(self.grid),
                'area'      : area, # in N/W/S/E, Un point Nord OUest, un Sud Est, en degrés décimaux
                'time'      : "00/06/12/18", #Hours of the day
                'date'      : date,

            #If you want NetCDF format. Otherise it's grib.
                #'format' : 'netcdf',


                'target'    : name_file[i]
            }
            if quick_option == True:
                Dic['param'] = "165.128/166.128"

            server.retrieve(Dic)

        if Nsplit > 1:
            date = format_time(dates[0]) + '/to/' + format_time(dates[1])
    #
            os.system('cat ' + ''.join([i + ' ' for i in name_file]) + '> ' + self.grib_name)

        if quick_option == True:
            self.grid_bounds = area_wanted
            print('Grid_bounds =' + str(area))
            print('quick option has been used. Please ensure that the area returned by ECMWF correspond to the grid_bounds. Otherwise correct it by modifying self.grid_bounds.')


    def Update_grib_name(self):
        self.grib_name = 'interim_' + format_time(self.years[0]) + 'to' + format_time(self.years[1]) + '_'+ self.name + '.grib'

    def Write_spec(self, name):
        dict = {'name' : self.name, 'area' : self.grid_bounds, 'years' : self.years, 'grid' : self.grid}
        if os.path.isfile(name) == True:
            print(name + ' already exists')
        else:
            with open(name,"w") as f:
                f.write(str(dict))

    def load_spec(self,name):
        with open(name,'r') as inf:
            dict_from_file = eval(inf.read())
        self.name = dict_from_file['name']
        self.grid_bounds = dict_from_file['area']
        self.years = dict_from_file['years']
        self.grid = dict_from_file['grid']
        self.lat = np.arange(self.grid_bounds[0][0], self.grid_bounds[1][0] - self.grid, -self.grid)
        self.lon = np.arange(self.grid_bounds[0][1], self.grid_bounds[1][1] + self.grid, self.grid)


    def Extract_UV(self, path_to_wgrib = None):
        if path_to_wgrib != None:
            os.environ['PATH'] += os.pathsep + path_to_wgrib
        os.system('wgrib -s ' + self.grib_name + ' | grep :10U: | wgrib -i -text ' + self.grib_name + ' -o ' + self.grib_name[:-5] + '_10U.txt')
        os.system('wgrib -s ' + self.grib_name + ' | grep :10V: | wgrib -i -text ' + self.grib_name + ' -o ' + self.grib_name[:-5] + '_10V.txt')

    def load_time_series(self):
        print('Loading wind data from U/V txt files')
        if self.grib_name == None:
            self.Update_grib_name()
        with open(self.grib_name[:-5] + '_10U.txt') as f:
            first_line = f.readline().split(' ')
        Nx = int(first_line[0])
        Ny = int(first_line[1])
        Nt = file_lenght(self.grib_name[:-5] + '_10U.txt')//(Nx*Ny+1)
        self.Uwind = np.zeros((Nx,Ny,Nt))
        self.Vwind = np.zeros((Nx,Ny,Nt))
        with open(self.grib_name[:-5] + '_10U.txt') as fU, open(self.grib_name[:-5] + '_10V.txt') as fV:
            i = 0
            for lineU, lineV in zip(fU, fV):
                t = i//(Nx*Ny +1)
                temp = i%(Nx*Ny + 1)
                if temp != 0:
                    x = (temp - 1)%Nx
                    y = (temp - 1)//Nx
                    self.Uwind[x,y,t] = float(lineU.strip())
                    self.Vwind[x,y,t] = float(lineV.strip())
                i += 1

    def Save_to_bin(self):
        np.save('Uwind.npy', self.Uwind)
        np.save('Vwind.npy', self.Vwind)

    def load_from_bin(self):
        self.Uwind = np.load('Uwind.npy')
        self.Vwind = np.load('Vwind.npy')

    def Write_wind_data(self, dir, pattern = 'wind_data_'):
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
        i = 0
        Npoints = self.Uwind.shape[0]*self.Uwind.shape[1]
        format_string = '{:0' + str(int(np.log10(Npoints)) + 1) + '}'
        for y in range(self.Uwind.shape[1]):
            for x in range(self.Uwind.shape[0]):
                print('x = ' + str(x) +', y = ' + str(y) + ', Point number' + str(i))
                np.savetxt(dir + '/' + pattern + format_string.format(i+1) +'.txt', np.c_[self.Uorientation[x,y,:], self.Ustrength[x,y,:]])
                i = i + 1

    def Cartesian_to_polar(self):
        self.Ustrength = 0*self.Uwind
        self.Uorientation = 0*self.Uwind

        self.Ustrength = np.sqrt(self.Uwind**2 + self.Vwind**2)
        self.Uorientation = (np.arctan2(self.Vwind,self.Uwind) % (2*np.pi) )*180/np.pi

    def Calculate_fluxes(self, grain_size = 180*10**-6):
        self.Qstrength, self.Qorientation = Wind_to_flux(self.Uorientation, self.Ustrength, grain_size)

    def Write_wind_rose(self, dir, ext = '.pdf', **kwargs):
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
        i = 0
        Npoints = self.Uwind.shape[0]*self.Uwind.shape[1]
        format_string = '{:0' + str(int(np.log10(Npoints)) + 1) + '}'
        for y in range(self.Uwind.shape[1]):
            for x in range(self.Uwind.shape[0]):
                print('Point number' + str(i))
                fig = plt.figure()
                wind_rose(self.Uorientation[x,y,:],self.Ustrength[x,y,:], fig = fig, **kwargs)
                plt.savefig(dir + '/wind_rose_'+ format_string.format(i+1) + ext)
                plt.close('all')
                i = i + 1

    def Write_flux_rose(self, dir, ext = '.pdf', **kwargs):
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
        i = 0
        Npoints = self.Uwind.shape[0]*self.Uwind.shape[1]
        format_string = '{:0' + str(int(np.log10(Npoints)) + 1) + '}'
        print('Printing flux roses ...')
        for y in range(self.Uwind.shape[1]):
            for x in range(self.Uwind.shape[0]):
                print('Point number' + str(i))
                pdfQ, Angle  = PDF_flux(self.Qstrength[x,y,:], self.Qorientation[x,y,:])
                fig = plt.figure()
                flux_rose(Angle,pdfQ, fig = fig, **kwargs)
                plt.savefig(dir + '/flux_rose_'+ format_string.format(i+1) + ext)
                plt.close('all')
                i = i + 1


    def Update_coordinates(self):
        self.coordinates = np.zeros((self.lat.size*self.lon.size,2))
        k = 0
        for i in range(self.lat.size):
            for j in range(self.lon.size):
                    self.coordinates[k] = [self.lat[i], self.lon[j]]
                    k = k + 1

    def Write_coordinates(self):
        np.savetxt('Coordinates.txt', self.coordinates, fmt='%+2.4f')

    def Create_KMZ(self):
        loc_path = os.path.join(os.path.dirname(__file__), 'src')
        #### Destination file
        with open(self.name + '.kml','w') as dest :

            ##### Writing the first Part
            with open(os.path.join(loc_path,'En_tete.kml'),'r') as entete :
                name = self.name
                for line in islice(entete, 10, None):
                    if line == '	<name>Skeleton_Coast.kmz</name>'+'\n': ###Premiere occurence
                        line = ' 	<name>'+name+'.kmz</name>'+'\n'
                    elif line == '		<name>Skeleton_Coast</name>'+'\n': #### Second occurence
                        line = ' 	<name>'+name+'</name>'+'\n'

                    dest.write(line)

            ##### Writing placemarks
            with open(os.path.join(loc_path,'placemark.kml'),'r') as placemark, open('Coordinates.txt','r') as Coordinates :
                i = 0
                for Coord in Coordinates:
                    i += 1
                    print(i)
                    lat = Coord[:8]
                    lon = Coord[9:]
                    print('lon =',lon)
                    print('lat=',lat)

                    for line in islice(placemark, 7, None):
                        if line == '			<name>1</name>'+'\n':
                            line = '			<name>'+str(i)+'</name>'+'\n'
                        if line == '				<coordinates>11.25,-17.25,0</coordinates>'+'\n':
                            line = '				<coordinates>'+lon+','+lat+',0</coordinates>'+'\n'
                        dest.write(line)
                    placemark.seek(0,0)

            ##### Wrtiting closure
            with open(os.path.join(loc_path,'bottom_page.kml'),'r') as bottom :
                dest.writelines(bottom.readlines()[7:])

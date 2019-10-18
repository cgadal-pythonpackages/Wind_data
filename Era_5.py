# @Author: gadal
# @Date:   2019-05-21T18:44:14+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-10-18T11:16:10+02:00

# @Author: gadal
# @Date:   2018-11-09T14:00:41+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-10-18T11:16:10+02:00

import cdsapi
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .Wind_treatment import wind_rose, flux_rose, PDF_flux, Wind_to_flux
from itertools import islice
from decimal import Decimal
# from . import Wind_treatment

area_ref = [-17.25,11.25]

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

    def __init__(self, name):
        self.name = name
        self.grid_bounds = None
        self.years = None
        self.grib_name = None
        self.coordinates = None
        self.grid = None

        ####### numpy arrays [3D arrays, x,y,t]
        self.Uwind = None
        self.Vwind = None
        self.Ustrength = None
        self.Uorientation = None
        self.Qx = None
        self.Qy = None
        self.Qstrength = None
        self.Qorientation = None


    def Getting_wind_data(self,  variable_dic, Nsplit = 1):
        if Nsplit < 1:
            Nsplit = 1

        Nitems = len(variable_dic['variable']) * (365.25 * len(variable_dic['month'])/12 * len(variable_dic['day'])/31) \
        * len(variable_dic['time']) * len(variable_dic['year'])
        if Nitems/Nsplit > 120000:
            Nsplit = round(Nitems/120000) + 1
            print('Request too large. Setting Nsplit =', Nsplit)

        if self.grid is None:
            if 'grid' in variable_dic.keys():
                self.grid = variable_dic['grid'][0]
            else:
                self.grid = 0.25
        # Defining years for data, either from dic variable
        dates = np.array([int(i) for i in variable_dic['year']])
        self.years = [[dates.min(),1,1], [dates.max(),12,31]]

        ### Puting the required area on the ERA5 grid
        area_wanted = variable_dic['area']
        area_wanted[0] = area_wanted[0] - float(Decimal(str(area_wanted[0] - area_ref[0]))%Decimal(str(self.grid)))
        area_wanted[1] = area_wanted[1] - float(Decimal(str(area_wanted[1] - area_ref[1]))%Decimal(str(self.grid)))
        area_wanted[2] = area_wanted[2] - float(Decimal(str(area_wanted[2] - area_ref[0]))%Decimal(str(self.grid)))
        area_wanted[3] = area_wanted[3] - float(Decimal(str(area_wanted[3] - area_ref[1]))%Decimal(str(self.grid)))

        ## updating dic and class obj
        variable_dic['area'] = area_wanted
        self.grid_bounds = area_wanted
        self.lat = np.linspace(self.grid_bounds[0], self.grid_bounds[2], abs(self.grid_bounds[0] - self.grid_bounds[2])/self.grid + 1)
        self.lon = np.linspace(self.grid_bounds[1], self.grid_bounds[3], abs(self.grid_bounds[1] - self.grid_bounds[3])/self.grid + 1)
        print('Area is :', area_wanted)
        # print('Please ensure that the area returned by ECMWF correspond to this Area. Otherwise correct it by modifying self.area afterwards.')

        self.Update_grib_name()

        # Spliting request
        dates = np.array([int(i) for i in variable_dic['year']])
        year_list = [list(map(str,j)) for j in np.array_split(dates, Nsplit)]
        ##### checking the Nitems for every Nsplit
        Nitems_list = np.array([len(variable_dic['variable']) * (365.25 * len(variable_dic['month'])/12 * len(variable_dic['day'])/31)*len(variable_dic['time']) * len(i)
                        for i in year_list])
        if (Nitems_list > 120000).any():
            Nsplit = Nsplit + 1
            year_list = [list(map(str,j)) for j in np.array_split(dates, Nsplit)]

        name_file = []

        for years in year_list :
            string = years[0] + 'to' + years[-1]
            print(string)
            name_file.append('interim_' + string + '_' + self.name + '.grib')
            c = cdsapi.Client()

            variable_dic['year'] = years
            c.retrieve('reanalysis-era5-single-levels', variable_dic, name_file[-1])

        if Nsplit > 1:
            os.system('cat ' + ''.join([i + ' ' for i in name_file]) + '> ' + self.grib_name)

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
        self.lat = np.linspace(self.grid_bounds[0], self.grid_bounds[2], abs(self.grid_bounds[0] - self.grid_bounds[2])/self.grid + 1)
        self.lon = np.linspace(self.grid_bounds[1], self.grid_bounds[3], abs(self.grid_bounds[1] - self.grid_bounds[3])/self.grid + 1)

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
                np.savetxt(dir + '/' + pattern + format_string.format(i+1) +'.txt', np.c_[self.Uorientation[x,y,:], self.Ustrength[x,y,:]], fmt ='%1.5e')
                i = i + 1

    def Cartesian_to_polar(self):
        self.Ustrength = 0*self.Uwind
        self.Uorientation = 0*self.Uwind

        self.Ustrength = np.sqrt(self.Uwind**2 + self.Vwind**2)
        # self.Uorientation = (np.arctan2(self.Vwind, self.Uwind) % (2*np.pi))*180/np.pi
        self.Uorientation = (np.arctan2(self.Vwind, self.Uwind)*180/np.pi) % 360 #no need to decimal here, because used only to change sign

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
                plt.ioff()
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
                pdfQ, Angle  = PDF_flux(self.Qorientation[x,y,:],self.Qstrength[x,y,:])
                fig = plt.figure()
                flux_rose(Angle,pdfQ, fig = fig, **kwargs)
                plt.savefig(dir + '/flux_rose_'+ format_string.format(i+1) + ext)
                plt.close('all')
                i = i + 1


    def Update_coordinates(self):
        self.coordinates = np.zeros((self.lat.size*self.lon.size, 2))
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
            with open(os.path.join(loc_path,'En_tete_era5.kml'),'r') as entete :
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

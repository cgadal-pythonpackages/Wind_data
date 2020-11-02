# @Author: gadal
# @Date:   2019-05-21T18:44:14+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2020-11-02T17:55:37+01:00

import cdsapi
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .Wind_treatment import wind_rose, flux_rose, PDF_flux, Wind_to_flux
from itertools import islice
from decimal import Decimal
from scipy.io import netcdf
from datetime import datetime, timezone, timedelta

area_ref = [0, 0]
Names = {'reanalysis-era5-single-levels': 'ERA5', 'reanalysis-era5-land': 'ERA5Land'}
atmos_epoch = datetime(1900, 1, 1, 0, 0, tzinfo=timezone.utc)

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

    def __init__(self, name, type = 'reanalysis-era5-single-levels'):
        self.name = name
        self.type = type  # should be either reanalysis-era5-single-levels or 'reanalysis-era5-land' for now
        self.grid_bounds = None
        self.years = None
        self.file_names = None
        self.coordinates = None
        self.grid = None
        self.time = None

        ####### numpy arrays [3D arrays, x,y,t]
        self.Uwind = None
        self.Vwind = None
        self.Ustrength = None
        self.Uorientation = None
        self.Qx = None
        self.Qy = None
        self.Qstrength = None
        self.Qorientation = None

    def Getting_wind_data(self, variable_dic, Nsplit = 1, file = 'info.txt', save_to_npy = True, remove_netcdf = True):
        Nitems_max = 120000 if self.type == 'reanalysis-era5-single-levels' else 100000
        if Nsplit < 1:
            Nsplit = 1
        Nitems = len(variable_dic['variable']) * (365.25 * len(variable_dic['month'])/12 * len(variable_dic['day'])/31) \
        * len(variable_dic['time']) * len(variable_dic['year'])
        if Nitems/Nsplit > Nitems_max:
            Nsplit = round(Nitems/Nitems_max) + 1
            print('Request too large. Setting Nsplit =', Nsplit)

        if self.grid is None:
            if 'grid' in variable_dic.keys():
                self.grid = variable_dic['grid'][0]
            elif self.type == 'reanalysis-era5-land':
                self.grid = 0.1
            else:
                self.grid = 0.25
        # Defining years for data, either from dic variable
        dates = np.array([int(i) for i in variable_dic['year']])
        self.years = [[dates.min(),1,1], [dates.max(),12,31]]
        #
        ### Puting the required area on the ERA5 grid
        area_wanted = variable_dic['area']
        area_wanted[0] = area_wanted[0] - float(Decimal(str(area_wanted[0] - area_ref[0]))%Decimal(str(self.grid)))
        area_wanted[1] = area_wanted[1] - float(Decimal(str(area_wanted[1] - area_ref[1]))%Decimal(str(self.grid)))
        area_wanted[2] = area_wanted[2] - float(Decimal(str(area_wanted[2] - area_ref[0]))%Decimal(str(self.grid)))
        area_wanted[3] = area_wanted[3] - float(Decimal(str(area_wanted[3] - area_ref[1]))%Decimal(str(self.grid)))
        #
        ## updating dic and class obj
        variable_dic['area'] = area_wanted
        self.grid_bounds = area_wanted
        # self.latitude = np.linspace(self.grid_bounds[0], self.grid_bounds[2], int(round(abs(self.grid_bounds[0] - self.grid_bounds[2])/self.grid + 1, 2)))
        # self.longitude = np.linspace(self.grid_bounds[1], self.grid_bounds[3], int(round(abs(self.grid_bounds[1] - self.grid_bounds[3])/self.grid + 1, 2)))
        print('Area is :', area_wanted)
        #
        # Spliting request
        dates = np.array([int(i) for i in variable_dic['year']])
        year_list = [list(map(str,j)) for j in np.array_split(dates, Nsplit)]
        ##### checking the Nitems for every Nsplit
        Nitems_list = np.array([len(variable_dic['variable']) * (365.25 * len(variable_dic['month'])/12 * len(variable_dic['day'])/31)*len(variable_dic['time']) * len(i)
                        for i in year_list])
        if (Nitems_list > 120000).any():
            Nsplit = Nsplit + 1
            year_list = [list(map(str,j)) for j in np.array_split(dates, Nsplit)]
        #
        ####### Launching requests by year bins
        self.file_names = []
        for years in year_list :
            string = years[0] + 'to' + years[-1]
            print(string)
            self.file_names.append(Names[self.type] + string + '_' + self.name + '.netcdf')
            c = cdsapi.Client()
            variable_dic['year'] = years
            c.retrieve(self.type, variable_dic, self.file_names[-1])
        #
        ##
        self.Load_netcdf(self.file_names, save_to_npy = save_to_npy)
        if save_to_npy and remove_netcdf:
            for file in self.file_names:
                os.rmdir(file)
        elif remove_netcdf and not save_to_npy:
            print('remove_netcdf is TRUE but save_to_npy is FALSE so data would be lost. Erasing canceled, netcdf files preserved.')
        #
        #### Writing informations to spec file
        self.Save_spec_to_txt(file)

    def Load_netcdf(self, name_files, save_to_npy = False):
        self.Uwind = []
        self.Vwind = []
        self.time = []
        self.file_names = name_files
        for i, file in enumerate(name_files):
            file_temp = netcdf.NetCDFFile(file, 'r')
            self.Uwind.append(np.moveaxis(file_temp.variables['u10'][:], 0, -1))
            self.Vwind.append(np.moveaxis(file_temp.variables['u10'][:], 0, -1))
            self.time.append(file_temp.variables['time'][:])
            if i == 0:
                self.latitude = file_temp.variables['latitude'][:]
                self.longitude = file_temp.variables['longitude'][:]

        self.Uwind, self.Vwind, self.time = np.concatenate(self.Uwind, axis = -1), np.concatenate(self.Uwind, axis = -1), np.concatenate(self.time, axis = -1)
        self.Save_basic()

    def Save_spec_to_txt(self, name):
        Pars_to_save = ['name', 'type', 'years', 'latitude', 'longitude', 'file_names']
        sub_dir = { i: getattr(self, i) for i in list_par_to_save}
        if os.path.isfile(name):
            print(name + ' already exists')
        else:
            with open(name,"w") as f:
                f.write(str(dict))

    def load_spec(self, name):
        with open(name,'r') as inf:
            dict_from_file = eval(inf.read())
        for key in dict_from_file.keys():
            setattr(self, key, temp[key])
            temp[key] = None
        if 'type' not in dict_from_file.keys():
            self.type = 'reanalysis-era5-single-levels'
        else:
            self.type = 'reanalysis-era5-land'

    def Extract_points(points, file_format = 'npy', system_coordinates = 'cartesian'):
        ######## function to extract specific points and write (u, v) velocity to <format> files
        # points can either be a list of integers (1 is top left of the grid), or a list of coordinates (lat, lon)
        # file_format is 'npy' or 'txt'
        # system_coordinates is cartesian or polar
        points = np.array(points)
        if system_coordinates == 'polar':
            self.Cartesian_to_polar()
        for i, coords in points:
            ## if for referencing point system
            if ((len(points.shape) == 2) & (points.shape[-1] == 2)):
                lat_ind = np.argwhere(coords[0] == self.latitude)[0][0]
                lon_ind = np.argwhere(coords[1] == self.longitude)[0][0]
                indexes = sub2ind(self.Uwind[:-1], lat_ind, lon_ind)
            else:
                lat_ind, lon_ind = ind2sub(self.Uwind[:-1], coords)
                indexes = coords
            #
            # if for data coordinate system
            if system_coordinates == 'cartesian':
                data_to_write = [self.Uwind[lat_ind, lon_ind, :], self.Vwind[lat_ind, lon_ind, :]]
            elif system_coordinates == 'polar':
                data_to_write = [self.Ustrength[lat_ind, lon_ind, :], self.Uorientation[lat_ind, lon_ind, :]]
            #
            # if for saved file format
            if file_format == 'npy':
                np.save('Point_' + str(indexes) + '.npy', )
            else:
                np.savetxt('Point_' + str(indexes) + '.txt', [self.Uwind[lat_ind, lon_ind, :], self.Vwind[lat_ind, lon_ind, :]])

    def Cartesian_to_polar(self):
        self.Ustrength = 0*self.Uwind
        self.Uorientation = 0*self.Uwind

        self.Ustrength = np.sqrt(self.Uwind**2 + self.Vwind**2)
        # self.Uorientation = (np.arctan2(self.Vwind, self.Uwind) % (2*np.pi))*180/np.pi
        self.Uorientation = (np.arctan2(self.Vwind, self.Uwind)*180/np.pi) % 360 #no need to decimal here, because used only to change sign

########################### Small functions
    def Save_basic(self):
        Pars_to_save = ['Uwind', 'Vwind', 'time', 'longitude', 'latitude']
        self.Save_Data(Pars_to_save, 'Data.npy')

    def Save_Data(self, Pars_to_save, name):
        sub_dir = { i: getattr(self, i) for i in Pars_to_save}
        np.save(name, sub_dir)

    def Load_Data(self, dic):
        temp = np.load(dic, allow_pickle = True).item()
        for key in temp.keys():
            setattr(self, key, temp[key])
            temp[key] = None

    def Load_Basic(self):
        dic = 'Data.npy'
        self.Load_Data(dic)
        
########################### Google earth functions
    def Update_coordinates(self):
        LAT, LON = np.meshgrid(self.latitude, self.longitude)
        coordinates = np.array([LAT, LON]).T
        self.coordinates = np.reshape(coordinates, (3*10, 2))

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

########################################## Fluxes calculation
    def Calculate_fluxes(self, grain_size = 180*10**-6, **kwargs):
        self.Qstrength, self.Qorientation = Wind_to_flux(self.Uorientation, self.Ustrength, grain_size, **kwargs)

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


############ Not in class function
def Convert_time(Times):
    # convert array of times in hours from epoch to dates
    return np.array([atmos_epoch + timedelta(hours = i) for i in Times])

def sub2ind(array_shape, rows, cols):
    return rows*array_shape[1] + cols

def ind2sub(array_shape, ind):
    rows = (ind.astype('int') / array_shape[1])
    cols = (ind.astype('int') % array_shape[1]) # or numpy.mod(ind.astype('int'), array_shape[1])
    return (rows, cols)

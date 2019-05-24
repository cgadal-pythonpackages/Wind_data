# @Author: gadal
# @Date:   2019-05-21T18:44:14+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-05-24T14:20:31+02:00

# @Author: gadal
# @Date:   2018-11-09T14:00:41+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-05-24T14:20:31+02:00

import cdsapi
import os
import numpy as np
import matplotlib.pyplot as plt
from .Wind_treatment import wind_rose, flux_rose, PDF_flux
# from . import Wind_treatment

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

    def __init__(self):
        self.name = 'Skeleton_Coast'
        self.grid_bounds = None
        self.years = None
        self.grib_name = None
        self.coordinates = None

        ####### numpy arrays [3D arrays, x,y,t]
        self.Uwind = None
        self.Vwind = None
        self.Ustrength = None
        self.Uorientation = None


    def Getting_wind_data(self,  variable_dic, Nsplit = 1):
        if Nsplit < 1:
            Nsplit = 1

        Nitems = len(variable_dic['variable']) * (365.25 * len(variable_dic['month'])/12 * len(variable_dic['day'])/31) \
                * len(variable_dic['hour']) * len(variable_dic['year'])
        if Nfields/Nsplit > 120000:
            print('Request too large. Setting Nsplit =', Nitems/120000)
            Nsplit = Nitems/120000

        # Defining years for data, either from dic variable
        dates = np.array([int(i) for i in variable_dic['year']])
        self.years = [[dates.min(),1,1], [dates.max(),12,31]]

        ### Puting the required area on the ERA5 grid
        area_wanted = variable_dic['area']
        area_wanted[0] = area_wanted[0] - (area_wanted[0] - area_ref[0])%(0.25)
        area_wanted[1] = area_wanted[1] - (area_wanted[1] - area_ref[1])%(0.25)
        area_wanted[2] = area_wanted[2] - (area_wanted[2] - area_ref[0])%(0.25)
        area_wanted[3] = area_wanted[3] - (area_wanted[3] - area_ref[1])%(0.25)

        ## updating dic and class obj
        variable_dic['area'] = area_wanted
        self.grid_bounds = area_wanted
        # area = format_area(area_wanted[0]) + '/' + format_area(area_wanted[1])
        print('Area is :', area_wanted)
        # print('Grid_bounds =' + str(area))
        print('Please ensure that the area returned by ECMWF correspond to this Area. Otherwise correct it by modifying self.area afterwards.')

        self.Update_grib_name()

        # Spliting request
        dates = np.array([int(i) for i in variable_dic['year']])
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

    def Save_to_bin(self):
        np.save('Uwind.npy', self.Uwind)
        np.save('Vwind.npy', self.Vwind)

    def load_from_bin(self):
        self.Uwind = np.load('Uwind.npy')
        self.Vwind = np.load('Vwind.npy')

    def Cartesian_to_polar(self):
        self.Ustrength = 0*self.Uwind
        self.Uorientation = 0*self.Uwind

        self.Ustrength = np.sqrt(self.Uwind**2 + self.Vwind**2)
        self.Uorientation = (np.arctan2(self.Vwind,self.Uwind) % (2*np.pi) )*180/np.pi
        # for x in range(self.Uwind.shape[0]):
        #     for y in range(self.Uwind.shape[1]):
        #         for t in range(self.Uwind.shape[2]):
        #             u = self.Uwind[x,y,t]
        #             v = self.Vwind[x,y,t]
        #
        #             self.Ustrength[x,y,t] = np.sqrt(u**2 + v**2)
        #             self.Uorientation[x,y,t] = (atan2(v,u) % (2*np.pi) )*180/np.pi


    def Update_coordinates(self):
        lat = np.arange(self.grid_bounds[0], self.grid_bounds[2] - 0.25, -0.25)
        lon = np.arange(self.grid_bounds[1], self.grid_bounds[3] + 0.25, 0.25)
        self.coordinates = np.zeros((lat.size*lon.size,2))
        k = 0
        for i in range(lat.size):
            for j in range(lon.size):
                    self.coordinates[k] = [lat[i], lon[j]]
                    k = k + 1

    def Write_coordinates(self):
        np.savetxt('Coordinates.txt', self.coordinates, fmt='%2.4f')

    def Create_KMZ(self):
        loc_path = os.path.join(os.path.dirname(__file__), 'src')
        #### Destination file
        with open(self.name + '.kml','w') as dest :

            ##### Writing the first Part
            with open(os.path.join(loc_path,'En_tete_era5.kml'),'r') as entete :
                name = self.name
                for line in entete[6:]:
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
                    lat = Coord[:6]
                    lon = Coord[7:]
                    print('lon =',lon)
                    print('lat=',lat)

                    for line in placemark[6:]:
                        if line == '			<name>1</name>'+'\n':
                            line = '			<name>'+str(i)+'</name>'+'\n'
                        if line == '				<coordinates>11.25,-17.25,0</coordinates>'+'\n':
                            line = '				<coordinates>'+lon+','+lat+',0</coordinates>'+'\n'
                        dest.write(line)
                    placemark.seek(0,0)

            ##### Wrtiting closure
            with open(os.path.join(loc_path,'bottom_page.kml'),'r') as bottom :
                dest.write(bottom.read()[6:])


    def Extract_UV(self, path_to_wgrib = None):
        if path_to_wgrib != None:
            os.environ['PATH'] += os.pathsep + path_to_wgrib
        os.system('wgrib -s ' + self.grib_name + ' | grep :10U: | wgrib -i -text ' + self.grib_name + ' -o ' + self.grib_name[:-5] + '_10U.txt')
        os.system('wgrib -s ' + self.grib_name + ' | grep :10V: | wgrib -i -text ' + self.grib_name + ' -o ' + self.grib_name[:-5] + '_10V.txt')

    def load_wind_data(self):
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

    def Write_flux_rose(self, dir, ext = '.pdf', grain_size = 180*10**-6, **kwargs):
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
        i = 0
        Npoints = self.Uwind.shape[0]*self.Uwind.shape[1]
        format_string = '{:0' + str(int(np.log10(Npoints)) + 1) + '}'
        print('Printing flux roses ...')
        for y in range(self.Uwind.shape[1]):
            for x in range(self.Uwind.shape[0]):
                print('Point number' + str(i))
                pdfQ, Angle, _  = PDF_flux(np.c_[self.Uorientation[x,y,:],self.Ustrength[x,y,:]], grain_size)
                fig = plt.figure()
                flux_rose(Angle[:-1], pdfQ, fig = fig, **kwargs)
                plt.savefig(dir + '/flux_rose_'+ format_string.format(i+1) + ext)
                plt.close('all')
                i = i + 1

    def Write_spec(self, name):
        dict = {'name' : self.name, 'area' : self.grid_bounds, 'years' : self.years}
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

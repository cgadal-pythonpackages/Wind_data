# @Author: gadal
# @Date:   2019-05-22T13:35:05+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-09-17T11:23:40+02:00

import sys
sys.path.append('../')
import Wind_data.Era_5 as Era5
import numpy as np

########### CReating wind data object
Namibia = Era5.Wind_data()
Namibia.name = 'Namibia'

########## Defining request (optional in theory but ..)
#Nsplit = 8  # Spliting request into Nsplit part. Automatically set by the function that send the requests (in theory).

### Specifying request
variables = ['10m_u_component_of_wind','10m_v_component_of_wind']  ## variables
year = [str(i) for i in np.arange(1979, 2020)]   ## years
month = ['{:02d}'.format(i) for i in np.arange(1, 13)] ## months
day = ['{:02d}'.format(i) for i in np.arange(1, 32)] ## days
time =  ['{:02d}'.format(i) +':00' for i in np.arange(0, 24)] ## hours
area = [-22.5, 14.25, -27.75, 16.5] ## geographical subset

variable_dic = {'product_type':'reanalysis',
                'format': 'grib',
                'variable': variables,
                'year': year,
                'month': month,
                'day': day,
                'time': time,
                'area': area }

### launching request
Namibia.Getting_wind_data(variable_dic)

### Writing place specifications (ALWAYS call this function just after the requests)
Namibia.Write_spec('info.txt')

### Extracting data ### checl that your path to wgrib is correct
Namibia.Update_grib_name()
Namibia.Extract_UV(path_to_wgrib = '/home/gadal/Bin_local/')
Namibia.load_wind_data()

### Writing to binary files for fast futur loading
Namibia.Save_to_bin()

### Printing wind and flux roses
Namibia.Cartesian_to_polar()
Namibia.Write_wind_rose('wind_rose', ext = '.pdf',  normed=True, opening=1, edgecolor='k', nsector = 20, bins = 6)
Namibia.Write_flux_rose('flux_rose', ext = '.pdf', withaxe = 1, opening = 0.9, nsector = 30)

### Creating google earth points
Namibia.Update_coordinates()
Namibia.Write_coordinates()
Namibia.Create_KMZ()

#####################################################################
#####################################################################
# Imagine that you forgot to do this on the first script, but you want to do it later.
# You can write another script and just call:
Namibia = Era5.Wind_data()

## Loading specifications, in case you to start the script here with data already downloaded.
Namibia.load_spec('info.txt')

# Loading from binary files: If you want to load the data later, much quicker with binary files.
Namibia.load_from_bin()

### Writing wind data by point over grid
Namibia.Update_coordinates()
Namibia.Cartesian_to_polar()
Namibia.Write_wind_data('wind_data')

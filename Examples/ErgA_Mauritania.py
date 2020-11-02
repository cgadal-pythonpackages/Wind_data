
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 17:54:19 2020

@author: cyril
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# @Author: gadal
# @Date:   2019-05-22T13:35:05+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   cyril
# @Last modified time: 2020-01-14T11:17:19+01:00

path_lib = '/home/cyril/Documents/Stage_Jeanne/Python_lib'
import sys
sys.path.append(path_lib)

import Wind_data.Era_5 as Era5
import numpy as np

########### CReating wind data object
WindData = Era5.Wind_data('ErgA_Mauritania', type = 'reanalysis-era5-land')

########## Defining request (optional in theory but ..)
#Nsplit = 8  # Spliting request into Nsplit part. Automatically set by the function that send the requests (in theory).

### Specifying request
variables = ['10m_u_component_of_wind','10m_v_component_of_wind']  ## variables
year = [str(i) for i in np.arange(2001, 2017)]   ## years
month = ['{:02d}'.format(i) for i in np.arange(1, 13)] ## months
day = ['{:02d}'.format(i) for i in np.arange(1, 32)] ## days
time =  ['{:02d}'.format(i) +':00' for i in np.arange(0, 24)] ## hours
area = [17.8, -15, 17.6, -14.7] ## geographical subset

variable_dic = {'format': 'grib',
                'variable': variables,
                'year': year,
                'month': month,
                'day': day,
                'time': time,
                'area': area }

### launching request
WindData.Getting_wind_data(variable_dic)

### Writing place specifications (ALWAYS call this function just after the requests)
WindData.Write_spec('info.txt')

### Extracting data ### checl that your path to wgrib is correct
WindData.Update_grib_name()
WindData.Extract_UV(path_to_wgrib = '/home/gadal/Bin_local/')
WindData.load_time_series()

### Writing to binary files for fast futur loading
WindData.Save_to_bin()

### Printing wind and flux roses
WindData.Cartesian_to_polar()
WindData.Calculate_fluxes()
WindData.Write_wind_rose('wind_rose', ext = '.pdf',  normed=True, opening=1, edgecolor='k', nsector = 20, bins = 6)
WindData.Write_flux_rose('flux_rose', ext = '.pdf', withaxe = 1, opening = 0.9, nsector = 30)

### Creating google earth points
WindData.Update_coordinates()
WindData.Write_coordinates()
WindData.Create_KMZ()

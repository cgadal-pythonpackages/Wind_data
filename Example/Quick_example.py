# @Author: gadal
# @Date:   2020-12-01T16:01:33+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2020-12-01T16:02:40+01:00

import Wind_data.Era_5 as Era5
import numpy as np

########### CReating wind data object
Test = Era5.Wind_data('test_place', type = 'reanalysis-era5-single-levels')

### Specifying request
variables = ['10m_u_component_of_wind','10m_v_component_of_wind']  ## variables
year = [str(i) for i in np.arange(2010, 2011 + 1)]   ## years: from 2012 to 2018
month = ['{:02d}'.format(i) for i in np.arange(1, 12 + 1)] ## months: all of them
day = ['{:02d}'.format(i) for i in np.arange(1, 31 + 1)] ## days: all of them
time =  ['{:02d}'.format(i) +':00' for i in np.arange(0, 23 + 1)] ## hours: all of them
area = [-24, 15, -24, 15] ## geographical subset

variable_dic = {'product_type':'reanalysis',
                'format': 'netcdf',
                'variable': variables,
                'year': year,
                'month': month,
                'day': day,
                # 'grid': 0.1 # note that you can specify the grid span you want, and the CDS will interpolate for you. Native grid is 0.25 for ERA5 and 0.1 for ERA5Land.
                'time': time,
                'area': area}

### launching request
Test.Getting_wind_data(variable_dic)

##### Creating a KML file to show spatial points on Google Earth
Test.Update_coordinates()
Test.Write_coordinates()
Test.Create_KMZ()

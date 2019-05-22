# @Author: gadal
# @Date:   2019-05-22T13:35:05+02:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-05-22T16:34:09+02:00

import sys
sys.path.append('../')
import Wind_data.Era_5 as Era5
import numpy as np

########### CReating wind data object
Namibia = Era5.Wind_data()
Namibia.name = 'Namibia'

########## Defining request
Nsplit = 1  # Spliting request into 5 part

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
Namibia.Getting_wind_data(variable_dic, Nsplit)

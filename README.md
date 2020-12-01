# Wind_data

Wind_data is a Python library to download data from the Climate Data Store, but currently only supports very few of the available datasets.
For now, it is oriented to download data from the 'reanalysis-era5-single-levels' and 'reanalysis-era5-land' datasets and process the velocity at 10m.

## Quick example

```python
import Wind_data.Era_5 as Era5
import numpy as np

########### CReating wind data object
Test = Era5.Wind_data('test_place', type = 'reanalysis-era5-land')

### Specifying request
variables = ['10m_u_component_of_wind','10m_v_component_of_wind']  ## variables
year = [str(i) for i in np.arange(2012, 2018 + 1)]   ## years: from 2012 to 2018
month = ['{:02d}'.format(i) for i in np.arange(1, 12 + 1)] ## months: all of them
day = ['{:02d}'.format(i) for i in np.arange(1, 31 + 1)] ## days: all of them
time =  ['{:02d}'.format(i) +':00' for i in np.arange(0, 23 + 1)] ## hours: all of them
area = [-24.126, 15.049, -24.126, 15.049] ## geographical subset

variable_dic = {'format': 'netcdf',
                'variable': variables,
                'year': year,
                'month': month,
                'day': day,
                'time': time,
                'area': area}

### launching request
Test.Getting_wind_data(variable_dic)

##### Creating a KML file to show spatial points on Google Earth
Test.Update_coordinates()
Test.Write_coordinates()
Test.Create_KMZ()
##
```

## Usefull details

### Optional keywords

The functions have plenty of optional keywords, I will write a documentation as soon as possible. In the mean time, here is a list of usefull keywords in `Getting_wind_data()` to play with.

- `save_to_npy = True`: if you want to convert netcdf files to .npy files. True is only supported for 10m velocities. Default is True.
- `on_grid = True`: if you want to have the spacial points given moved to correspond to the original grid of the downloaded dataset. Default it True.
- `file = 'info.txt'`: Name of the file some informations will be written to.
- `Nsplit = 1`: Number of sub-requests you request will be split to. Theroretically, it is automatically calculated by the function. If an error ocurr, try to increase it. Default is 1 but automatically calculated.


### Differences between datasets

The different datasets have differences in the `variable_dic` passed to `Test.Getting_wind_data()`. In particular, for the , you have to add the entry `'product_type':'reanalysis'`. More details can be found on the original documentation of the CDSAPI.

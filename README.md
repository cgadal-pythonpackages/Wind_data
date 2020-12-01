# Wind_data

Wind_data is a Python library to download data from the Climate Data Store, but currently only supports very few of the available datasets.
For now, it is oriented to download data from the 'reanalysis-era5-single-levels' and 'reanalysis-era5-land' datasets and process the velocity at 10m.

## Set up
As the data are downloaded through the Climate Data Store API, you need to follow a few steps:

- create an account [here](https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome), and log in.
- setup the API key on your computer: see [here](https://cds.climate.copernicus.eu/api-how-to)
- install the lib on your computer: As for most python package, use pip. In a terminal run `pip3 install --upgrade https://github.com/Cgadal/Wind_data/tarball/master`. If you also have `git` installed on your computer, you may prefer to use: `pip install git+https://github.com/Cgadal/Wind_data.git`.

General documentation can be found on the ECMWWF website, for [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) and [ERA5Land](https://www.ecmwf.int/en/era5-land).

Note that I am quite unsure on how this is going to work on other O.S. than Linus distributions.

## Quick example

```python
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
##
```

## Usefull details

### Optional keywords

The functions have plenty of optional keywords, I will write a documentation as soon as possible. In the mean time, here is a list of usefull keywords in `Getting_wind_data()` to play with.

- `save_to_npy = True`: if you want to convert netcdf files to .npy files. `True` is only supported for 10m velocities. Default is True.
- `on_grid = True`: if you want to have the spacial points given moved to correspond to the original grid of the downloaded dataset. Default it True.
- `file = 'info.txt'`: Name of the file some informations will be written to.
- `Nsplit = 1`: Number of sub-requests you request will be split to. Theroretically, it is automatically calculated by the function. If an error ocurr, try to increase it. Default is 1 but replaced if found to be too low.


### Differences between datasets

The different datasets have differences in the `variable_dic` passed to `Test.Getting_wind_data()`. In particular, for the `'reanalysis-era5-land'` dataset, you need to remove the entry `'product_type':'reanalysis'`. More details can be found on the original documentation of the CDSAPI.

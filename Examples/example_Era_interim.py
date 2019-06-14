# @Author: gadal
# @Date:   2018-12-14T18:00:01+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-06-14T14:31:05+02:00


import sys
sys.path.append('../')
import Era_Interim

######################################  Create the wanted wind data Data base :
Skeleton_Coast = Era_Interim.Wind_data()
Skeleton_Coast.name =  'Skeleton_Coast'

####################################################### Define its attributes :
Skeleton_Coast.grid_bounds = [[-23.8,14.07], [-26.3,16.7]]
Skeleton_Coast.years = [[1979,1,1], [2017,12,31]]

######################### Retrieve the wind data fron the Era Interim serveur :
#### Do not forget to split your request it's too large.
Nsplit = 3
Skeleton_Coast.Update_grib_name()
Skeleton_Coast.Getting_wind_data(Skeleton_Coast.grid_bounds, Nsplit)

#Write these attributes to .txt file that can be re-loaded.
Skeleton_Coast.Write_spec('info.txt')

################################################### Proceed the raw wind data :
Skeleton_Coast.Extract_UV(path_to_wgrib = '/home/gadal/Bin_local')
Skeleton_Coast.load_wind_data()
Skeleton_Coast.Cartesian_to_polar()

# Optional, write the wind data to separate .txt files.
Skeleton_Coast.Write_wind_data('wind_data')

###############################################  Plot the wind and flux roses :
Skeleton_Coast.Write_wind_rose('wind_rose', ext = '.pdf',  normed=True,
opening=1, edgecolor='k', nsector = 20, bins = 6)
Skeleton_Coast.Write_flux_rose('flux_rose', ext = '.pdf', withaxe = 1,
opening = 0.9)

######################## Create the KML points to see the grid on google Earth:
Skeleton_Coast.Update_coordinates()
Skeleton_Coast.Write_coordinates()
Skeleton_Coast.Create_KMZ()

# @Author: gadal
# @Date:   2018-12-11T14:18:01+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-10-23T13:38:35+02:00



import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from windrose import WindroseAxes

def wind_rose(Angle, Intensity, place = None, fig = None, **kwargs):
    #### Angle : Orientation of the wind
    #### Intensity : Intensity of tje wind
    #### Nbin : nbins in terms of velocity
    #### Nsector : n bins in terms of direction

    Angle = np.array(Angle)
    Intensity = np.array(Intensity)

    ## removing nans
    inds = ~np.logical_or(np.isnan(Angle), np.isnan(Intensity))
    Angle = Angle[inds]
    Intensity = Intensity[inds]
    ####### documentation https://windrose.readthedocs.io/en/latest/

    ax = WindroseAxes.from_ax(fig = fig)
    if place != None:
        ax.set_position(place, which='both')
    # bars = ax.bar(Angle, Intensity, normed=True, opening=1, edgecolor='k', nsector = Nsector, bins = Nbin, cmap = cmap)
    Angle = (90 - Angle)%360
    bars = ax.bar(Angle, Intensity,  **kwargs)
    ax.set_legend()

def flux_rose(Angle, PdfQ_tp, withaxe = 0, place = None, fig = None, color = 'green', nsector = 20, opening = 0.6):
    #### pdfQ flux distribution
    #### Corresponding angles in degree
    #### N bin nuber of bins for the rose
    #### withaxe : if 0, removes everything except the bars
    #### place :: where on the figure

    PdfQ = PdfQ_tp/np.nansum(PdfQ_tp)  # normalization
    ######## creating the new pdf with the number of bins
    Lbin = 360/nsector
    Bins = np.arange(0, 360, Lbin)
    Qdat = []
    Qangle = []
    precision_flux = 0.001

    for n in range(len(Bins)) :
        ind = np.argwhere((Angle >= Bins[n] - Lbin/2) & (Angle < Bins[n] + Lbin/2))
        integral = int(np.nansum(PdfQ[ind])/precision_flux)
        for i in range(integral):
            Qangle.append(Bins[n])
            Qdat.append(1)
    Qangle = np.array(Qangle)
    #ax = plt.subplot(111, projection='polar')
    ax = WindroseAxes.from_ax(fig = fig)
    if place != None:
        ax.set_position(place, which='both')
    # bars = ax.bar(Angle, Intensity, normed=True, opening=1, edgecolor='k', nsector = Nsector, bins = Nbin, cmap = cmap)
    Qangle = (90 - Qangle)%360
    if Qangle.size !=0:
        bars = ax.bar(Qangle, Qdat, color = color, nsector = nsector, opening = opening)
        ax.set_rmin(0)
        plt.plot(0,0,'.', color = 'w', zorder = 100, markersize = 4)
        ax.set_yticklabels(['{:.1f}'.format(float(i.get_text())*precision_flux) for i in ax.get_yticklabels()])
        if withaxe != 1:
            ax.set_yticks([])

def Wind_to_flux(wind_direction, wind_strength, grain_size, z_0 = 1e-3, z = 10, rhoair = 1.293, rhosed = 2.55e3, threshold = False):
        # Data : first column are directions, second column are speed
        # d : grain diameter
        # dt : step of the time serie
        # z_0 = 1e-3 : Roughness of the sediment layer. (meters)
        # z = 10  : Height of wind speed measurment.
        # rhoair = 1.293 : air density [kg/m^3].
        # rhosed = 2.55e3 : sediment density [kg/m^3].

        direction = wind_direction
        speed = wind_strength

        kappa = 0.4                  # Von Karman constant.
        # d = 180e-6;                   % grain diameter [m].
        u = speed*kappa/np.log(z/z_0)      # Shear velocity  [m/s] fron the law of the wall
        g = 9.81                     # Gravitational acceleration [m/s^{-2}].
        ut = 0.1 * np.sqrt((rhosed-rhoair)*g*grain_size/rhoair)

        ######## flux
        # qs = np.maximum(0,((ut*rhoair)/(rhosed *grain_size))*(u**2-ut**2))
        if not threshold :
            qs = np.maximum(0,(25*(rhoair/rhosed)*np.sqrt(grain_size/g))*(u**2-ut**2))
            return qs, direction
        else:
            qs = np.maximum(0,(25*(rhoair/rhosed)*np.sqrt(grain_size/g))*(u**2-ut**2))
            r = np.maximum(1, (25*(rhoair/rhosed)*np.sqrt(grain_size/g))*(u**2-ut**2))
            return qs, direction, r


def PDF_flux(direction, qs):
    # direction : flux direction
    # qs : flux intensity
     return Make_angular_PDF(direction, qs)


def Make_angular_PDF(quantity, weight):
    hist, bin_edges = np.histogram(quantity, bins = np.linspace(0, 360, 361), density = 1, weights = weight)
    a = np.array([np.mean(bin_edges[i:i+2]) for i in range(bin_edges.size -1)])
    return hist, a


def Make_threshold_distribution(direction, r):
    bin_edges = np.linspace(0, 360, 361)
    ut = []
    for i in range(bin_edges.size - 1):
        vel = r[(direction >= bin_edges[i]) & (direction > bin_edges[i+1])]
        ut.append(np.mean(vel[vel > 1]))
    a = np.array([np.mean(bin_edges[i:i+2]) for i in range(bin_edges.size -1)])
    return np.array(ut), a

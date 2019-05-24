# @Author: gadal
# @Date:   2018-12-11T14:18:01+01:00
# @Email:  gadal@ipgp.fr
# @Last modified by:   gadal
# @Last modified time: 2019-05-24T17:58:10+02:00



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

    PdfQ = PdfQ_tp/np.sum(PdfQ_tp)  # normalization
    ######## creating the new pdf with the number of bins
    Lbin = 360/nsector
    Bins = np.linspace(Lbin/2,360-Lbin/2,nsector)
    Qdat = []
    Qangle = []
    precision_flux = 0.001

    for n in range(len(Bins)) :
        ind = np.argwhere((Angle >= Bins[n] - Lbin/2) & (Angle < Bins[n] + Lbin/2))
        integral = int(sum(PdfQ[ind])/precision_flux)
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
    bars = ax.bar(Qangle, Qdat, color = color, nsector = nsector, opening = opening)
    ax.set_rmin(0)
    plt.plot(0,0,'.', color = 'w', zorder = 100, markersize = 4)
    ax.set_yticklabels(['{:.1f}'.format(float(i.get_text())*precision_flux) for i in ax.get_yticklabels()])
    if withaxe != 1:
        ax.set_yticks([])

def PDF_flux(wind_data, grain_size):

    # Data : first column are directions, second column are speed
    # d : grain diameter
    # dt : step of the time serie

    direction = wind_data[:,0]
    speed = wind_data[:,1]

    kappa = 0.4                  # Von Karman constant.
    # d = 180e-6;                   % grain diameter [m].
    z_0 = 1e-3                   # Roughness of the sediment layer. (meters)
    z = 10                    # Height of wind speed measurment.
    u = speed*kappa/np.log(z/z_0)      # Shear velocity  [m/s] fron the law of the wall
    rhoair = 1.293               # air density [kg/m^3].
    rhosed = 2.55e3              # sediment density [kg/m^3].
    g = 9.81                     # Gravitational acceleration [m/s^{-2}].
    ut = 0.1 * np.sqrt((rhosed-rhoair)*g*grain_size/rhoair)
    # ut = 0.15;                    % Shear velocity threshold for motion inception [m/s].
    # Lsat = 2.2 *(rhosed/rhoair)*d ; % saturation length

    ######## flux
    # qs = np.maximum(0,((ut*rhoair)/(rhosed *grain_size))*(u**2-ut**2))
    qs = np.maximum(0,(25*(rhoair/rhosed)*np.sqrt(grain_size/g))*(u**2-ut**2))
    Ntheta = 360
    dN = 360/(Ntheta-1)
    pdfQ = np.zeros((Ntheta-1,))
    r = np.zeros((Ntheta-1,))

    Angle = np.linspace(0,Ntheta,360)
    for n in range(Ntheta-1):
        ind = (direction >= Angle[n]) & (direction < Angle[n+1])
        pdfQ[n] = np.nansum(qs[ind])

        ua = u[ind]
        ind2 = np.argwhere(ua/ut >=1)
        if np.size(ua[ind2]) == 0:
            r[n] = 1
        else:
            r[n] = np.nanmean(ua[ind2]/ut)

    # Qtot = np.nansum(pdfQ)
    # pdfQ = pdfQ/Qtot
    Angle = Angle + ((Angle[1]-Angle[0])/2)%360
    return pdfQ, Angle, r

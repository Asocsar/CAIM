import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def zips_func(rank, c, a , b):
    return c/((rank+b)**a)


def zips_law(frec):
    rango = list(range(1, len(frec)+1))
    plt.plot(rango, frec, label="Data")

    result, cov = curve_fit(f=zips_func, xdata=rango, ydata=frec, bounds=(-np.inf, np.inf), p0=[230000,1,1], method='lm')

    plt.plot(zips_func(rango, *result), label= "Zips")
    
    plt.text(1, 1.0, "c = {}, a = {}, b = {}".format(*result), fontsize='x-small')
    plt.yscale("log")
    plt.xscale("log")
    plt.legend()


    plt.show()

def show(datos):
    frec = []
    for (rank, (word,frecu)) in enumerate(datos[-4::-1]):
        frec.append(frecu)
        
    #zips_law(frec)


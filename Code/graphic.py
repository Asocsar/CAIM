import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def zips_func(rank, c, a , b):
    return c/((rank+b)**a)


def show(datos):
    frec = []
    for (rank, (word,frecu)) in enumerate(datos[-3::-1]):
        frec.append(frecu)
    rango = list(range(1, len(frec)+1))
    plt.plot(rango, frec, label="Data")

    result, cov = curve_fit(f=zips_func, xdata=rango, ydata=frec, bounds=(-np.inf, np.inf), p0=[230000,1,1], method='lm')

    plt.plot(zips_func(rango, *result), label= "Zips")


    plt.yscale("log")
    plt.xscale("log")
    plt.legend()


    plt.show()

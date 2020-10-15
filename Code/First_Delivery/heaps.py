import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def heaps_func(N, k, beta):
    return k*(N**beta)

def heaps_law(total, difer, index):
    
    plt.plot(total, difer, label="Data")

    result, cov = curve_fit(f=heaps_func, xdata=total, ydata=difer, bounds=(-np.inf, np.inf), method='lm')

    plt.plot(total, heaps_func(total, *result), label= "Heaps")
    plt.title(index)
    print(result)
    plt.text(1, 0, "k = {}, beta = {}".format(*result))
    plt.legend()


    plt.show()

def show(datos, index):
    total = []
    difer = []
    for sub_frec in datos:
        total.append(np.sum(sub_frec)) 
        difer.append(len(sub_frec))
    heaps_law(total, difer, index)


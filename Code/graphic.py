import matplotlib.pyplot as plt

def show(datos):
    rango = list(range(0, len(datos)))
    frec = []
    for (rank, (word,frecu)) in enumerate(datos[::-1]):
        frec.append(frecu)
    
    plt.plot(rango, frec)
    plt.yscale("log")
    plt.xscale("log")
    plt.show()

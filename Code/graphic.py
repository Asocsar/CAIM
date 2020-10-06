import matplotlib.pyplot as plt

def show(datos):
    frec = []
    for (rank, (word,frecu)) in enumerate(datos[-3::-1]):
        frec.append(frecu)
    rango = list(range(0, len(frec)))
    plt.plot(rango, frec)
    plt.yscale("log")
    plt.xscale("log")
    plt.show()

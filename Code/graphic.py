import matplotlib.pyplot as plt

def show(datos):
    frec = []
    for (rank, (word,frecu)) in enumerate(datos[-3::-1]):
        frec.append(frecu)
    rango = list(range(1, len(frec)+1))
    plt.plot(rango, frec, label="Data")
    plt.yscale("log")
    plt.xscale("log")

    c = 10000
    rank = rango[:]
    b = 1
    a = 30

    plt.plot(rank, [c/((x+b)**a) for x in rank], label= "Zips")
    plt.legend()


    plt.show()

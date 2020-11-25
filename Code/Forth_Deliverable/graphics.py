import matplotlib.pyplot as plt
import numpy as np
import sys


def plot_time():
    times = open('times.txt', 'r')
    data_times = [float(x.split()[-1]) for x in times.readlines()]
    times.close()
    plt.title('Time for diferents damping factor')
    plt.xlabel('Damping Factor')
    plt.ylabel('Time in seconds')
    plt.plot(np.linspace(0.8, 0.9, 10), data_times)
    plt.show()

def plot_results():
    output = open('output.txt', 'r')
    data_out = output.read()
    output.close()
    data_out = data_out.split('\n')[5:]
    all_results = [[] for _ in range(10)]
    line = 0
    sect = -1
    while line < len(data_out):
        if '*------------------------------*' in data_out[line]:
            line += 11
            sect += 1
        else:
            current_line = data_out[line].split(' ')
            all_results[sect].append((current_line[-3], float(current_line[-1])))
        line += 1

    for i, arr in enumerate(all_results):
        arr_aux = sorted(arr, key=lambda x: x[1])
        all_results[i] = arr_aux
    
    datos = []
    info = []
    dampings = np.linspace(0.8,0.9,10)
    for i, arr in enumerate(all_results):
        top_nodes = [x + '_' +str(int(dampings[i]*100)/100) for (x,_) in arr[-5:]]
        info_nodes = [x for (_,x) in arr[-5:]]
        datos += top_nodes.copy()
        info += info_nodes.copy()
    
    

    plt.bar(datos, info)
    plt.xticks(rotation='vertical')
    plt.show()

def main(argv=None):
    plot_time()
    plot_results()

if __name__ == "__main__":
    sys.exit(main())
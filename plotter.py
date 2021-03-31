import matplotlib.pyplot as plt
import numpy as np

class Plotter():

    @staticmethod
    def plot(info):
        plt.plot(info[0], info[1], info[0], info[1], 'bo')
        plt.title("Simulated Annealing - 8 Queen Problem")
        plt.ylabel('Best solution\'s evaluation')
        plt.xlabel('Iterations')
        plt.show()

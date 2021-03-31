from board import *
import math

class Annealing():

    ### HYPERPARAMETERS ###

    max_k = 250 # Spot criteria; Max iterations

    start_c = 0.1 # Initial c for heating
    beta = 1.1 # For heating
    alpha = 0.95 # For cooling
    L = 30 # Neighbour tries per iteration

    r_max = 0.9 # Stop heating starting temp when neighbour_tries / accepted_tries >= r_max

    #######################

    def __init__(self, board, starting = False):
        self.k = 0
        self.neighbour_tries = 0
        self.accepted_tries = 0
        self.running = starting
        self.u = board.evaluate()
        self.all_time_best = [self.u, board.saveBoard()]
        self.plot_info = [[], []]
        self.c = self.getStartingTemp(board) # heat up c before starting algorithm

    def getProb(self, v, c = None, u = None): # Return boolean value which defines wheter or not neighbour solution should be accepted
        if c == None:
            c = self.c
        if u == None:
            u = self.u

        return float(random.randrange(0, 2)) / 100 < math.exp(- (v - u) / float(c))

    def getStartingTemp(self, board):
        c = Annealing.start_c
        u = 0
        r = 0
        ntries = 0 # neighbour tries
        atries = 0 # accepted tries
        while r < Annealing.r_max:
            for l in range(Annealing.L):
                board.generate_neighbour_solution() # Get neighbour solution
                v = board.evaluate() # Evaluate it
                if v <= u:
                    u = v # Found better solution!
                    atries += 1
                else:
                    if self.getProb(v, c, u): # Worse solution, use probability function
                        u = v
                        atries += 1
                    else:
                        board.undo_last_queen_swap() # No luck, go back to previous board state

                ntries += 1

            c *= Annealing.beta # heat up
            r = atries / ntries # calculate acceptance rate
            atries = 0
            ntries = 0

        return c

    def getNextTemp(self):
        self.c *= Annealing.alpha # cool

    def storeInfo(self):
        # If there is a better all time best, store its info so that it can be graphed
        if not len(self.plot_info[1]) or self.all_time_best[0] < self.plot_info[1][len(self.plot_info[1]) - 1]:
            self.plot_info[0].append(self.k) # x axis
            self.plot_info[1].append(self.all_time_best[0]) # y axis

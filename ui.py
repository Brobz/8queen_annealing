import curses, time
from annealing import *
from plotter import *


class UI:
    def __init__(self, board):
        # Store board
        self.board = board

        # Board scale
        self.boardScale = (6, 3)

        # Offset when drawing board
        self.boardOffset = [3, 2]

        # Set labels
        self.instructionLabels =    [
                                        "Run/Pause Algorithm: Enter\t   Plot Results: P",
                                        "Restart Algorithm: R\t\t   Exit: Q"
                                    ]

        # Set annealing variables
        self.prepare_for_annealing()

        # Init labels
        self.getEvalLabel()
        self.getPressedLabel(-1)

        # Init Module
        curses.wrapper(self.mainloop)

        # self.noUI()

    def noUI(self):
        while 1:
            input()
            recocido_simulado(self.board)

    def mainloop(self, stdscr):
        # Define symbols for empty square and queen
        self.symbols = [' ', curses.ACS_DIAMOND]

        # Turn off cursor blinking
        curses.curs_set(0)

        # White on black color scheme
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Black on white color scheme
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Black on green color scheme
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)

        # Set screen object as class property
        self.stdscr = stdscr

        # Set nodelay mode
        self.stdscr.nodelay(1)

        # Set framerate
        self.stdscr.timeout(100)

        # Get screen height and width
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

        while 1:

            key = self.stdscr.getch() # Get input

            self.getPressedLabel(key) # Get pressed label

            self.stdscr.clear() # Clear screen


            if self.annealing.running: # Algorithm is running
                if self.annealing.k < Annealing.max_k and self.annealing.all_time_best[0] > 0: # Run max_k iterations OR until 0 eval solution is found
                    for l in range(Annealing.L):
                        self.board.generate_neighbour_solution() # Get neighbour solution
                        v = self.board.evaluate() # Evaluate it
                        if v <= self.annealing.u:
                            self.annealing.u = v # Found better solution!
                            self.annealing.accepted_tries += 1
                        else:
                            if self.annealing.getProb(v): # Worse solution, use probability function
                                self.annealing.u = v
                                self.annealing.accepted_tries += 1
                            else:
                                self.board.undo_last_queen_swap() # No luck, go back to previous board state

                        if self.annealing.u <= self.annealing.all_time_best[0]:
                            self.annealing.storeInfo() # Store best eval and iteration number to be graphed later
                            self.annealing.all_time_best = [self.annealing.u, self.board.saveBoard()] # Store all time best evaluation and board state

                        self.annealing.neighbour_tries += 1

                    self.annealing.k += 1

                    # Recalculate temperature
                    self.annealing.getNextTemp()


                else:
                    self.board.setBoard(self.annealing.all_time_best[1]) # Set board to all time best state
                    self.getEvalLabel()
                    self.getAnnealingLabels()
                    self.annealing.running = False # Stop running algorithm


            # Draw labels
            self.color_print_str(1, 3, self.evalLabel, 1)
            for i, label in enumerate(self.instructionLabels):
                self.color_print_str(8 * self.boardScale[1] + self.boardOffset[1] + i, 3, label, 1)
            self.color_print_str(8 * self.boardScale[1] + self.boardOffset[1] + len(self.instructionLabels), 3, self.pressedLabel, 1)

            for i, label in enumerate(self.annealing_labels):
                self.color_print_str(3 * self.boardScale[1] + self.boardOffset[1] + (i * 2) - 1, 8 * self.boardScale[0] + self.boardOffset[0] + 1, label, 1)

            # Draw board
            for y, row in enumerate(self.board.board):
                for x, square in enumerate(row):
                    square_color = (y + x) % 2 # Get board color
                    for i in range(self.boardScale[1]):
                        for j in range(self.boardScale[0]): # Draw square to scale
                            self.draw(x * self.boardScale[0] + j + self.boardOffset[0], y * self.boardScale[1] + i + self.boardOffset[1], square, square_color + 2)

            if key in [113]:
                return # If Q is pressed, exit
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # If enter is pressed, run/pause/restart the algorithm
                if not self.annealing.k or self.annealing.k == Annealing.max_k or not self.annealing.all_time_best[0]: # Run it for the first time, or restart it if it has ended
                    self.prepare_for_annealing(True)
                else: # Else, resume it / pause it
                    self.annealing.running = not self.annealing.running
            elif key in [114]: # R was pressed, restart annealing
                self.prepare_for_annealing()
            elif key in [112]: # P was pressed, plot!
                Plotter.plot(self.annealing.plot_info)

            if self.annealing.running: # If algorithm is running, update labels
                self.getEvalLabel()
                self.getAnnealingLabels()

    # Updates annealing realted labels
    def getAnnealingLabels(self):
        self.annealing_labels = []

        if self.annealing.running:
            if not self.annealing.all_time_best[0]:
                self.annealing_labels.append("Simulated Annealing: Solution Found!")
            elif self.annealing.k == Annealing.max_k:
                self.annealing_labels.append("Simulated Annealing: Finished Running")
            else:
                self.annealing_labels.append("Simulated Annealing: Running")
        else:
            self.annealing_labels.append("Simulated Annealing: Not Running")

        self.annealing_labels.append("k: " + str(self.annealing.k) + " of " + str(Annealing.max_k) + " (" + str(self.annealing.k / Annealing.max_k * 100)[:5] + "%)")
        self.annealing_labels.append("c: " + str(round(self.annealing.c, 8)) + "\tNeighbour Tries: " + str(self.annealing.neighbour_tries))
        self.annealing_labels.append("alpha: " + str(Annealing.alpha) + "\tbeta: " + str(Annealing.beta) + "\tL: " + str(Annealing.L))
        self.annealing_labels.append("Best Evaluation: " + str(self.annealing.all_time_best[0]))


    # Reset annealing variables
    def prepare_for_annealing(self, starting = False):
        self.board.init_board()
        self.annealing = Annealing(self.board, starting)
        self.board.init_board()
        self.annealing.all_time_best = [self.board.evaluate(), self.board.saveBoard()]
        self.getAnnealingLabels()
        self.getEvalLabel()

    # Sets the pressed label to the value of the key that is pressed
    def getPressedLabel(self, input):
        if input == -1:
            self.pressedLabel = "Pressed: None"
        else:
            self.pressedLabel = "Pressed: " + str(input)

    # Sets eval label
    def getEvalLabel(self):
        self.evalLabel = 'The 8 Queen Problem\t   Current Evaluation: ' + str(self.board.evaluate())

    # Draw to console
    def draw(self, x, y, target, pair_num):
        self.color_print_ch(y, x, self.symbols[target], pair_num)

    # Print char
    def color_print_ch(self, y, x, text, pair_num):
        self.stdscr.attron(curses.color_pair(pair_num))
        self.stdscr.addch(y, x, text)
        self.stdscr.attroff(curses.color_pair(pair_num))

    # Print string
    def color_print_str(self, y, x, text, pair_num):
        self.stdscr.attron(curses.color_pair(pair_num))
        self.stdscr.addstr(y, x, text)
        self.stdscr.attroff(curses.color_pair(pair_num))

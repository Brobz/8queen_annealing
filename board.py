import random

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class Queen:
    def __init__(self, pos):
        self.pos = pos # Tuple containing X and Y position on the board
        self.score = 0 # How many other queens is this queen threatening?

class Board:
    def __init__(self):
        self.max_neighbour_distance = 7
        self.init_board()

    def init_board(self, random = True):
        self.last_queen_swap = [-1, (-1, -1)] # Contains the info to undo the last queen swap (queen index and previous position) e.g. [0, (0, 0)]. If it is -1, no prev swap exists.
        self.board =        [
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0]
                            ]

        if random:
            self.init_queens()


    def setBoard(self, queen_positions):
        self.init_board(False)

        self.queens = []

        for qp in queen_positions:
            self.place_queen(qp)

    def saveBoard(self):
        queen_positions = []

        for q in self.queens:
            queen_positions.append(q.pos)

        return queen_positions

    def init_queens(self):
        self.queens = []
        new_pos = (random.randrange(8), random.randrange(8)) # Random starting position for the queen
        for i in range(8):
            while not self.available_pos(new_pos): # Check if spot is available on the board
                new_pos = (random.randrange(8), random.randrange(8)) # If not, generate new position
            self.place_queen(new_pos) # If it is, place the queen there


    def available_pos(self, pos):
        if not self.board[pos[1]][pos[0]]: # Check board position
            return True # A 0 on the board matrix meeans no queen
        return False # A 1 means a queen

    def place_queen(self, pos):
        self.queens.append(Queen(pos)) # Instatiate new queen and add it to queen array
        self.board[pos[1]][pos[0]] = 1 # Mark it on the board


    def undo_last_queen_swap(self):
        if self.last_queen_swap[0] < 0:
            return
        self.swap_queen_pos(self.last_queen_swap[0], self.last_queen_swap[1]) # Swap it back


    def swap_queen_pos(self, queen_index, new_pos):
        old_pos = self.queens[queen_index].pos # Get old queen pos
        self.board[old_pos[1]][old_pos[0]] = 0 # Set old pos to 0 in board matrix
        self.board[new_pos[1]][new_pos[0]] = 1 # Set new pos to 1 in board matrix
        self.queens[queen_index].pos = new_pos # Set queen to new pos
        self.last_queen_swap = [queen_index, old_pos] # Store swap info

    def generate_neighbour_solution(self):
        i = random.randrange(8) # Queen that will be relocated
        new_pos = self.queens[i].pos
        while not self.available_pos(new_pos): # Check if spot is available on the board
            i = random.randrange(8) # Queen that will be relocated
            n = (random.randrange(-self.max_neighbour_distance, self.max_neighbour_distance + 1), random.randrange(-self.max_neighbour_distance, self.max_neighbour_distance + 1)) # New pos delta, bsed on distance parameter
            new_pos = (clamp(self.queens[i].pos[0] + n[0], 0, 7), clamp(self.queens[i].pos[1] + n[1], 0, 7)) # New queen pos


        self.swap_queen_pos(i, new_pos) # Swap queen pos


    def evaluate(self):
        total_score = 0 # Start the total score on 0
        for q in self.queens: # Loop through every queen

            q.score = 0 # Reset Queen score

            # Check Row
            for x in range(8):
                if x == q.pos[0]:
                    continue # No need for the queen to check itself
                if not self.available_pos((x, q.pos[1])):
                    q.score += 1

            # Check Column
            for y in range(8):
                if y == q.pos[1]:
                    continue # No need for the queen to check itself
                if not self.available_pos((q.pos[0], y)):
                    q.score += 1


            # Check Upper Left Diagonal
            n = 1
            while(q.pos[0] - n >= 0 and q.pos[1] - n >= 0):
                if not self.available_pos((q.pos[0] - n, q.pos[1] - n)):
                    q.score += 1
                n += 1

            # Check Upper Right Diagonal
            n = 1
            while(q.pos[0] + n < 8 and q.pos[1] - n >= 0):
                if not self.available_pos((q.pos[0] + n, q.pos[1] - n)):
                    q.score += 1
                n += 1

            # Check Lower Left Diagonal
            n = 1
            while(q.pos[0] - n >= 0 and q.pos[1] + n < 8):
                if not self.available_pos((q.pos[0] - n, q.pos[1] + n)):
                    q.score += 1
                n += 1

            # Check Lower Right Diagonal
            n = 1
            while(q.pos[0] + n < 8 and q.pos[1] + n < 8):
                if not self.available_pos((q.pos[0] + n, q.pos[1] + n)):
                    q.score += 1
                n += 1

            total_score += q.score # Add queen score to total score

        return total_score / 2 # Since Every collision is counted twice (by both queens that collide), we divide total score by 2

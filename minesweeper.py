import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8, starting_position=None):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        available_squares = [(x, y) for x in range(height) for y in range(width)]
        available_squares.remove(starting_position)
        for i in [x for x in range(starting_position[0] - 1, starting_position[0] + 2) if 0 <= x < height]:
            for j in [y for y in range(starting_position[1] - 1, starting_position[1] + 2) if 0 <= y < width]:
                if (i, j) != starting_position:
                    available_squares.remove((i, j))
        while len(self.mines) != mines:
            available_count = len(available_squares)
            i, j = available_squares[random.randrange(available_count)]
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) > 0:
            if self.count == len(self.cells):
                return self.cells
        return False

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if len(self.cells) > 0:
            if self.count == 0:
                return self.cells
        return False

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8, difficulty=1):

        # Set initial height and width
        self.height = height
        self.width = width
        self.difficulty = difficulty

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell) #1
        self.mark_safe(cell) #2
        cs = set() #3
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made:
                        cs.add((i, j))
        #if Sentence(cells, count) not in self.knowledge:
        self.knowledge.append(Sentence(cs, count))
        #4
        i = copy.copy(self.difficulty)
        while i > 0:
            #print('1')
            mine_set = set()
            safe_set = set()
            for sentence in self.knowledge:
                is_mine = sentence.known_mines()
                is_safe = sentence.known_safes()
                if is_mine != False:
                    for m in is_mine:
                        mine_set.add(m)
                elif is_safe != False:
                    for s in is_safe:
                        safe_set.add(s)
            if mine_set != None:
                for m in mine_set:
                    self.mark_mine(m)
            if safe_set != None:
                for s in safe_set:
                    self.mark_safe(s)
            for m in self.mines:
                for sentence in self.knowledge:
                    sentence.mark_mine(m)
            i -=1
        #5
        #Remove empty sentences
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        #Deduce new sentences from subsets
        i = copy.copy(self.difficulty)
        while i > 1:
            append_list = []
            if self.difficulty > 1:
                for sentence in self.knowledge:
                    for subsentence in self.knowledge:
                        if sentence.cells > subsentence.cells:
                            append_list.append(Sentence(sentence.cells - subsentence.cells, sentence.count - subsentence.count))
                            
            for sentence in append_list:
                if sentence not in self.knowledge:
                    self.knowledge.append(sentence)
            i -=1

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        for position in list(self.safes):
            if position not in self.moves_made:
                return position
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        spare = []

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    spared = False
                    for a in range(i - 1, i + 2):
                        if spared == True:
                            break
                        for b in range(j - 1, j + 2):
                            if 0 <= a < self.height and 0 <= b < self.width:
                                if (a, b) in self.moves_made:
                                    spare.append((i, j))
                                    spared = True
                                    break
                    if (i, j) not in spare:
                        return (i, j)
        if len(spare) > 0:
            return spare[random.randrange(len(spare))]                    
        return None


import itertools
import random
import math
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

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
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
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
        """
        :param cell: (i, j)
        :return: the corresponding  value of that cell in the board (True or False)
        """
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
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        clone = self.cells.copy()
        for cell0 in clone:
            if cell0 == cell:
                self.cells.discard(cell)
                self.count -= 1
                break

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

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
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
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
        # Mark the cell as a move that has been made
        ################################################################################################################
        self.moves_made.add(cell)
        ################################################################################################################

        # Mark the cell as safe: removing this particular cell from any sentence if it does exist
        ################################################################################################################
        self.mark_safe(cell)
        ################################################################################################################


        # Add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`. However before making a sentence, I should take
        # into consideration if a neighboring cell is already in self.mines or self.safes or self.made_moves
        # and decrement the count and the neighboring cells accordingly.
        ################################################################################################################
        # a list to hold neighboring cells
        cells = []
        # iterate through all neighboring cells
        for cell1 in self.neighbors(cell):
            # if a neighboring cell is already marked as a mine then
            # decrement the count by one and do not append it to cells.
            if cell1 in self.mines:
                count -= 1
                continue
            # if a neighboring cell is already marked as a safe or made cell then don't append it to cells
            if cell1 in self.safes or cell1 in self.moves_made:
                continue
            # otherwise append it to cells
            cells.append(cell1)
        # if there is any cell remained after all that filtering then proceed with composing a sentence
        if len(cells):
            new_sentence = Sentence(cells, count)
            # one more condition before committing to adding new_sentence: make sure it is a new sentence for real!
            # (I know I might be unnecessarily extra cautious but I am so afraid of repetitions and confusing the AI)
            if new_sentence not in self.knowledge:
                self.knowledge.append(Sentence(cells, count))
        ################################################################################################################


        # Mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        ################################################################################################################
        # This function would iterate through the KB's sentences looking for any known mines or safes
        self.mark_mines_safes()
        # as I am removing known mines and safes and constantly filtering out AI's sentences, some
        # sentences would end up either becoming empty with no cells or identical to other sentences.
        # the following two functions would clean up the KB from such useless sentences
        self.clean_empty_sentences()
        self.clean_identical_sentences()
        ################################################################################################################


        # add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        # via looking for subset sentences
        ################################################################################################################

        # this list would carry the new inferred sentences
        sub_sentences = []
        # this would hold the difference of the counts of subset and the sentence
        count_subset = -1
        # make a copy so I can modify while iterating
        copy_knowledge = copy.deepcopy(self.knowledge)

        # catch the first sentence
        for sentence in copy_knowledge:
            # catch another sentence
            for sentence1 in copy_knowledge:
                # this list would carry the cells resulting from subtracting
                # the subset's cells from the complete sentence's cells
                is_subset = []

                # basically this condition is asking if the cells of SENTENCE
                # is a subset of the SENTENCE1 as that would return
                # an empty set
                if not sentence.cells.difference(sentence1.cells):
                    # subtract cells and counts
                    is_subset = sentence1.cells - sentence.cells
                    count_subset = abs(sentence1.count - sentence.count)

            # now that I have the cells resulting from the above process
            # I will make a deep copy and filter out all the cells that are already in moves_made, safes, mines
            # (even though a shallow copy is enough, I felt deep is safer just in case)
                is_subset0 = copy.deepcopy(is_subset)
                for cell in is_subset0:
                    if cell in self.moves_made or cell in self.safes or cell in self.mines:
                        is_subset.discard(cell)

                # after all that filtering if any cell left then proceed with making the sentence
                if is_subset and count_subset != -1:
                    # the new sentence's cells would be the cells in is_subset and the count would be
                    # the difference of the subset's count and the sentence count as explained in the
                    # "the subset method" at the website of this project
                    new_sentence = Sentence(is_subset, count_subset)

                    # again extra cautious: before appending the sentence
                    # to sub_sentences, make sure it's not already in my KB
                    if new_sentence not in self.knowledge:
                        sub_sentences.append(new_sentence)

        # finally add all resultant sentences to self.knowledge
        for sentence in sub_sentences:
            self.knowledge.append(sentence)
        ################################################################################################################

        # At the very end, do a final cycle of getting, marking, cleaning mines, safes and sentences as there
        # might be some new mines and safes could be marked for the AI to make a safe move!
        ################################################################################################################
        self.mark_mines_safes()
        self.clean_empty_sentences()
        self.clean_identical_sentences()
        self.clean_exceuted_safes()
        ################################################################################################################

    def mark_mines_safes(self):
        """
        this function would check if there is any known mines or safes
        and update self.mines and self.safes.
        """
        for sentence in self.knowledge:
            mines_of_sentence = copy.deepcopy(sentence.known_mines())
            safes_of_sentence = copy.deepcopy(sentence.known_safes())
            if len(mines_of_sentence):
                for cell in mines_of_sentence:
                    self.mark_mine(cell)
                    self.mines.add(cell)
            if len(safes_of_sentence):
                for cell in safes_of_sentence:
                    if cell not in self.moves_made:
                        self.mark_safe(cell)
                        self.safes.add(cell)

    def clean_empty_sentences(self):
        """
        this function clears all empty sentences from
        self.knowledge.
        """
        clone = copy.deepcopy(self.knowledge)
        for sentence in clone:
            if not sentence.cells:
                self.knowledge.remove(sentence)

    def clean_identical_sentences(self):
        """
        this function delete identical sentences in self.knowledge.
        """
        # make a deep copy se I can iterate and alter sentences safely
        clone = copy.deepcopy(self.knowledge)
        # set index to 0
        indx = 0
        # access all sentences in the deep copy
        for sentence in clone:
            # increment the index by one so this sentence ends up
            # being compared to all following (subsequent) sentences not itself.
            indx += 1
            for i in range(indx, len(clone)):
                if sentence == clone[i]:
                    # if it is identical then TRY to remove it just in case
                    # if for some reason it is not eligible then pass without crashing the game
                    try:
                        self.knowledge.remove(sentence)
                    except:
                        pass

    def clean_exceuted_safes(self):
        """
        another cleaning function that would remove all safes
        that was already executed in the board as a move.
        """
        clone = copy.deepcopy(self.safes)
        for cell in clone:
            if cell in self.moves_made:
                self.safes.remove(cell)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made and cell not in self.mines:
                return cell
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # iterate with random range up to the height of the board
        for row in range(random.randrange(self.height)):
            # iterate with random range up to the width of the board
            for col in range(random.randrange(self.width)):
                # checking that the cell (row, col) not already executed or marked as a mine
                if (row, col) not in self.mines and (row, col) not in self.moves_made:
                    return row, col
        return None

    def neighbors(self, cell):
        """
        :param cell: cell (i, j) to find its neighbor within one column and one row
        :return: a list of all (i, j) neighboring cells
        """
        # create an empty cell
        neighboring_cells = []
        # up and down within one row
        for i in range(cell[0] - 1, cell[0] + 2):
            # up and down within one column
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update neighboring_cells list if i, j are not crossing the height and width of the board
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighboring_cells.append((i, j))

        return neighboring_cells




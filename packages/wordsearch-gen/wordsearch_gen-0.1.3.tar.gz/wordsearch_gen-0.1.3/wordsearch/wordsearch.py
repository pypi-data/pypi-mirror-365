from random import shuffle, choice
import copy
from .alphabets import Alphabets

# Directions for placing words: Horizontal, Vertical, and Diagonal
DIRECTIONS = ['H', 'V', 'D']

class WordSearch:
    """
    WordSearch class generates a customizable word search puzzle.
    """
    def __init__(self, words, language=Alphabets.ENGLISH):
        """
        Initializes the WordSearch object, setting the language and grid size,
        and filling the grid with the provided words.

        Args:
            words: List of words to be placed in the grid
            language: The alphabet/language to use for empty cells (default is English)
        """
        # Determine the grid size based on longest word
        self.size = self.calculate(words) 

        # Convert all words to uppercase and sort them by length in descending order
        words = [word.upper() for word in words]
        words.sort(key=len, reverse=True)

        # Initialize an empty grid
        grid = self.make_grid(self.size)

        # Fill the grid with the words
        grid = self.fill_grid(grid, words)
        if grid is False:
            raise Exception('Could not fill grid')  # Raise an error if words do not fit

        # Fill remaining empty spaces with random letters
        grid = self.fill_empty(grid, language=language)

        self.grid = grid


    def make_grid(self, size):
        """
        Creates an empty grid of the given size.

        Args:
            size: desiered size of the grid (an integer)
        
        Return:
            A 2D list representing an empty grid
        """
        return [['' for _ in range(size)] for _ in range(size)]


    def calculate(self, words) -> int:
        """
        Calculates the size of the grid based on the longest word.

        Args:
            words: List of words
        
        Return:
            The grid size (an integer)
        """
        size = self.get_longest_word_len(words)  # Get the length of the longest word

        # Ensure the grid size is at least 10
        if size < 10:
            size = 10
        else:
            size = size + 2  # Add a buffer for better word placement

        return size


    def get_longest_word_len(self, inputArray) -> int:
        """
        Finds the length of the longest word in the list.

        Args:
            inputArray: List of words
        
        Return:
            Length of the longest word as integer
        """
        max_len = 0
        for word in inputArray:
            if len(word) > max_len:
                max_len = len(word)

        return max_len


    def can_fit(self, grid, row, col, word, direction):
        """
        Checks if a word can fit in a given position and direction.

        Args:
            grid: The current grid
            row: Row position to start placing the word
            col: Column position to start placing the word
            word: The word to place
            direction: The direction (Horizontal, Vertical, or Diagonal)

        Returns:
            True if the word can fit, otherwise False
        """
        for i, letter in enumerate(word):
            new_row, new_col = self.move_position(row, col, direction, i)

            # Check if the letter fits in the grid and doesn't overlap with an existing letter
            if letter != grid[new_row][new_col] and grid[new_row][new_col] != '':
                return False

        return True


    def place_word(self, grid, row, col, word, direction):
        """
        Places the word in the grid at the given position and direction.

        Args:
            grid: The current grid
            row: Row position to place the word
            col: Column position to place the word
            word: The word to place
            direction: The direction (Horizontal, Vertical, or Diagonal)
        """
        for i, letter in enumerate(word):
            new_row, new_col = self.move_position(row, col, direction, i)
            grid[new_row][new_col] = letter


    def move_position(self, row, col, direction, i):
        """
        Calculates the new position based on the direction and index.

        Args:
            row: Current row
            col: Current column
            direction: The direction (Horizontal, Vertical, or Diagonal)
            i: Index of the current letter in the word

        Returns:
            The new row and column as a tuple
        """
        if direction == 'H' or direction == 'D':
            col = col + i

        if direction == 'V' or direction == 'D':
            row = row + i

        return row, col


    def fill_grid(self, grid, words, word_index=0):
        """
        Fills the grid with words by trying to place each word in random directions.

        Args:
            grid: The current grid
            words: List of words to place in the grid
            word_index: Index of the current word in the list

        Returns:
            A filled grid or False if placement fails
        """
        shuffled_directions = copy.deepcopy(DIRECTIONS)
        shuffle(shuffled_directions)

        for direction in shuffled_directions:
            for y in self.get_y_positions(words[word_index], direction):
                for x in self.get_x_positions(words[word_index], direction):
                    if self.can_fit(grid, y, x, words[word_index], direction):
                        new_grid = copy.deepcopy(grid)
                        self.place_word(new_grid, y, x, words[word_index], direction)

                        # Recursively place the next word
                        if len(words) == word_index + 1:
                            return new_grid

                        result = self.fill_grid(new_grid, words, word_index + 1)
                        if result is not False:
                            return result

        return False


    def fill_empty(self, grid, language):
        """
        Fills the remaining empty cells in the grid with random letters.

        Args:
            grid: The current grid
            language: The alphabet/language to use for empty cells

        Returns:
            The grid with empty cells filled
        """
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == '':
                    grid[y][x] = choice(language)

        return grid


    def get_y_positions(self, word, direction):
        """
        Determines the possible row positions where a word can be placed.

        Args:
            word: The word to place
            direction: The direction (Horizontal or Vertical)

        Returns:
            List of possible row positions
        """
        if direction == 'H':
            positions = [i for i in range(self.size)]
            shuffle(positions)
            return positions
        else:
            positions = [i for i in range(self.size - len(word) + 1)]
            shuffle(positions)
            return positions


    def get_x_positions(self, word, direction):
        """
        Determines the possible column positions where a word can be placed.

        Args:
            word: The word to place
            direction: The direction (Horizontal or Vertical)

        Returns:
            List of possible column positions
        """
        if direction == 'V':
            positions = [i for i in range(self.size)]
            shuffle(positions)
            return positions
        else:
            positions = [i for i in range(self.size - len(word) + 1)]
            shuffle(positions)
            return positions

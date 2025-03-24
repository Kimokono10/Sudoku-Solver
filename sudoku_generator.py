import random

class SudokuGenerator:
    def __init__(self, level="medium"):
        self.level = level
        self.difficulty = self._set_difficulty()

    def _set_difficulty(self):
        """
        Set the number of cells to remain filled based on the difficulty level.
        """
        if self.level == "easy":
            return 60
        elif self.level == "medium":
            return 40
        elif self.level == "hard":
            return 28

    def generate_board(self):
        """
        Generate a fully solved Sudoku board.
        """
        board = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_board(board)
        return board

    def fill_board(self, board):

        def backtrack(i, j):
            if i == 9:  # If all rows are filled, the board is complete
                return True
            if j == 9:  # Move to the next row if the current row is complete
                return backtrack(i + 1, 0)
            if board[i][j] != 0:  # Skip already filled cells
                return backtrack(i, j + 1)

            random_nums = list(range(1, 10))
            random.shuffle(random_nums)  # Shuffle numbers to introduce randomness
            for num in random_nums:
                if self._is_valid(board, i, j, num):  # Check if placing `num` is valid
                    board[i][j] = num  # Place the number
                    if backtrack(i, j + 1):  # Continue to the next cell
                        return True
                    board[i][j] = 0  # Reset cell on failure
            return False

        backtrack(0, 0)  # Start backtracking from the top-left corner

    def _is_valid(self, board, row, col, num):

        # Check the row and column
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False

        # Check the 3x3 subgrid
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False

        return True

    def remove_numbers(self, board):
        """
        Remove numbers from the solved board to create a puzzle based on difficulty.
        """
        cells_to_remove = 81 - self.difficulty  # Calculate how many cells to remove
        empty_cells = random.sample(range(81), cells_to_remove)  # Randomly select cells
        for idx in empty_cells:
            row, col = divmod(idx, 9)  # Convert 1D index to 2D grid coordinates
            board[row][col] = 0  # Remove the number from the cell
        return board

    def generate_puzzle(self):
        solved_board = self.generate_board()  # Generate a solved board
        puzzle = self.remove_numbers(solved_board)  # Remove numbers to create the puzzle
        return puzzle


if __name__ == "__main__":
    generator = SudokuGenerator(level="medium")
    puzzle = generator.generate_puzzle()
    for row in puzzle:
        print(row)

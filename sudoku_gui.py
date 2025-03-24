import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
from sudoku_csp import *
from sudoku_generator import SudokuGenerator
import time


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.board = [[tk.StringVar() for _ in range(9)] for _ in range(9)]
        self.create_widgets()

    def create_widgets(self):
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=20)

        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.grid_frame, width=2, font=("Arial", 18), justify="center",
                                 textvariable=self.board[i][j])
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.bind("<KeyRelease>", self.validate_input)
                if i % 3 == 0:
                    entry.grid(row=i, column=j, pady=(10, 2))
                if j % 3 == 0:
                    entry.grid(row=i, column=j, padx=(10, 2))

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        tk.Button(self.button_frame, text="Solve", command=self.solve).grid(row=0, column=0, padx=5)
        tk.Button(self.button_frame, text="Clear", command=self.clear_board).grid(row=0, column=1, padx=5)
        tk.Button(self.button_frame, text="Load Test", command=self.load_test_board).grid(row=0, column=2, padx=5)
        tk.Button(self.button_frame, text="Generate Puzzle", command=self.generate_puzzle).grid(row=0, column=3, padx=5)
        tk.Button(self.button_frame, text="Analyze", command=self.analyze).grid(row=0, column=4, padx=5)

        self.difficulty_label = tk.Label(self.button_frame, text="Difficulty:")
        self.difficulty_label.grid(row=0, column=5, padx=5)

        self.difficulty_combo = ttk.Combobox(self.button_frame, values=["easy", "medium", "hard"], state="readonly")
        self.difficulty_combo.set("medium")  # Default difficulty is medium
        self.difficulty_combo.grid(row=0, column=6, padx=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.timer_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.timer_label.pack(pady=10)

    def load_test_board(self):
        test_board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        self.set_board(test_board)

    def generate_puzzle(self):
        difficulty = self.difficulty_combo.get()
        generator = SudokuGenerator(level=difficulty)
        puzzle = generator.generate_puzzle()
        self.set_board(puzzle)

    def get_board(self):
        return [[int(self.board[i][j].get()) if self.board[i][j].get() else 0 for j in range(9)] for i in range(9)]

    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                self.board[i][j].set(str(board[i][j]) if board[i][j] != 0 else "")

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                self.board[i][j].set("")
                entry = self.grid_frame.grid_slaves(row=i, column=j)[0]
                entry.config(bg='white')

    def set_status(self, status):
        self.status_label.config(text=status)

    def validate_input(self, event):
        row, col = event.widget.grid_info()['row'], event.widget.grid_info()['column']
        value = event.widget.get()

        if value and (not value.isdigit() or not (1 <= int(value) <= 9)):
            event.widget.delete(0, tk.END)
            return

        if self.is_invalid(row, col, value):
            event.widget.config(bg='red')
        else:
            event.widget.config(bg='white')

    def is_invalid(self, row, col, value):
        if not value:
            return False

        value = int(value)
        for j in range(9):
            if j != col and self.board[row][j].get() == str(value):
                return True

        for i in range(9):
            if i != row and self.board[i][col].get() == str(value):
                return True

        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.board[i][j].get() == str(value):
                    return True

        return False

    def solve(self):
        board = self.get_board()
        self.set_status("Solving... Please wait.")
        self.root.update()

        start_time = time.perf_counter()
        sudoku_csp = SudokuCSP(board)
        csp_solution = sudoku_csp.solve()

        if csp_solution:
            self.set_board(csp_solution)
            self.set_status("Solved")
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            self.timer_label.config(text=f"Time taken: {elapsed_time:.2f} seconds")
            #sudoku_csp.visualize_ac3()
        else:
            self.set_status("No solution exists!")
            messagebox.showerror("Error", "No solution exists!")


    def analyze(self): #bei generate 3 puzzles lkol wa7ed lkol difficulty then y solve each of them to compare their solving time
        levels = ["easy", "medium", "hard"]
        results = {}

        for level in levels:
            generator = SudokuGenerator(level=level)
            total_time = 0
            puzzle = generator.generate_puzzle()
            sudoku_csp = SudokuCSP(puzzle)
            start_time = time.perf_counter()
            sudoku_csp.solve()
            end_time = time.perf_counter()
            total_time= end_time - start_time
            results[level] = total_time

        self.plot_results(results)

    def plot_results(self, results):
        levels = list(results.keys())
        times = list(results.values())

        plt.figure(figsize=(8, 5))
        plt.bar(levels, times, color=['green', 'blue', 'red'])
        plt.xlabel("Difficulty Level")
        plt.ylabel("Solving Time (seconds)")
        plt.title("Solving Time for Sudoku Difficulty Levels")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

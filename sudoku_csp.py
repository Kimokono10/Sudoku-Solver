import networkx as nx
import matplotlib.pyplot as plt


class SudokuCSP:
    def __init__(self, grid):
        """Initialize the Sudoku CSP solver."""
        self.grid = grid
        self.domains = self.initialize_domains(grid)  # Initialize domains for each cell
        self.arcs = self.generate_arcs()

    def initialize_domains(self, grid):
        """Initialize domains for each cell in the grid."""
        domains = {}
        for i in range(9):  # Iterate through rows
            for j in range(9):  # Iterate through columns
                if grid[i][j] != 0:  # If the cell is pre-filled
                    domains[(i, j)] = {grid[i][j]}  # Domain is the fixed value
                else:  # If the cell is empty
                    domains[(i, j)] = set(range(1, 10))  # Domain is all possible values
        return domains

    def generate_arcs(self):
        """Generate all arcs (constraints) for the Sudoku puzzle."""
        arcs = set()  # Store unique arcs
        all_arcs = []  # Store all arcs for queue

        # Row constraints
        for i in range(9):  # Iterate through rows
            for j in range(9):  # Iterate through columns in the row
                for k in range(j + 1, 9):  # Pair each cell with others in the same row
                    arc = ((i, j), (i, k))
                    if arc not in arcs:  # Avoid duplicates
                        arcs.add(arc)
                        all_arcs.append(arc)
                    reverse_arc = ((i, k), (i, j))  # Include reverse direction
                    if reverse_arc not in arcs:
                        arcs.add(reverse_arc)
                        all_arcs.append(reverse_arc)

        # Column constraints
        for j in range(9):  # Iterate through columns
            for i in range(9):  # Iterate through rows in the column
                for k in range(i + 1, 9):  # Pair each cell with others in the same column
                    arc = ((i, j), (k, j))
                    if arc not in arcs:
                        arcs.add(arc)
                        all_arcs.append(arc)
                    reverse_arc = ((k, j), (i, j))
                    if reverse_arc not in arcs:
                        arcs.add(reverse_arc)
                        all_arcs.append(reverse_arc)

        # Subgrid constraints
        for box_row in range(0, 9, 3):  # Iterate over 3x3 subgrids by rows
            for box_col in range(0, 9, 3):  # Iterate over 3x3 subgrids by columns
                subgrid_cells = [(box_row + r, box_col + c) for r in range(3) for c in range(3)]
                for i in range(len(subgrid_cells)):  # Pair each cell with others in the subgrid
                    for j in range(i + 1, len(subgrid_cells)):
                        arc = (subgrid_cells[i], subgrid_cells[j])
                        if arc not in arcs:
                            arcs.add(arc)
                            all_arcs.append(arc)
                        reverse_arc = (subgrid_cells[j], subgrid_cells[i])
                        if reverse_arc not in arcs:
                            arcs.add(reverse_arc)
                            all_arcs.append(reverse_arc)

        return all_arcs

    def revise(self, Xi, Xj):
        """Revise the domain of Xi based on the constraint with Xj."""
        revised = False
        removed_values = []
        for x in list(self.domains[Xi]):  # Iterate through values in Xi's domain
            if not any(x != y for y in self.domains[Xj]):  # Check if no value in Xj satisfies the constraint
                removed_values.append(x)

        for value in removed_values:  # Remove inconsistent values
            self.domains[Xi].remove(value)
            print(f"Removed {value} from domain of {Xi} due to constraint with {Xj}.")
            revised = True

        return revised

    def arc_consistency(self):
        """Enforce arc consistency using the AC-3 algorithm."""
        queue = self.arcs[:]  # Initialize the queue with all arcs
        while queue:
            (Xi, Xj) = queue.pop(0)  # Dequeue an arc
            print(f"Processing arc ({Xi}, {Xj})...")
            if self.revise(Xi, Xj):  # If a revision is made
                print(f"Domain of {Xi} reduced to {self.domains[Xi]}.")
                if not self.domains[Xi]:  # If a domain is empty
                    print(f"Domain of {Xi} became empty. No solution possible.")
                    return False  # Inconsistency found

                self.update_grid_from_domains()  # Update the grid with singleton domains

                for Xk, _ in filter(lambda arc: arc[1] == Xi, self.arcs):  # Add affected neighbors to the queue
                    if (Xk, Xi) not in queue:
                        queue.append((Xk, Xi))
            print(f"Current domains: {self.domains}\n")

        return True

    def update_grid_from_domains(self):
        """Update the Sudoku grid with values from singleton domains."""
        for (i, j), domain in self.domains.items():
            if len(domain) == 1:  # If a domain has one value, update the grid
                self.grid[i][j] = list(domain)[0]

    def solve(self):
        """Solve the Sudoku puzzle."""
        if not self.arc_consistency():  # Apply AC-3 to enforce arc consistency
            return None
        if self.is_solved():  # Check if the puzzle is solved
            self.update_grid_from_domains()  # Update the grid
            return self.grid
        else:
            return self.backtrack()  # Use backtracking if necessary

    def is_solved(self):
        """Check if the Sudoku is solved."""
        return all(len(self.domains[(i, j)]) == 1 for i in range(9) for j in range(9))

    def backtrack(self):
        """Solve the puzzle using backtracking search."""
        empty_cell = self.find_empty_cell()  # Find the next empty cell
        if not empty_cell:  # If no empty cells remain
            return self.grid

        row, col = empty_cell
        for num in sorted(self.domains[(row, col)]):  # Try each value in the domain
            self.grid[row][col] = num  # Assign a value
            if self.is_valid(row, col):  # Check if the assignment is valid
                result = self.backtrack()  # Recursively solve
                if result:  # If solved
                    return result
            self.grid[row][col] = 0  # Reset the cell

        return None

    def find_empty_cell(self):
        """Find the next empty cell in the grid."""
        for i in range(9):  # Iterate through rows
            for j in range(9):  # Iterate through columns
                if self.grid[i][j] == 0:  # If the cell is empty
                    return (i, j)
        return None

    def is_valid(self, row, col):
        """Check if a cell's value is valid."""
        value = self.grid[row][col]

        # Check row
        if any(self.grid[row][j] == value and j != col for j in range(9)):
            return False

        # Check column
        if any(self.grid[i][col] == value and i != row for i in range(9)):
            return False

        # Check 3x3 subgrid
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i][j] == value and (i, j) != (row, col):
                    return False

        return True

    def visualize_ac3(self):
        """Visualize the constraint graph after applying AC-3."""
        G = nx.Graph()
        for variable in self.domains.keys():  # Add nodes with labels
            if not self.domains[variable]:
                G.add_node(variable, label=f"{variable}\n∅", node_color='red')
            else:
                G.add_node(variable, label=f"{variable}\n{self.domains[variable]}")

        for (Xi, Xj) in self.arcs:  # Add edges for constraints
            domain_i = self.domains[Xi]
            domain_j = self.domains[Xj]
            if any(d1 == d2 for d1 in domain_i for d2 in domain_j):
                G.add_edge(Xi, Xj)

        pos = {k: (k[1], -k[0]) for k in self.domains.keys()}  # Position nodes by their grid coordinates
        plt.figure(figsize=(8, 6))
        nx.draw(
            G,
            pos,
            with_labels=False,
            node_size=800,
            node_color="lightgreen",
            font_size=10,
            font_weight="bold",
        )
        labels = nx.get_node_attributes(G, "label")
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

        plt.title("AC-3 Visualization")
        plt.show()

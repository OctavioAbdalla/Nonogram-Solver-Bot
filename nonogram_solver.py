class NonogramSolver:
    def __init__(self):
        self.board_size = 15
        self.puzzle = []
        self.clues = []
    
    def reset_values(self):
        self.puzzle = []
        self.clues = [] 
      
    def solve_puzzle(self, clues):
        self.clues = clues
        for _ in range(self.board_size):
            self.puzzle.append([0] * self.board_size)
        
        result = self.insert_possibility()
        result = self.puzzle_to_string(result)
        return result

    def generate_combinations(self, clue, empty_spaces=None):
        if empty_spaces == None: 
            empty_spaces = self.board_size
        
        if len(clue) == 0:
            return [['X'] * empty_spaces]

        first_hint = clue[0]
        remaining_hints = clue[1:]

        combinations = []

        if remaining_hints:
            separator = 1
        else:
            separator = 0

        for i in range(empty_spaces - first_hint + 1):
            current_combination = ['X'] * i + ['O'] * first_hint

            if len(remaining_hints) > 0:
                current_combination += ['X']

            sub_combinations = self.generate_combinations(remaining_hints, empty_spaces - i - separator - first_hint)

            for sub_combination in sub_combinations:
                combinations.append(current_combination + sub_combination)

        return combinations

    def verify_puzzle(self):
        for col in range(self.board_size):
            puzzle_column = [self.puzzle[i][col] for i in range(self.board_size) if self.puzzle[i][col] != 0]
            possibilities = self.generate_combinations(self.clues[col])
            possibilities = [possibility[:len(puzzle_column)] for possibility in possibilities]

            if puzzle_column not in possibilities:
                return False

        return True

    def insert_possibility(self):
        for index, _ in enumerate(self.puzzle):
            if self.puzzle[index][0] == 0:
                possibilities = self.generate_combinations(self.clues[index + self.board_size])

                for possibility in possibilities:
                    self.puzzle[index] = possibility

                    if self.verify_puzzle():
                        result = self.insert_possibility()
                        if result:
                            return result
                else:
                    self.puzzle[index] = [0] * self.board_size
                    return False

        return self.puzzle

    def puzzle_to_string(self, puzzle):
        result = ''

        for line in puzzle:
            for item in line:
                result += item
            result += '\n'
        
        self.reset_values()
        return result

    


# clues = [[1], [8, 3], [2, 1, 4, 2], [1, 6, 1], [1, 1, 4, 2], [13], [1, 3], [1, 2, 3], [1, 2, 3], [1, 6, 3], [1, 6, 5], [1, 2, 3, 1], [1, 2, 2, 1], [1, 3, 2], [9, 3], 
# [8], [4, 1], [2, 1, 2, 1], [1, 1, 2, 1], [1, 1, 6, 1], [5, 6, 1], [1, 1, 1, 2, 1], [1, 1, 1, 2, 1], [5, 1], [15], [12], [2, 8, 2], [1, 1, 1, 1], [2, 2, 1, 2], [3, 3]]

# solver = NonogramSolver()
# print(solver.solve_puzzle(clues))


# Wave Function Collapse Algorithm
# Author: Nathan Strong
# Date: April 4, 2022
# Description: Runs the wave function collapse
# algorithm (look it up idk) to solve sudoku puzzles

import copy
import random

class square(list[int]):
    def __init__(self, allowed_vals:list[int]) -> None:
        self.extend(allowed_vals)
        self.solved = len(self)==1
    
    def __eq__(self, __o: object) -> bool:
        if type(__o) == int:
            if self.solved:
                return self[0] == __o
            else:
                return False
        else:
            raise Exception(f"Can't check equality between square and {type(__o)}")
    
    def __ne__(self, __o: object) -> bool:
        return not (self == __o)

class board(list[list[square]]):
    def __init__(self, known:list[list[int]]=None) -> None:
        """known: 9x9 grid with -1 for each unknown element"""
        self.clear()
        for y in range(9):
            self.append([square([i for i in range(1,10) if (known[y][x] in (i, -1))]) for x in range(9)])
        self.propagate()
    
    def __str__(self) -> str:
        """Print out the whole board in a legible format"""
        string_lines = ["-"*73]
        for line in self:
            for i in range(3):
                string_line = "|"
                for sqr in line:
                    string_line = string_line + " "
                    for j in range(3):
                        string_line = f"{string_line}{i*3+j+1 if i*3+j+1 in sqr else ('_' if sqr.solved else ' ')} "
                    string_line = string_line[:-1]+" |"
                string_lines.append(string_line)
            string_lines.append("-"*73)
        return "\n".join(string_lines)
    
    def isvalid(self, x:int, y:int, num:int) -> bool:
        """Tests if a certain number is valid in a certain position"""
        for cx in range(9):
            for cy in range(9):
                if num != self[cy][cx] or (cx == x and cy == y):
                    continue
                if cx == x or cy == y:
                    return False
                if cx//3 == x//3 and cy//3 == y//3:
                    return False
        return True
    
    def issolved(self):
        """Tests if the current board is completely solved"""
        for x in range(9):
            for y in range(9):
                if not self[y][x].solved:
                    return False
        return True
    
    def iterate(self):
        """Performs one 'move' on the board (marks one square),
        then checks to see how that affects the others"""
        # Find the easiest square to solve (the one with the fewest options that isn't already solved)
        lowest_entropy = (-1, -1, 10000)
        for x in range(9):
            for y in range(9):
                if len(self[y][x]) < lowest_entropy[2] and not self[y][x].solved:
                    lowest_entropy = (x, y, len(self[y][x]))
        sqr = self[lowest_entropy[1]][lowest_entropy[0]]
        
        # Check to see if that square has no options (if it does, there's been a problem)
        if len(sqr) == 0:
            print(self)
            raise Exception(f"No options for square at {lowest_entropy[:-1]}")
        
        # Solve that square, then return its position, the chosen value, and the removed ones
        l = list(lowest_entropy[:-1])
        l.reverse()
        print(f"Solving at {l}")
        val = random.choice(sqr)
        print(f"Chose {val}, {'had options' if len(sqr)>1 else 'only choice'}")
        sqr_copy = copy.copy(sqr)
        sqr_copy.remove(val)
        sqr.clear()
        sqr.append(val)
        sqr.solved = True

        return (lowest_entropy[0], lowest_entropy[1], val, sqr_copy)
    
    def propagate(self):
        """Checks which numbers in the grid are no longer valid and removes them"""
        removed = []
        for x in range(9):
            for y in range(9):
                sqr = self[y][x]
                sqr_copy = copy.copy(sqr)
                for num in sqr_copy:
                    if not self.isvalid(x, y, num):
                        sqr.remove(num)
                        removed.append((x, y, num))
        return removed
    
    def solve(self):
        iter = 0
        changestack = []
        while not self.issolved():
            iter += 1
            print(f"Iteration #{iter}")

            iter_res = self.iterate()
            prop_res = self.propagate()
            changestack.append((iter_res, prop_res))

            # Weird-looking list comprehension thing to check for any zeros
            while len([row for row in self if len([itm for itm in row if len(itm)==0])]) != 0:
                # There's a zero space, backtrack
                print("Zero detected, removing incorrect choice")
                last_iter, last_prop = changestack.pop()
                print(f"Choice was {last_iter[2]} at ({last_iter[0]},{last_iter[1]})")
                # Fix iteration
                self[last_iter[1]][last_iter[0]] = square(last_iter[3])
                self[last_iter[1]][last_iter[0]].solved = False
                # Fix propagation
                for rem in last_prop:
                    self[rem[1]][rem[0]].append(rem[2])


def main():
    board_arr = [
        [ 5,  3, -1, -1,  7, -1, -1, -1, -1],
        [ 6, -1, -1,  1,  9,  5, -1, -1, -1],
        [-1,  9,  8, -1, -1, -1, -1,  6, -1],
        [ 8, -1, -1, -1,  6, -1, -1, -1,  3],
        [ 4, -1, -1,  8, -1,  3, -1, -1,  1],
        [ 7, -1, -1, -1,  2, -1, -1, -1,  6],
        [-1,  6, -1, -1, -1, -1,  2,  8, -1],
        [-1, -1, -1,  4,  1,  9, -1, -1,  5],
        [-1, -1, -1, -1,  8, -1, -1,  7,  9],
    ]
    #board_arr = [[-1 for i in range(9)] for j in range(9)]
    b = board()#board_arr)
    b.solve()
    print(b)

if __name__ == "__main__":
    main()
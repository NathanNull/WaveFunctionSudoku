# Wave Function Collapse Algorithm
# Author: Nathan Strong
# Date: April 4, 2022
# Description: A class that creates/solves a
# board using the wave function collapse algorithm

import copy
import math
import random
import abc
from typing import Generic, TypeVar

class possibility(abc.ABC):
    @abc.abstractmethod
    def isvalid(self, x:int, y:int, board:"board") -> bool:
        pass
    @abc.abstractmethod
    def aschar(self) -> str:
        pass

TPoss = TypeVar("TPoss", bound=possibility)
class square(Generic[TPoss], list[TPoss]):
    def __init__(self, allowed_vals:list[TPoss]) -> None:
        self.extend(allowed_vals)
        self.solved = len(self)==1
        try:
            self.allowed_type = type(allowed_vals[0])
        except:
            self.allowed_type = None
    
    def __eq__(self, __o: object) -> bool:
        if self.allowed_type in (type(__o), None):
            if self.solved:
                return self[0] == __o
            else:
                return False
        else:
            raise Exception(f"Can't check equality between square and {type(__o)}")
    
    def __ne__(self, __o: object) -> bool:
        return not (self == __o)

class board(list[list[square[TPoss]]]):
    def __init__(self, allowed:list[TPoss], known:list[list[TPoss]]=None, size:tuple[int,int]=(4,6)) -> None:
        """known: grid with -1 for each unknown element\n
        size: dimensions of the grid (x, y), use if grid is all unknown"""
        self.allowed = allowed

        if known == None:
            known = [[-1 for _ in range(size[0])] for _ in range(size[1])]
        else:
            size = (len(known[0]), len(known))
        self.size = size

        self.clear()
        for y in range(size[1]):
            self.append([square[TPoss]([itm for itm in allowed if (known[y][x] in (itm, -1))]) for x in range(size[0])])
        self.propagate()
    
    def __str__(self) -> str:
        """Print out the whole board in a legible format"""
        gridsize = math.ceil(math.sqrt(len(self.allowed)))
        num_dashes = ((gridsize+1)*2*self.size[0])+1
        string_lines = ["-"*num_dashes]
        for line in self:
            for i in range(gridsize):
                string_line = "|"
                for sqr in line:
                    string_line = string_line + " "
                    for j in range(gridsize):
                        # Selects character based on whether solved, possible, or ruled out
                        idx = i*gridsize+j
                        string_line = f"{string_line}\
{self.allowed[idx].aschar() if len(self.allowed)>idx and self.allowed[idx] in sqr else ('_' if sqr.solved else ' ')} "
                    string_line = string_line[:-1]+" |"
                string_lines.append(string_line)
            string_lines.append("-"*num_dashes)
        return "\n".join(string_lines)
    
    def __format__(self, __format_spec: str) -> str:
        if __format_spec == "compact":
            lines = []
            for line in self:
                l = ""
                for sqr in line:
                    l = l+(sqr[0].aschar() if sqr.solved else "?")
                lines.append(l)
            return "\n".join(lines)
        else:
            return str(self)
    
    def isvalid(self, x:int, y:int, num:int) -> bool:
        """Tests if a certain number is valid in a certain position"""
        for cx in range(self.size):
            for cy in range(self.size):
                # Number's different or it's the same square, so move on
                if num != self[cy][cx] or (cx == x and cy == y):
                    continue
                # On same row/col
                if cx == x or cy == y:
                    return False
                # In same box
                if cx//self.gridsize == x//self.gridsize and cy//self.gridsize == y//self.gridsize:
                    return False
        return True
    
    def issolved(self) -> bool:
        """Tests if the current board is completely solved"""
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if not self[y][x].solved:
                    return False
        return True
    
    def iterate(self, verbose:bool=False) -> tuple[int, int, TPoss, list[TPoss]]:
        """Performs one 'move' on the board (marks one square),
        then checks to see how that affects the others"""
        # Find the easiest square to solve (the one with the fewest options that isn't already solved)
        lowest_entropy = (-1, -1, 10000)
        for x in range(self.size[0]):
            for y in range(self.size[1]):
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
        if verbose:
            print(f"Solving at {l}")
        val = random.choice(sqr)
        if verbose:
            print(f"Chose {val.aschar()}, {'had options' if len(sqr)>1 else 'only choice'}")
        sqr_copy = copy.copy(sqr)
        sqr_copy.remove(val)
        sqr.clear()
        sqr.append(val)
        sqr.solved = True

        return (lowest_entropy[0], lowest_entropy[1], val, sqr_copy)
    
    def propagate(self) -> list[tuple[int, int, TPoss]]:
        """Checks which numbers in the grid are no longer valid and removes them"""
        removed = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                sqr = self[y][x]
                sqr_copy = copy.copy(sqr)
                for num in sqr_copy:
                    if not num.isvalid(x, y, self):
                        sqr.remove(num)
                        removed.append((x, y, num))
        return removed
    
    def solve(self, verbose:bool=False) -> None:
        # Make a backup in case we get stuck
        original = copy.deepcopy(self)

        # Try to solve it 3 times
        for _ in range(3):
            iter = 0
            changestack:list[tuple[tuple[int, int, TPoss, list[TPoss]],list[tuple[int, int, TPoss]]]] = []
            # As long as the board isn't solved and the iteration limit isn't reached...
            while (not self.issolved()) and iter<self.size[0]*self.size[1]*2:
                iter += 1
                if verbose:
                    print(f"Iteration #{iter}")

                # Iterate and remember the changes that were made
                iter_res = self.iterate(verbose)
                prop_res = self.propagate()
                changestack.append((iter_res, prop_res))

                # Weird-looking list comprehension thing to check for any zeros
                while len([row for row in self if len([itm for itm in row if len(itm)==0])]) != 0:
                    # There's a zero space, backtrack
                    if verbose:
                        print("Zero detected, removing incorrect choice")
                    last_iter, last_prop = changestack.pop()
                    if verbose:
                        print(f"Choice was {last_iter[2].aschar()} at ({last_iter[0]},{last_iter[1]})")
                    # Fix iteration
                    self[last_iter[1]][last_iter[0]] = square(last_iter[3])
                    self[last_iter[1]][last_iter[0]].solved = False
                    # Fix propagation
                    for rem in last_prop:
                        self[rem[1]][rem[0]].append(rem[2])
            if self.issolved():
                return
            
            # Hopefully, HOPEFULLY, this part will never be relevant. If it is, something's gone wrong.
            if verbose:
                print("Failed, trying again")
            self.clear()
            self.extend(copy.deepcopy(original))
        # Even more hopefully, this will never trigger. When it does, I probably won't know what to do about it.
        raise Exception("Houston, we have a problem. (Couldn't solve the board after 3 tries)")

if __name__ == "__main__":
    raise Exception("Hey, don't run this, it's a library! Run example.py instead.")
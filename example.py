# Wave Function Collapse Example
# Author: Nathan Strong
# Date: May 1, 2022
# Description: An example of the library in use

import wavefunction as wf

digits = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class exm(wf.possibility):
    def __init__(self, name):
        self.name = str(name)
        self.range = 3
    def isvalid(self, x, y, board:wf.board):
        # Essentially, no squares within a 3-cell radius can be the same.
        for cx in range(x-self.range, x+self.range+1):
            for cy in range(y-self.range, y+self.range+1):
                if cx<0 or cy<0 or cx>=board.size[0] or cy>=board.size[1]:
                    continue
                if cx==x and cy==y:
                    continue
                csqr = board[cy][cx]
                if csqr == self:
                    return False
        return True
    def aschar(self):
        return self.name

allowed = [exm(digits[i]) for i in range(25)]
b = wf.board[exm](allowed, size=(10, 10))
b.solve(True)
print(f"{b:compact}")
print(b)
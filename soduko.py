import copy
n = 9 #this is an assumption, this can not be currently changed.
# empty matrix (for copying over the filled one and refilling)
board = [[[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],

         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],

         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         [[ ],[ ],[ ],  [ ],[ ],[ ],  [ ],[ ],[ ],],
         ]
board = [[[ ],[1],[ ],  [6],[ ],[ ],  [3],[ ],[ ],],
         [[5],[ ],[ ],  [ ],[3],[ ],  [ ],[1],[8],],
         [[ ],[2],[ ],  [5],[ ],[ ],  [ ],[ ],[ ],],

         [[3],[ ],[ ],  [ ],[ ],[ ],  [ ],[2],[ ],],
         [[ ],[ ],[ ],  [7],[ ],[4],  [ ],[ ],[ ],],
         [[ ],[9],[ ],  [ ],[ ],[ ],  [ ],[ ],[7],],

         [[ ],[ ],[ ],  [ ],[ ],[6],  [ ],[7],[ ],],
         [[1],[5],[ ],  [ ],[9],[ ],  [ ],[ ],[2],],
         [[ ],[ ],[6],  [ ],[ ],[3],  [ ],[5],[ ],],
         ]

guess_count = 0

class EmptyCell(Exception):
    pass

class SodukoSolver:
    def __init__(self):
        self.did_something = False
        # fill needed optional values in cells:
        for i in range(n):
            for j in range(n):
                if len(board[i][j]) < 1:
                    board[i][j] = list(range(1,n+1))

    def remove(self,row,col,val):
        if val in board[row][col]:
            board[row][col].remove(val)
            if len(board[row][col]) == 1:
                self.reduce(row,col)
            if len(board[row][col]) < 1:
                raise EmptyCell()

    def check_section(self,row,col,section_name):
        indexMethod = getattr(self,'get_indexes_in_' + section_name)
        for val in range(n):
            count = 0
            idx = (-1,-1)
            notSingle = False
            for cell in indexMethod(row,col):
                if val in board[cell[0]][cell[1]]:
                    if len(board[cell[0]][cell[1]]) > 1:
                        count = count + 1
                        idx = (cell[0],cell[1])
                        notSingle = True
                    else:
                        break
            if count == 1 and notSingle:
                board[idx[0]][idx[1]] = [val]
                self.reduce(idx[0],idx[1])

    def reduce_row(self,row,col):
        for i in range(n):
            if i != col:
                self.remove(row,i,board[row][col][0])

    def reduce_col(self,row,col):
        for i in range(n):
            if i != row:
                self.remove(i,col,board[row][col][0])

    def reduce_block(self,row,col):
        for cell in self.get_indexes_in_block(row,col):
            if cell[0] != row or cell[1] != col:
                self.remove(cell[0],cell[1],board[row][col][0])
    
    def get_indexes_in_block(self,row,col):
        start_row = int(row/3)*3
        start_col = int(col/3)*3
        return [(start_row+x,start_col+y) for x in range(3) for y in range(3)]

    def get_indexes_in_row(self,row,col):
        return [(row,x) for x in range(9)]

    def get_indexes_in_col(self,row,col):
        return [(x,col) for x in range(9)]

    def solve(self):
        # initial pass:
        try:
            for row in range(n):
                for col in range(n):
                    if len(board[row][col]) == 1:
                        self.reduce(row,col)
            # now look deeper:
            self.check()
        except EmptyCell:
            print("impossible board!")
            return False
        # now guess:
        if not self.done():
            if not self.recurse(0,0):
                print("impossible board!")
        return True


    def recurse(self,row,col):
        global board
        global guess_count
        # if no work to be done in this cell:
        if len(board[row][col]) == 1:
            return self.recurse(row+int((col+1)/n),(col+1)%9)
        firstSnapShot = copy.deepcopy(board) # to revert to in case we completely fail
        while len(board[row][col]) > 0:
            snapshot = copy.deepcopy(board) # to not forget what we learned between iterations in this cell.

            #first, make a guess, see what happens:
            if len(board[row][col]) > 1:
                guess_count += 1
                board[row][col] = [board[row][col][0]] # try the current first item in the list
            try:
                self.reduce(row,col)
                self.check()
            except EmptyCell: # if the first item can't be chosen, remove it from the list
                board = copy.deepcopy(snapshot)
                try:
                    self.remove(row,col,board[row][col][0])
                    self.check()
                    continue
                except EmptyCell:
                    # if the first item can't be chosen, and can't be removed, then return False.
                    board = copy.deepcopy(firstSnapShot)
                    return False

            # if the guess passed the reduce and check phases, we can recurse on:
            if not self.done() and not self.recurse(row+int((col+1)/n),(col+1)%9):
                board = copy.deepcopy(snapshot)
                try:
                    self.remove(row,col,board[row][col][0])
                    self.check()
                except EmptyCell:
                    board = copy.deepcopy(firstSnapShot)
                    return False
            else: # were either done or recurse() returned True
                return True
        board = copy.deepcopy(firstSnapShot)
        return False

    def reduce(self,row,col):
        self.did_something = True
        self.reduce_row(row,col)
        self.reduce_col(row,col)
        self.reduce_block(row,col)

    def check(self):
        while not self.done() and self.did_something:
            self.did_something = False
            for row in range(n):
                self.check_section(row, 0, "row")
            for col in range(n):
                self.check_section(0,col,"col")
            for row in range(int(n/3)):
                for col in range(int(n/3)):
                    self.check_section(row*3,col*3,"block")

    def done(self):
        for row in range(n):
            for col in range(n):
                if len(board[row][col]) != 1:
                    return False
        return True

for row in range(n):
    print(board[row])
print("\n")

sd = SodukoSolver()
if sd.solve():
    for row in range(n):
        print(board[row])
print("guess count is: " + str(guess_count))
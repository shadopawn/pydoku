from Tkinter import *                
import tkFileDialog                         
import tkMessageBox                         
import tkFont                               
from abc import ABCMeta, abstractmethod 
from copy import copy
import sys, os, random, getopt, re

class Subject(object):
    def attach(self, o):
        self.observers.append(o)
        
    def detach(self, o):
        self.observers.remove(o)
        
    def notify(self):
        for o in self.observers:
            o.update()
        
    def __init__(self):
        self.observers = list()
        pass
    
class Observer(object):
    @abstractmethod
    def update(self):
        pass
        
    def __init__(self):
        pass
    
class GridWindow(Observer):
    def __init__(self, master, gui, rows, cols, rowOffset = 0, colOffset = 0, rowHeight = 40, colWidth = 40, squareColourInFocus = "LightGray", squareColourOutFocus = "White", dividerWidth = 3):
        super(GridWindow, self).__init__()
        self.subject = gui
        self.subject = gui
        self.rows = rows
        self.cols = cols
        self.rowOffset = rowOffset
        self.colOffset = colOffset
        self.rowHeight = rowHeight
        self.colWidth  = colWidth
        
        self.squareColourInFocus = squareColourInFocus
        self.squareColourOutFocus = squareColourOutFocus
        
        self.dividerWidth = dividerWidth
        
        self.master = master
        self.window = Toplevel(master)
        self.window.title("("+str(rowOffset)+","+str(colOffset)+")")
        
        self.window.bind("<Button-1>", self.onClick)
        self.window.bind("<Key>", self.onKey)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        
        self.canvas = Canvas(self.window, width=cols*self.colWidth+2, height=rows*self.rowHeight+2)
        self.canvas.pack()
        self.rectangle = {}
        self.text = {}
        self.focus = None 
        self.clearkey = [65, 22, 36]
        
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                self.rectangle[(row, col)] = self.canvas.create_rectangle(2+colWidth*col, 2+rowHeight*row, 2+colWidth*(col+1), 2+rowHeight*(row+1), fill="White")
                if self.subject.state.state[(self.rowOffset+row,self.colOffset+col)]==0:
                    textt=str()
                else:
                    textt=str(self.subject.state.state[(row+self.rowOffset,col+self.colOffset)])
        
                if self.subject.state.isFixed((row+self.rowOffset,col+self.colOffset)): 
                    font1 = ('Segoe UI', 11, 'bold') 
                    self.text[(row, col)] = self.canvas.create_text(2+colWidth*(col+0.5), 2+rowHeight*(row+0.5), text=textt, font=font1) 
                else: 
                    self.text[(row, col)] = self.canvas.create_text(2+colWidth*(col+0.5), 2+rowHeight*(row+0.5), text=textt)

        
    def setNumber(self, location, number):
        itemId = self.text[location]
        self.canvas.itemconfigure(itemId, text=number)
        newLoc = (location[0]+self.rowOffset,location[1]+self.colOffset)
        self.subject.enterValue(newLoc, number)
        
    def setColour(self, location, colour):
        itemId = self.rectangle[location]
        self.canvas.itemconfigure(itemId, fill=colour)
        
    def onClick(self, event):
        row = (event.y - 2) / self.rowHeight
        col = (event.x - 2) / self.colWidth

        if row >= 0 and row < self.rows and col >= 0 and col < self.cols and not self.subject.state.isFixed((row+self.rowOffset,col+self.colOffset)):
            if (self.focus != None):
                self.setColour(self.focus, self.squareColourOutFocus)
            self.focus = (row, col)
            self.setColour(self.focus, self.squareColourInFocus)
        
    def onKey(self, event):
        if self.focus != None:
            if "123456789".find(event.char) != -1:
                newValue = event.char
            elif event.keycode in self.clearkey:
                newValue = ""
            else:
                return

            self.setNumber(self.focus, newValue)
        
    def onClose(self):
        self.window.destroy()
        self.subject.detach(self)
        
    def update(self):
        newState = self.subject.getState()
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if newState.state[(self.rowOffset+row,self.colOffset+col)]==0:
                    textt=str()
                else:
                    textt=str(newState.state[(row+self.rowOffset,col+self.colOffset)])
                itemId = self.text[(row, col)]

                if self.subject.state.isFixed((row+self.rowOffset,col+self.colOffset)):
                    font1 = ('Segoe UI', 11, 'bold') 
                    self.canvas.itemconfigure(itemId, text=textt, font=font1) 
                else: 
                    self.canvas.itemconfigure(itemId, text=textt)

        if self.focus != None:
            self.setColour(self.focus, self.squareColourOutFocus)
            self.focus = None
        
    
class BlockWindow(GridWindow):
    def __init__(self, master, gui, rowOffset, colOffset):
        GridWindow.__init__(self, master, gui, 3, 3, rowOffset, colOffset)
        
    
class ColWindow(GridWindow):
    def __init__(self, master, gui, rowOffset, colOffset):
        GridWindow.__init__(self, master, gui, 9, 1, rowOffset, colOffset)
        
    
class MainWindow(GridWindow):
    def __init__(self, master, gui):
        GridWindow.__init__(self, master,gui, 9,9)
        self.subject.attach(self)
        for i in range(0,2):
            self.canvas.create_line(2+3*self.colWidth*(i+1), 2, 2+3*self.colWidth*(i+1), 2+9*self.rowHeight, width=self.dividerWidth)
            self.canvas.create_line(2, 2+3*self.rowHeight*(i+1), 2+9*self.colWidth, 2+3*self.rowHeight*(i+1), width=self.dividerWidth)
        
    
class RowWindow(GridWindow):
    def __init__(self, master, gui, rowOffset, colOffset):
        GridWindow.__init__(self, master, gui, 1, 9, rowOffset, colOffset)
        
    
class Command(object):
    @abstractmethod
    def execute(self):
        pass
        
    @abstractmethod
    def undo(self):
        pass
        
    @abstractmethod
    def redo(self):
        pass
        
    def __init__(self):
        pass
    
class Element(object):
    def accept(self, v):
        pass
        
    def __init__(self):
        pass
    
class EnterValueCommand(Command):
    def __init__(self, boardState, loc, num):
        self.receiver = boardState
        self.location = loc 
        self.number = num
        self.oldVal = None
        
    def execute(self):
        self.oldVal = self.receiver.state[self.location]
        self.receiver.state[self.location] = self.number
        
    def undo(self):
        self.receiver.state[self.location] = self.oldVal
        
    def redo(self):
        self.receiver.state[self.location] = self.number
        
    
class LoadCommand(Command):
    def __init__(self, boardState, fileName):
        self.receiver = boardState
        self.fileName = fileName
        
    def execute(self):
        self.oldState = copy(self.receiver.state)
        self.oldOriginalPuzzle = copy(self.receiver.originalPuzzle)
        self.receiver.accept(LoadVisitor(self.fileName))
        
    def undo(self):
        self.receiver.state = copy(self.oldState)
        self.receiver.originalPuzzle = copy(self.oldOriginalPuzzle)
        
    def redo(self):
        self.execute()
        
    
class SaveCommand(Command):
    def __init__(self, boardState, fileName):
        self.receiver = boardState
        self.fileName = fileName
        
    def execute(self):
        self.receiver.accept(SaveVisitor(self.fileName))
        
    
class Visitor(object):
    def visitSudokuBoardState(self, sbs):
        pass
        
    def __init__(self):
        pass
    
class LoadVisitor(Visitor):
    def __init__(self, fileName):
        self.fileName = fileName
        
    def visitSudokuBoardState(self, sbs):
        f = open(self.fileName, 'r')
        data = f.readline().strip()
        data2 = f.readline().strip()
        f.close()
        row = 0
        col = 0
        for c in data:
            sbs.state[(row,col)]=int(c)
            col=col+1
            if col==9:
                col=0
                row=row+1
        row = 0
        col = 0
        for c in data2:
            sbs.originalPuzzle[(row,col)]=int(c)
            col=col+1
            if col==9:
                col=0
                row=row+1

    
class SaveVisitor(Visitor):
    def __init__(self, fileName):
        self.fileName = fileName
        
    def visitSudokuBoardState(self, sbs):
        f = open(self.fileName,'w')
        for row in range(9):
            for col in range(9):
                f.write(str(sbs.state[(row,col)]))
        f.write("\n")
        for row in range(9):
            for col in range(9):
                f.write(str(sbs.originalPuzzle[(row,col)]))
        f.close()
        
    
class SudokuEngine(object):
    def __init__(self, sbs):
        self.boardState = sbs
        
    def hasSolution(self):
        current = []
        for row in xrange(9):
            for col in xrange(9):
                if self.boardState.state[(row,col)] != 0:
                    current.append(int(self.boardState.state[(row,col)])-int(1))
                else:
                    current.append(None)

        if self.solveboard(current)[1] == None:
            return False
        return True
        
    def solve(self):
        current = []
        for row in xrange(9):
            for col in xrange(9):
                if self.boardState.state[(row,col)] != 0:
                    current.append(int(self.boardState.state[(row,col)])-int(1))
                else:
                    current.append(None)
        self.currentSolution = self.solveboard(current)[1]
        for i in xrange(81):
            self.boardState.state[(self.axisfor(i,0),self.axisfor(i,1))] = self.currentSolution[i]+1
        
    def generate(self):
        self.currentSolution = self.solveboard([None]*81)[1]
        self.currentGenerated = self.makepuzzle(self.currentSolution)
        for i in xrange(81):
            if self.currentGenerated[i] != None:
                self.boardState.state[(self.axisfor(i,0),self.axisfor(i,1))] = self.currentGenerated[i]+1
            else:
                self.boardState.state[(self.axisfor(i,0),self.axisfor(i,1))] = 0
        
    def makepuzzle(self, board):
        puzzle = []; deduced = [None] * 81
        order = random.sample(xrange(81), 81)
        for pos in order:
            if deduced[pos] is None:
                puzzle.append((pos, board[pos]))
                deduced[pos] = board[pos]
                self.deduce(deduced)
        random.shuffle(puzzle)
        for i in xrange(len(puzzle) - 1, -1, -1):
            e = puzzle[i]; del puzzle[i]
            rating = self.checkpuzzle(self.boardforentries(puzzle), board)
            if rating == -1: puzzle.append(e)
        return self.boardforentries(puzzle)
        
    def ratepuzzle(self, puzzle, samples):
        total = 0
        for i in xrange(samples):
            state, answer = self.solveboard(puzzle)
            if answer is None: return -1
            total += len(state)
        return float(total) / samples
        
    def checkpuzzle(self, puzzle, board = None):
        state, answer = self.solveboard(puzzle)
        if answer is None: return -1
        if board is not None and not self.boardmatches(board, answer): return -1
        difficulty = len(state)
        state, second = self.solvenext(state)
        if second is not None: return -1
        return difficulty
        
    def solveboard(self, original):
        board = list(original)
        guesses = self.deduce(board)
        if guesses is None: return ([], board)
        track = [(guesses, 0, board)]
        return self.solvenext(track)
        
    def solvenext(self, remembered):
        while len(remembered) > 0:
            guesses, c, board = remembered.pop()
            if c >= len(guesses): continue
            remembered.append((guesses, c + 1, board))
            workspace = list(board)
            pos, n = guesses[c]
            workspace[pos] = n
            guesses = self.deduce(workspace)
            if guesses is None: return (remembered, workspace)
            remembered.append((guesses, 0, workspace))
        return ([], None)
        
    def deduce(self, board):
        while True:
            stuck, guess, count = True, None, 0
            # fill in any spots determined by direct conflicts
            allowed, needed = self.figurebits(board)
            for pos in xrange(81):
                if None == board[pos]:
                    numbers = self.listbits(allowed[pos])
                    if len(numbers) == 0: return []
                    elif len(numbers) == 1: board[pos] = numbers[0]; stuck = False
                    elif stuck:
                        guess, count = self.pickbetter(guess, count, [(pos, n) for n in numbers])
            if not stuck: allowed, needed = self.figurebits(board)
            # fill in any spots determined by elimination of other locations
            for axis in xrange(3):
                for x in xrange(9):
                    numbers = self.listbits(needed[axis * 9 + x])
                    for n in numbers:
                        bit = 1 << n
                        spots = []
                        for y in xrange(9):
                            pos = self.posfor(x, y, axis)
                            if allowed[pos] & bit: spots.append(pos)
                        if len(spots) == 0: return []
                        elif len(spots) == 1: board[spots[0]] = n; stuck = False
                        elif stuck:
                            guess, count = self.pickbetter(guess, count, [(pos, n) for pos in spots])
            if stuck:
                if guess is not None: random.shuffle(guess)
                return guess
        
    def figurebits(self, board):
        allowed, needed = [e is None and 511 or 0 for e in board], []
        for axis in xrange(3):
            for x in xrange(9):
                bits = self.axismissing(board, x, axis)
                needed.append(bits)
                for y in xrange(9):
                    allowed[self.posfor(x, y, axis)] &= bits
        return allowed, needed
        
    def posfor(self, x, y, axis = 0):
        if axis == 0: return x * 9 + y
        elif axis == 1: return y * 9 + x
        else: return ((0,3,6,27,30,33,54,57,60)[x] + (0,1,2,9,10,11,18,19,20)[y])
        
    def axisfor(self, pos, axis):
        if axis == 0: return pos / 9
        elif axis == 1: return pos % 9
        else: return (pos / 27) * 3 + (pos / 3) % 3
        
    def axismissing(self, board, x, axis):
        bits = 0
        for y in xrange(9):
            e = board[self.posfor(x, y, axis)]
            if e is not None: bits |= 1 << e
        return 511 ^ bits
        
    def listbits(self, bits):
        return [y for y in xrange(9) if 0 != bits & 1 << y]
        
    def allowed(self, board, pos):
        bits = 511
        for axis in xrange(3):
            x = self.axisfor(pos, axis)
            bits &= self.axismissing(board, x, axis)
        return bits
        
    def pickbetter(self, b, c, t):
        if b is None or len(t) < len(b): return (t, 1)
        if len(t) > len(b): return (b, c)
        if random.randint(0, c) == 0: return (t, c + 1)
        else: return (b, c + 1)
        
    def entriesforboard(self, board):
        return [(pos, board[pos]) for pos in xrange(81) if board[pos] is not None]
        
    def boardforentries(self, entries):
        board = [None] * 81
        for pos, n in entries: board[pos] = n
        return board
        
    def boardmatches(self, b1, b2):
        for i in xrange(81):
            if b1[i] != b2[i]: return False
        return True
        
    
class SudokuBoardState(Element):
    def __init__(self):
        self.engine = SudokuEngine(self)
        self.state = {}
        for row in range(9):
            for col in range(9):
                self.state[(row,col)] = 0
        self.originalPuzzle = copy(self.state)
        
    def __str__(self):
        strRepr = ""
        for row in range(9):
            for col in range(9):
                strRepr += " "+str(self.state[(row,col)])
            strRepr += "\n"
        return strRepr
        
    def accept(self, v):
        v.visitSudokuBoardState(self)
        
    def generate(self):
        self.engine.generate()
        self.originalPuzzle = copy(self.state)
        
    def solve(self):
        self.engine.solve()
        
    def hasSolution(self):
        return self.engine.hasSolution()
        
    def isFixed(self, loc):
        if self.originalPuzzle[loc] != 0:
            return True
        return False
        
    def isFinished(self):
        for row in range(9):
            for col in range(9):
                if self.state[(row,col)] == 0:
                    return False
        return True
        
    
class SudokuGUI(Subject):
    def __init__(self, master):
        self.undoCommandList = list()
        self.state = SudokuBoardState()
        self.redoCommandList = list()
        Subject.__init__(self)
        
        self.warningStatus = IntVar()
        
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.onQuit)
        
        frame = Frame(master)
        
        fileFrame = Frame(frame, borderwidth=5)
        self.btn_load = Button(fileFrame, width=15, text="Load from File", command=self.load)
        self.btn_load.config(state="active")
        self.btn_load.pack()
        self.btn_saveAs = Button(fileFrame, width=15, text="Save As", command=self.saveAs)
        self.btn_saveAs.config(state="active")
        self.btn_saveAs.pack()
        self.btn_save = Button(fileFrame, width=15, text="Save", command=self.save)
        self.btn_save.config(state="disabled") 
        self.btn_save.pack()
        self.btn_generate = Button(fileFrame, width=15, text="Generate", command=self.generate)
        self.btn_generate.config(state="active")
        self.btn_generate.pack()
        self.chkbtn_warnings = Checkbutton(fileFrame, text = "Warnings", variable = self.warningStatus, onvalue = 1, offvalue = 0, height=1, width = 15)
        self.chkbtn_warnings.pack()
        fileFrame.pack() 
        
        undoFrame = Frame(frame, borderwidth=5)  
        self.btn_undo = Button(undoFrame, width=15, text="Undo", command=self.undo) 
        self.btn_undo.pack() 
        self.btn_redo = Button(undoFrame, width=15, text="Redo", command=self.redo) 
        self.btn_redo.pack() 
        self.btn_undo_since_error = Button(undoFrame, width=15, text="Undo since error", command=self.undo_last_error) 
        self.btn_undo_since_error.pack() 
        undoFrame.pack() 
        
        topFrame = Frame(frame, borderwidth=5) 
        self.btn_open = Button(topFrame, width=15, text="Open Full Board", command=self.open_main_board) 
        self.btn_open.pack() 
        topFrame.pack() 
        
        blockFrame = Frame(frame, borderwidth=5) 
        
        frame_label = Frame(blockFrame) 
        label = Label(frame_label, text="Open Block Windows") 
        label.pack() 
        frame_label.pack() 
        
        frame_buttons = Frame(blockFrame) 
        self.btn_open_block1 = Button(frame_buttons, text="(1,1)", command= lambda : self.open_block_board(0,0) ) 
        self.btn_open_block1.grid(row=0, column=0) 
        self.btn_open_block2 = Button(frame_buttons, text="(1,2)", command= lambda : self.open_block_board(0,3) ) 
        self.btn_open_block2.grid(row=0, column=1) 
        self.btn_open_block3 = Button(frame_buttons, text="(1,3)", command= lambda : self.open_block_board(0,6) ) 
        self.btn_open_block3.grid(row=0, column=2) 
        self.btn_open_block4 = Button(frame_buttons, text="(2,1)", command= lambda : self.open_block_board(3,0) ) 
        self.btn_open_block4.grid(row=1, column=0) 
        self.btn_open_block5 = Button(frame_buttons, text="(2,2)", command= lambda : self.open_block_board(3,3) ) 
        self.btn_open_block5.grid(row=1, column=1) 
        self.btn_open_block6 = Button(frame_buttons, text="(2,3)", command= lambda : self.open_block_board(3,6) ) 
        self.btn_open_block6.grid(row=1, column=2) 
        self.btn_open_block7 = Button(frame_buttons, text="(3,1)", command= lambda : self.open_block_board(6,0) ) 
        self.btn_open_block7.grid(row=2, column=0) 
        self.btn_open_block8 = Button(frame_buttons, text="(3,2)", command= lambda : self.open_block_board(6,3) ) 
        self.btn_open_block8.grid(row=2, column=1) 
        self.btn_open_block9 = Button(frame_buttons, text="(3,3)", command= lambda : self.open_block_board(6,6) ) 
        self.btn_open_block9.grid(row=2, column=2) 
        frame_buttons.pack() 
        
        blockFrame.pack() 
        
        rowFrame = Frame(frame, borderwidth=5) 
        
        frame_label = Frame(rowFrame) 
        label = Label(frame_label, text="Open Row Windows") 
        label.pack() 
        frame_label.pack() 
        
        frame_buttons = Frame(rowFrame) 
        self.btn_open_block1 = Button(frame_buttons, text=" 1 ", command= lambda : self.open_row_board(0,0) ) 
        self.btn_open_block1.grid(row=0, column=0) 
        self.btn_open_block2 = Button(frame_buttons, text=" 2 ", command= lambda : self.open_row_board(1,0) ) 
        self.btn_open_block2.grid(row=0, column=1) 
        self.btn_open_block3 = Button(frame_buttons, text=" 3 ", command= lambda : self.open_row_board(2,0) ) 
        self.btn_open_block3.grid(row=0, column=2) 
        self.btn_open_block4 = Button(frame_buttons, text=" 4 ", command= lambda : self.open_row_board(3,0) ) 
        self.btn_open_block4.grid(row=1, column=0) 
        self.btn_open_block5 = Button(frame_buttons, text=" 5 ", command= lambda : self.open_row_board(4,0) ) 
        self.btn_open_block5.grid(row=1, column=1) 
        self.btn_open_block6 = Button(frame_buttons, text=" 6 ", command= lambda : self.open_row_board(5,0) ) 
        self.btn_open_block6.grid(row=1, column=2) 
        self.btn_open_block7 = Button(frame_buttons, text=" 7 ", command= lambda : self.open_row_board(6,0) ) 
        self.btn_open_block7.grid(row=2, column=0) 
        self.btn_open_block8 = Button(frame_buttons, text=" 8 ", command= lambda : self.open_row_board(7,0) ) 
        self.btn_open_block8.grid(row=2, column=1) 
        self.btn_open_block9 = Button(frame_buttons, text=" 9 ", command= lambda : self.open_row_board(8,0) ) 
        self.btn_open_block9.grid(row=2, column=2) 
        frame_buttons.pack() 
        
        rowFrame.pack() 
        
        colFrame = Frame(frame, borderwidth=5) 
        
        frame_label = Frame(colFrame) 
        label = Label(frame_label, text="Open Column Windows") 
        label.pack() 
        frame_label.pack() 
        
        frame_buttons = Frame(colFrame) 
        self.btn_open_block1 = Button(frame_buttons, text=" 1 ", command= lambda : self.open_col_board(0,0) ) 
        self.btn_open_block1.grid(row=0, column=0) 
        self.btn_open_block2 = Button(frame_buttons, text=" 2 ", command= lambda : self.open_col_board(0,1) ) 
        self.btn_open_block2.grid(row=0, column=1) 
        self.btn_open_block3 = Button(frame_buttons, text=" 3 ", command= lambda : self.open_col_board(0,2) ) 
        self.btn_open_block3.grid(row=0, column=2) 
        self.btn_open_block4 = Button(frame_buttons, text=" 4 ", command= lambda : self.open_col_board(0,3) ) 
        self.btn_open_block4.grid(row=1, column=0) 
        self.btn_open_block5 = Button(frame_buttons, text=" 5 ", command= lambda : self.open_col_board(0,4) ) 
        self.btn_open_block5.grid(row=1, column=1) 
        self.btn_open_block6 = Button(frame_buttons, text=" 6 ", command= lambda : self.open_col_board(0,5) ) 
        self.btn_open_block6.grid(row=1, column=2) 
        self.btn_open_block7 = Button(frame_buttons, text=" 7 ", command= lambda : self.open_col_board(0,6) ) 
        self.btn_open_block7.grid(row=2, column=0) 
        self.btn_open_block8 = Button(frame_buttons, text=" 8 ", command= lambda : self.open_col_board(0,7) ) 
        self.btn_open_block8.grid(row=2, column=1) 
        self.btn_open_block9 = Button(frame_buttons, text=" 9 ", command= lambda : self.open_col_board(0,8) ) 
        self.btn_open_block9.grid(row=2, column=2) 
        frame_buttons.pack() 
        
        colFrame.pack() 
        
        bottomFrame = Frame(frame, borderwidth=5) 
        self.btn_quit = Button(bottomFrame, text="Quit", command=self.quit) 
        self.btn_quit.pack() 
        bottomFrame.pack() 
        
        frame.pack() 
        
    def enterValue(self, loc, num):
        newCommand = EnterValueCommand(self.state, loc, num)
        newCommand.execute()
        self.notify()
        
        violation = False
        vioList = []
        for i in range(9):
            if i!=loc[0] and int(self.state.state[(i,loc[1])])==int(num):
                vioList.append("column")
                violation = True
                break

        for i in range(9):    
            if i!=loc[1] and int(self.state.state[(loc[0],i)])==int(num):
                vioList.append("row")
                violation = True
                break

        for row in range(3):
            for col in range(3):
                if loc!=(loc[0]-loc[0]%3+row,loc[1]-loc[1]%3+col) and int(self.state.state[(loc[0]-loc[0]%3+row,loc[1]-loc[1]%3+col)])==int(num):
                    vioList.append("block")
                    violation = True
                    break

        if violation==True:
            vioText = "There is same number in that "
            for i in range(len(vioList)):
                if len(vioList)>1 and i==len(vioList)-1:
                    vioText = vioText + " and " + vioList[i]
                elif i==0:
                    vioText = vioText + vioList[i]
                else:
                    vioText = vioText + ", " +vioList[i]
            tkMessageBox.showinfo("Violation", vioText+"!")
            
            newCommand.undo()
            self.notify()
        else:
            
            if self.warningStatus.get()==1 and not self.state.hasSolution():
                tkMessageBox.showinfo("Warning", "This number will not lead to a solution!\nYou can undo it or you can undo until last successful board state with Undo Since Error button!\n\nYou can toggle this warning by warnings checkbox!")
            
            if self.state.isFinished():
                tkMessageBox.showinfo("Congratulations!", "Congratulations, you have finished the game!")

            self.undoCommandList.append(newCommand)
            del self.redoCommandList[:]
        
    def open_main_board(self):
        newWindow = MainWindow(self.master, self)
        
    def open_block_board(self, rowOffset, colOffset):
        newWindow = BlockWindow(self.master, self, rowOffset, colOffset)
        
    def open_row_board(self, rowOffset, colOffset):
        newWindow = RowWindow(self.master, self, rowOffset, colOffset)
        
    def open_col_board(self, rowOffset, colOffset):
        newWindow = ColWindow(self.master, self, rowOffset, colOffset)
        
    def load(self):
        fileName = tkFileDialog.askopenfilename(defaultextension=".sdk",filetypes=[("Sudoku", "*.sdk"),("All", "*")])

        if False:
            tkMessageBox.showwarning("Load", "Unable to load the file")
        else:
            self.__lastFileName = fileName
            self.btn_save.config(state="active")
            newCommand = LoadCommand(self.state, fileName)
            newCommand.execute()
            self.undoCommandList.append(newCommand)
            self.notify()
            del self.redoCommandList[:]
        
    def saveAs(self):
        fileName = tkFileDialog.asksaveasfilename(defaultextension=".sdk",filetypes=[("Sudoku", "*.sdk"),("All", "*")])
        if False:
            tkMessageBox.showwarning("Save As", "Unable to create the file")
        else:
            self.__lastFileName = fileName
            self.btn_save.config(state="active")
            newCommand = SaveCommand(self.state, fileName)
            newCommand.execute()
        
    def save(self):
        newCommand = SaveCommand(self.state, self.__lastFileName)
        newCommand.execute()
        
    def redo(self):
        if len(self.redoCommandList)!=0:
            tempCommand = self.redoCommandList.pop()
            tempCommand.redo()
            self.undoCommandList.append(tempCommand)
            self.notify()
        
    def undo(self):
        if len(self.undoCommandList)!=0:
            tempCommand = self.undoCommandList.pop()
            tempCommand.undo()
            self.redoCommandList.append(tempCommand)
            self.notify()
        
    def undo_last_error(self):
        if len(self.undoCommandList)!=0:
        	while(not self.state.hasSolution()):
        		tempCommand = self.undoCommandList.pop()
        		tempCommand.undo()
        		self.redoCommandList.append(tempCommand)
        		if len(self.undoCommandList)==0:
        			tkMessageBox.showinfo("No commands left!", "This board has no solution from beginning!")
        			break
        	self.notify()
        
    def quit(self):
        self.master.destroy()
        
    def onQuit(self):
        self.master.destroy()
        
    def getState(self):
        return self.state
        
    def generate(self):
        self.state.generate()
        self.notify()
        del self.undoCommandList[:]
        del self.redoCommandList[:]


if __name__ == "__main__":
	root = Tk()
	sudokuGui = SudokuGUI(root)

	root.title('Pydoku')
	root.mainloop()
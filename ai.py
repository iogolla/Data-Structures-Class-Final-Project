from random import randint
from players import *
from pathfinder import *

class InvalidRequestException(Exception):
    pass

class AISquirrel(Squirrel):
    def __init__(self, coordinate, board):
        super(Squirrel, self).__init__(coordinate, board)
        self.nuts = 0
        self.pic = pygame.image.load(os.path.join("imgs/squirrelright.png"))
        self.priority = Priority.player
        super().setSpeed((0,0))
        self.tileType = "squirrel"
        self.aiTicks = 0
        self.STONESPEED = 8

    # Turn *off* the ability to set a speed.
    def setSpeed(self,speed):
        return

    # Don't do anything!
    def handleEvent(self,ev):
        return

    # Every half second, the squirrel gets 1 more fuel
    def clockTick(self,fps,num):
        self.aiTicks += num
        if (self.aiTicks > 5):
            self.board.state.incrementFuel(3)
            self.aiTicks -= 5

    def getHealthPacks(self):
        self.board.state.decrementFuel(20)
        x = []
        for hpack in self.board.healthpacks:
            x.append((hpack.getX(),hpack.getY()))
        return x

    def getStones(self):
        x = []
        for stone in self.board.stones:
            x.append((stone.getX(), stone.getY()))
        return x

    def getFerrets(self):
        self.board.state.decrementFuel(5)
        x = []
        for ferret in self.board.ferrets:
            if ferret.hp > 0:
                x.append((ferret.getX(),ferret.getY()))
        return x

    def getExit(self):
        self.board.state.decrementFuel(30)
        return (self.board.endTile.getX(),self.board.endTile.getY())

    def abs(self,x):
        if (x < 0): return -x
        return x

    # Uses |x| + |y| fuel
    def move(self,x,y):
        print('at move')
        if (x < -1 or x > 1 or y < -1 or y > 1):
            print("here1")
            raise InvalidRequestException()
        if self.canMoveTo(self.getX() + x, self.getY() + y):
            super().move(x,y)
            self.board.state.decrementFuel(self.abs(x) + self.abs(y))
        else:
            print("here2")
            raise InvalidRequestException()

    # Where x & y are in the range of integers [-1,1]
    def fireStone(self,x,y):
        if (x < -1 or x > 1 or y < -1 or y > 1):
            raise InvalidRequestException()
        
        startingTile = (self.getX()+x,
                        self.getY()+y)

        movementVector = [x,y]

        # Make sure we're not trying to, shoot at something we can't,
        # e.g., a wall.
        if (self.canMoveTo(startingTile[0], startingTile[1])):
            stone = Stone(startingTile,self.board)
            stone.setPosition(startingTile[0], startingTile[1])
            stone.setSpeed((movementVector[0] * self.STONESPEED,
                            movementVector[1] * self.STONESPEED))
            self.board.addTile(stone)
            self.board.registerForClockTick(stone)
            self.board.state.decrementFuel((self.abs(x) + self.abs(y)) * 3)
        else:
            raise InvalidRequestException()

class MyAISquirrel(AISquirrel):

    def __init__(self, coordinate, board):
        super().__init__(coordinate, board)
        self.myTicks = 0
        self.setSpeed((0,0))
        self.exitPosition = None
        self.healthPack = None

    # Get the current fuel
    def getFuel(self):
        return self.board.state.getFuel()

    # You may call this method as often as you like: it does not use
    # any fuel.
    def canMove(self,x,y):
        print((self.getX() + x, self.getY() + y))
        return self.canMoveTo(self.getX() + x, self.getY() + y)

    # Use this method to move in any direction one tile. This will use
    # |x| + |y| fuel (i.e., if you call it with (-1, 1) it will use 2)
    def move(self,x,y):
        super().move(x,y)

    # Where x,y are in the range [-1,1] (integers)
    # Uses (|x| + |y|) * 3 fuel
    def fireStone(self,x,y):
        super().fireStone(x,y)

    # Gets the position of all stones on the board
    # 
    # Uses 0 fuel each time it is called
    def getStones(self):
        return super().getStones()

    # Gets the position of all ferrets (which will change!)
    # 
    # Uses 5 fuel each time it is called
    def getFerrets(self):
        return super().getFerrets()

    # Gets the position of the exit tile (nut)
    # 
    # Uses 30 fuel
    def getHealthPacks(self):
        return super().getHealthPacks()
        
    def contains(self, lst, x):
        return x in lst

    # Implement the main logic for your AI here. You may not
    # manipulate the other tiles on the board directly: this will be
    # considered cheating. Similarly, you may not manipulate the fuel
    # directly.
    # 
    # Every half second, you will receive 3 more fuel. This is
    # implemented in the parent class's clockTick (which, again, you
    # may not change).
    def clockTick(self,fps,num):
        super().clockTick(fps,num)
        pf = PathFinder(self.board, self)
        
        if self.myTicks < 1:
            # assign the getHealthPacks method to the healthPack attribute 
            if self.healthPack == None:
                self.healthPack = self.getHealthPacks()[0] 
            print("My health pack is here:", self.healthPack)
            #find the path to the healthPack
            healthpath = (pf.findPath(self.healthPack))
            #print the path
            print (healthpath)
            #if the path to the healthPath is valid move to the healthPack
            if healthpath != False:
                self.move(healthpath[1][0],healthpath[2][1])
        #update the number of ticks
        self.myTicks += 1 
        
        
                
        if self.getFuel() > 60:   
            #Just want to see the level of the fuel     
            print ("My fuel is", self.getFuel())
            #assign the getExit method to the exitPosition attribute to prevent it from
            #deducting 30 fuel every time the fuel is > 60
            if self.exitPosition == None: 
                self.exitPosition = self.getExit()
            print("My exit position is", self.exitPosition)
            #find the path to the exit 
            path = (pf.findPath(self.exitPosition))
            print("My path is:", path)
            #if the path to the exit is valid move toward the exit
            if path != False:
                #if the squirrel changes direction and starts moving up,
                #make it to start firing stones up and diagonally toward the northwest
                #direction
                if path[1][0] == 0 and path[1][1] == -1:
                    self.fireStone(0,-1)
                    self.fireStone(1,-1)
                #move toward the exit
                self.move(path[1][0],path[1][1])
                    
        
        #if self.getFuel() > 70:
         #   print ("My fuel is", self.getFuel())


from marioagent import MarioAgent
import numpy as np
class AStar(MarioAgent):

	action = None
	actionStr = None
	KEY_JUMP = 3
	KEY_SPEED = 4
	KEY_RIGHT = 1
	KEY_LEFT = 0
	KEY_DUCK = 2
	levelscene = None
	mayMarioJump = None
	isMarioOnGround = None
	marioFloats = None
	enemiesFloats = None
	isEpisodeOver = False
	marioState = None
	enemiesscene = None
	bigj = 0 #Makes jumps bigger (holds key down longer)
	scene = []  #level scene+enemies scene
	
	trueJumpCounter = 0;
	trueSpeedCounter = 0;

	"""default values for observation details"""
	receptiveFieldWidth = 19
	receptiveFieldHeight = 19
	marioEgoRow = 9
	marioEgoCol = 9

	agentName = "A* Search?"
	
	
	def reset(self):
		self.isEpisodeOver = False
		self.trueJumpCounter = 0;
		self.trueSpeedCounter = 0;
		
	def __init__(self):
		"""Constructor"""
		self.trueJumpCounter = 0
		self.trueSpeedCounter = 0
		self.action = [0, 0, 0, 0, 0, 0]
		self.actionStr = ""
		self.agentName = "A Star Agent"

	def getReceptiveFieldCellValue(self, x, y):
		if (x < 0 or x >= self.marioEgoRow or y < 0 or y >= self.marioEgoCol):
			return 0
		return self.levelself.scene[x][y]
		
	def setObservationDetails(self, rfWidth, rfHeight, egoRow, egoCol):
		self.receptiveFieldWidth = rfWidth
		self.receptiveFieldHeight = rfHeight
		self.marioEgoRow = egoRow;
		self.marioEgoCol = egoCol;
		
	def giveIntermediateReward(self, reward):
		pass
	
	def getTarget(self):
		last = []
		
		#Seeks out mushrooms only. Fire flowers are too hard as he can get stuck trying to get them.
		for row in self.scene:
			if 2 in row:
				if [self.scene.index(row),row.index(2)] != [9,9]:
					return [self.scene.index(row),row.index(2)] #seek out mushrooms.
			last.append(row[18])
		row = 0
		
		#No mushrooms? Just head right then.
		for element in last:
			if element == 0 and (self.scene[row+1][18]==0 or self.scene[row][17] ==0):
				return [row,18]
			row+=1
		return [9,9]

	def search(self):
		#1. merge level and enemies self.scene
		self.scene = []
		for x in range(len(self.levelscene)):
			temp = []
			for y in range(len(self.levelscene[x])):
				temp.append(self.levelscene[x][y]+self.enemiesscene[x][y]) #possible danger zone when enemies get stuck in bricks due to level gen. 
			self.scene.append(temp)
		
		#2. Initilize A* 
		closed = []
		open = [[9,9]]
		
		start = [9,9]
		target = self.getTarget() 
		
		camefrom = np.zeros((19,19,2))
		h = np.zeros((19,19))
		g = np.zeros((19,19))
		f = np.zeros((19,19))		

		f[start[0]][start[1]] = g[start[0]][start[1]] + h[start[0]][start[1]]
				
		#3. A* Search
		while len(open) > 0:

			#Get node in open with the lowest f_score
			tmin = 9999 #temp min
			for x in open:
				if f[x[0]][x[1]] < tmin:
					current = [x[0],x[1]]
					tmin = f[x[0]][x[1]]

			if current == target:
				return self.rebuildPath(camefrom,current)
					
			#neighborhood is the 8 cells surrounding the current cell
			neighborhood = [[current[0],current[1]+1], \
							[current[0]+1,current[1]], \
							[current[0]+1,current[1]+1],\
							[current[0]-1,current[1]+1],\
							[current[0]-1,current[1]],\
							[current[0]-1,current[1]-1],\
							[current[0],current[1]-1],\
							[current[0]+1,current[1]-1]]
			
			
			#Remove nodes that form barriers of some description
			for node in neighborhood[:]:
				removed = 0
				if node[1] > 18 or node[0] > 18 or node[1] < 0 or node[0] < 0:
					closed.append(node)	

			#add the current node to the "searched" nodes
			open.remove(current)
			closed.append(current)
					
			#Scan neighborhood for next best candidate
			for node in neighborhood:
				if node in closed:
					continue
					
				temp_g_score = g[node[0]][node[1]]+((current[0] - node[0])**2 + (current[1] - node[1])**2)**0.5
						
				if node not in open:
					open.append(node)
					h[node[0]][node[1]] = ((target[0] - node[0])**2 + (target[1] - node[1])**2)**0.5
					update_g = True
				elif temp_g_score < g[node[0]][node[1]]:
					update_g = True
				else:
					update_g = False
							
				if update_g:
					camefrom[node[0]][node[1]] = current
					g[node[0]][node[1]] = temp_g_score
					f[node[0]][node[1]] = temp_g_score+h[node[0]][node[1]]

	#Returns the best direction to head in
	def rebuildPath(self,camefrom,current):
		new = [int(camefrom[current[0]][current[1]][0]),int(camefrom[current[0]][current[1]][1])];
		prev = [9,10] 
		while new != [9,9]:
			prev = new
			new = [int(camefrom[current[0]][current[1]][0]),int(camefrom[current[0]][current[1]][1])]
			current = new
		return prev
	
	def getAction(self):
		direction = self.search()
		
		if direction[0] == 8 and (self.mayMarioJump or not self.isMarioOnGround or self.bigj < 4):
			self.bigj +=1
			self.action[self.KEY_JUMP] = 1
			self.action[self.KEY_SPEED] = 1
		else:
			self.bigj = 0
			self.action[self.KEY_JUMP] = 0
			self.action[self.KEY_SPEED] = 0

		if direction[1] == 10:
			self.action[self.KEY_RIGHT] = 1
		else:
			self.action[self.KEY_RIGHT] = 0
		
		if direction[1] == 8:
			self.action[self.KEY_LEFT] = 1
		else:
			self.action[self.KEY_LEFT] = 0
		
		return self.action
		
	def getName(self):
		return self.agentName

	def integrateObservation(self, squashedObservation, squashedEnemies, marioPos, enemiesPos, marioState):
		
		row = self.receptiveFieldHeight
		col = self.receptiveFieldWidth
		levelscene=[]
		enemiesObservation=[]
		
		for i in range(row):
			levelscene.append(squashedObservation[i*col:i*col+col])

		
		for i in range(row):
			enemiesObservation.append(squashedEnemies[i*col:i*col+col])
		
		self.enemiesscene = enemiesObservation
		self.marioFloats = marioPos
		self.enemiesFloats = enemiesPos
		self.mayMarioJump = marioState[3]
		self.isMarioOnGround = marioState[2]
		self.marioState = marioState[1]
		self.levelscene = levelscene

	def printLevelscene(self):
		ret = ""
		for x in range(self.receptiveFieldWidth):
			tmpData = ""
			for y in range(self.receptiveFieldHeight):
				tmpData += self.mapElToStr(self.getReceptiveFieldCellValue(x, y));
			ret += "\n%s" % tmpData;
		print ret

	def printenvobv(self):
		for x in self.levelself.scene:
			print x
		for x in self.enemiesself.scene:
			print x
			
	def mapElToStr(self, el):
		"""maps element of levelself.scene to str representation"""
		s = "";
		if  (el == 0):
			s = "##"
		s += "#MM#" if (el == 95) else str(el)
		while (len(s) < 4):
			s += "#";
		return s + " "

	def printObs(self):
		"""for debug"""
		print repr(self.observation)

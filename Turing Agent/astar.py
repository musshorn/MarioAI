from marioagent import MarioAgent
import numpy as np
import math
class AStarAgent(MarioAgent):


	action = None
	actionStr = None
	KEY_JUMP = 3
	KEY_SPEED = 4
	KEY_RIGHT = 1
	KEY_LEFT = 0
	KEY_DUCK = 2
	levelScene = None
	mayMarioJump = None
	isMarioOnGround = None
	marioFloats = None
	enemiesFloats = None
	isEpisodeOver = False
	marioState = None
	enemiesScene = None
	scene = []#enemies+enviroment on the same map
	visited = []#list of positions we've been
	return_punish = 2 #punishment for returning to visited nodes, just has to be bigger than sqrt(2) to be effective
	bigj = 0 #makes jumps bigger?
	
	last_target =[] #list of last moves. used to detect if mario gets stuck between 2 paths to a target
	marioLastX = [] #Last X position mario was at. Used to detect stuckness
	
	trueJumpCounter = 0;
	trueSpeedCounter = 0;
	oldpos = 0
	
	"""default values for observation details"""
	receptiveFieldWidth = 19
	receptiveFieldHeight = 19
	marioEgoRow = 9
	marioEgoCol = 9

	agentName = "A* Search"
	
	
	def reset(self):
		self.isEpisodeOver = False
		self.trueJumpCounter = 0;
		self.trueSpeedCounter = 0;
		scene = []#enemies+enviroment on the same map
		visited = []#list of positions we've been

	def __init__(self):
		"""Constructor"""
		self.trueJumpCounter = 0
		self.trueSpeedCounter = 0
		self.action = [0, 0, 0, 0, 0, 0]
		self.actionStr = ""
		self.agentName = "A* Search"

	def getReceptiveFieldCellValue(self, x, y):
		if (x < 0 or x >= self.marioEgoRow or y < 0 or y >= self.marioEgoCol):
			return 0
		return self.levelScene[x][y]
		
	def setObservationDetails(self, rfWidth, rfHeight, egoRow, egoCol):
		self.receptiveFieldWidth = rfWidth
		self.receptiveFieldHeight = rfHeight
		self.marioEgoRow = egoRow;
		self.marioEgoCol = egoCol;
		
	def giveIntermediateReward(self, reward):
		pass
	
	def getTarget(self):
		target = []
		last = []

		#Returns values in order of priority. End of level>fireflower>mushroom=coin
		flowers = []
		coins = []
		for row in self.scene:
			for column in row:
				if self.scene.index(row) >=5: #max jump height
					if column == 5:
						target.append([8,10])
					elif column == 3:
						target.append([self.scene.index(row),row.index(column)])
					elif column == 2:
						target.append([self.scene.index(row),row.index(column)])
					elif column == 1:
						target.append([self.scene.index(row),row.index(column)])

		for row in self.scene:
			last.append(row[18])
	
		x = 7 #Set lower to make him more jumpy
		while x >0:
			if last[x] == 0:
				target.append([x,18])
			x-=1

		#Find closest target
		closest = 99999
		closest_id = [0,18]

		for x in target:
			dist = ((x[0]-9)**2+(x[1]-9)**2)**.5
			if dist<closest:
				closest = dist
				closest_id = x


		return closest_id
		

	def search(self):
		#1. merge level and enemies self.scene
		self.scene = []
		for x in range(len(self.levelScene)):
			temp = []
			for y in range(len(self.levelScene[x])):
				temp.append(self.levelScene[x][y]+self.enemiesScene[x][y]) #possible danger zone when enemies get stuck in bricks due to level gen. 
			self.scene.append(temp)
		
		#Update punishable nodes list (this is nodes we've visited previously)
		#Attempting to print list of bad nodes to visit.
		index = -1
		shift = self.visited[-1]
		distx = abs(shift[0]-9)
		disty = abs(shift[1]-9)
		p = shift
		out = []
		while p[0]-distx >= 0 and p[1]-disty>=0 and -1*index < len(self.visited):#i think this is cool. Check back later
			index -=1
			if p[0]-distx >= 0 and p[0]-distx < 19 and p[1]-disty>=0 and  p[1]-disty< 19:
				out.append([p[0]-distx,p[1]-disty])
			p = self.visited[index]

			
		#2. Initilize A* 
		closed = []
		open = [[9,9]]
		
		start = [9,9]
		target = self.getTarget()
	
		camefrom = np.zeros((19,19,2))
		camefrom[9][9] = [9,9]
		h = np.zeros((19,19))
		g = np.zeros((19,19))
		f = np.zeros((19,19))		
		
		f[start[0]][start[1]] = g[start[0]][start[1]] + h[start[0]][start[1]]
		
		#Add the visited nodes to the distance list
		for x in out:
		    	g[x[0]][x[1]] = self.return_punish

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
							[current[0]-1,current[1]],\
							[current[0],current[1]-1]]


			#Remove nodes that form barriers of some description			
			for node in neighborhood[:]:
				if node[1] > 18 or node[0] > 18 or node[1] < 0 or node[0] < 0:
					closed.append(node)
				elif self.scene[node[0]][node[1]] in [-24,-60,-85] or self.scene[node[0]][node[1]] >50:
					closed.append(node)
				if node[1]<18 and node[0]<18 and node[0]>1 and node[1]>1:#attempt at better enemy detection, seems to work well
					if (self.scene[node[0]][node[1]+1] >50) and node in neighborhood and [node[0],node[1]] != target:
						closed.append(node)
					if self.scene[node[0]][node[1]]==0 and self.scene[node[0]-1][node[1]] in [-24,-60,-85]: 
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
					

		#Here begins the danger zone. This is returned if there is no path found. Usually indicates too many nodes were closed.
		return [[8,8]]

	#Returns the path from the goal to the start node
	def rebuildPath(self,camefrom,current):
		new = [int(camefrom[current[0]][current[1]][0]),int(camefrom[current[0]][current[1]][1])];
		prev = [current]
		while new != [9,9]:
			prev.append(new)
			new = [int(camefrom[current[0]][current[1]][0]),int(camefrom[current[0]][current[1]][1])]
			current = new
		return prev

			
	
	def getAction(self):
		path = self.search()
		if len(path)>1:
			direction = path[-2]
		else:
			direction = path[-1]
		if (direction[0] == 8 or direction[0]== 7 or self.scene[direction[0]+1][direction[1]]==0) and (self.mayMarioJump or not self.isMarioOnGround or self.bigj < 2):
			self.action[self.KEY_JUMP] = 1
			self.bigj +=1
		else:
			self.bigj=0
			self.action[self.KEY_JUMP] = 0

		if direction[0] == 7 or direction[0] == 11:
			self.action[self.KEY_SPEED] = 1
		else:
			self.action[self.KEY_SPEED] = 0
		
		if direction[0] == 11:
			self.action[self.KEY_DUCK] = 1
		else:
			self.action[self.KEY_DUCK] = 0
			
		if (direction[1] == 10 or direction[1]==11) and self.isMarioOnGround:
			self.action[self.KEY_RIGHT] = 1
			self.action[self.KEY_LEFT] = 0
		elif (direction[1] == 8 or direction[1]==7) and self.isMarioOnGround:
			self.action[self.KEY_LEFT] = 1
			self.action[self.KEY_RIGHT] = 0
			
		#Hacky attmept to detect if mario gets stuck, works sometimes and others not so much. Wont detect if he gets stuck in a "loop"
		self.marioLastX.append(math.floor(self.marioFloats[0]))
		if len(self.marioLastX)>80:
			self.marioLastX.pop(0)
		if self.marioLastX.count(math.floor(self.marioFloats[0])) > 30:
			#He's stuck so do the oposite of what he's currently doing
			for i in range(len(self.action)):
				if self.action[i] == 0:
					self.action[i] = 1
				else:
					self.action[i]=0
		self.action[self.KEY_DUCK] = 0
		return self.action
		
	def getName(self):
		return self.agentName

	def integrateObservation(self, squashedObservation, squashedEnemies, marioPos, enemiesPos, marioState):
			
		row = self.receptiveFieldHeight
		col = self.receptiveFieldWidth
		levelScene=[]
		enemiesObservation=[]
		
		for i in range(row):
			levelScene.append(squashedObservation[i*col:i*col+col])

		
		for i in range(row):
			enemiesObservation.append(squashedEnemies[i*col:i*col+col])
		
		self.enemiesScene = enemiesObservation
		self.marioFloats = marioPos
		self.enemiesFloats = enemiesPos
		self.mayMarioJump = marioState[3]
		self.isMarioOnGround = marioState[2]
		self.marioState = marioState[1]
		self.levelScene = levelScene
		if [int(self.marioFloats[0]/16),int(self.marioFloats[1]/16)] not in self.visited:
			self.visited.append([int(self.marioFloats[0]/16),int(self.marioFloats[1]/16)])

	def printLevelScene(self):
		ret = ""
		for x in range(self.receptiveFieldWidth):
			tmpData = ""
			for y in range(self.receptiveFieldHeight):
				tmpData += self.mapElToStr(self.getReceptiveFieldCellValue(x, y));
			ret += "\n%s" % tmpData;

	def printenvobv(self):
		for x in self.levelScene:
			print x
		for x in self.enemiesScene:
			print x
			
	def mapElToStr(self, el):
		"""maps element of levelScene to str representation"""
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

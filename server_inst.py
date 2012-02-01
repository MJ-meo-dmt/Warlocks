from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

from db import DataBase
from server import Server
from game import Game

game_tick=1.0/60.0

class ServerInst():
	def __init__(self):
		# Initialise Window
		self.showbase=ShowBase()
		
		# Disable Mouse Control for camera
		self.showbase.disableMouse()
		
		camera.setPos(0,0,350)
		camera.lookAt(0,0,0)
		# Start our server up
		self.server = Server(9099, compress=True)
		self.db = DataBase()
		self.users={} # We should send the clients from the lobby to here somehow? or just get it from somewhere...
		
		#if newGame == True:
			# Lets make something that instances the gameServer class for everything game thats hosted?
			
		taskMgr.doMethodLater(0.5, self.pregame_loop, 'Pregame Loop') # Probly start the game then
        
		# FROM HERE WILL GO TO GAME SERVER>>>
	def pregame_loop(self,task):
		# Guess all of this should move after the if.
		#print "Pregame State"
		if self.server.getClients():
			self.game_time=0
			self.tick=0
			self.game=Game(len(self.users),game_tick,self.showbase)
			temp=self.server.getData()
			print temp
			if temp!=[]:
				for i in range(len(temp)):
					valid_packet=False
					package=temp[i]
					if len(package)==2:
						print "Received: "+str(package)+" "+str(package[1])
						if len(package[0])==2:
							print "Packet right size"
							for u in range(len(self.users)):
								self.users[u]['warlock']=self.game.warlock[u]
								if self.users[u]['connection']==package[1]:
									print "Packet from "+self.users[u]['name']
									if package[0][0]=='ready':
										print "So i got the ready and im in game state"
										taskMgr.doMethodLater(0.5, self.game_loop, 'Game Loop')
										return task.done
									else:
										print "well i didnt get shit"
            
            
		return task.again
		
	def game_loop(self,task):
		#print "Game State"
		# if there is any clients connected
		if self.server.getClients():
			# process incoming packages
			temp=self.server.getData()
			if temp!=[]:
				for i in range(len(temp)):
					valid_packet=False
					package=temp[i]
					if len(package)==2:
						print "Received: " + str(package) +" "+str(package[1])
						if len(package[0])==2:
							print "packet right size"
							# else check to make sure connection has username
							for u in range(len(self.users)):
								if self.users[u]['connection']==package[1]:
									print "Packet from "+self.users[u]['name']
									# process packet
									# if chat packet
									if package[0][0]=='destination':
										print "Destination: "+str(package[0][1])
										valid_packet=True
										# Update warlock data for client
										self.users[u]['warlock'].set_destination(Vec3(package[0][1][0],package[0][1][1],0))
										self.users[u]['new_dest']=True
									elif package[0][0]=='spell':
										print "Spell: "+str(package[0][1])
										valid_packet=True
										# Update warlock data for client
										self.users[u]['warlock'].set_spell(package[0][1][0],package[0][1][1])
										self.users[u]['new_spell']=True
									break
								else:
									print "couldnt find connection"+str(self.users[u]['connection'])+" "+str(package[1])
			# get frame delta time
			dt=globalClock.getDt()
			self.game_time+=dt
			# if time is less than 3 secs (countdown for determining pings of clients)
			# tick out for clients
			if (self.game_time>game_tick):
				# update all clients with new info before saying tick
				for u in range(len(self.users)):
					# new warlock destinations
					if self.users[u]['new_dest']:
						data = {}
						data[0]='update_dest'
						data[1]=u
						data[2]={}
						data[2][0]=self.users[u]['warlock'].destination.getX()
						data[2][1]=self.users[u]['warlock'].destination.getY()
						self.users[u]['new_dest']=False
						self.server.broadcastData(data)
					# new warlock spell
					elif self.users[u]['new_spell']:
						data = {}
						data[0]='update_spell'
						data[1]=u
						data[2]=self.users[u]['warlock'].get_spell()
						data[3]=self.users[u]['warlock'].get_target()
						self.users[u]['new_spell']=False
						self.server.broadcastData(data)
				
				data = {}
				data[0]='tick'
				data[1]=self.tick
				self.server.broadcastData(data)
				self.game_time-=game_tick
				self.tick+=1
				# run simulation
				self.game.run_tick()
			return task.cont
		else:
			#taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
			return task.done

si = ServerInst()
run()

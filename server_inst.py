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
from spell							import Spell
from spellmanager					import SpellManager

game_tick=1.0/60.0

num_users=5

class ServerInst():
	def __init__(self):
		# Initialise Window
		self.showbase=ShowBase()
		
		# Disable Mouse Control for camera
		self.showbase.disableMouse()
		
		# Start our server up
		self.server = Server(9099, compress=True)
		self.db = DataBase()
		self.users={} # We should send the clients from the lobby to here somehow? or just get it from somewhere...

		for i in range(num_users):
			new_user={}
			new_user['name']='cake'
			new_user['connection']='cake'
			new_user['ready']=True
			new_user['new_dest']=False
			new_user['new_spell']=False
			self.users[len(self.users)]=new_user
		
		camera.setPos(0,0,45*num_users)
		camera.lookAt(0,0,0)
		
		taskMgr.doMethodLater(0.5, self.pregame_loop, 'Lobby Loop')
		#taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')

		#if newGame == True:
			# Lets make something that instances the gameServer class for everything game thats hosted?
			
		#taskMgr.doMethodLater(0.5, self.login_loop, 'Login Loop') # Probly start the game then
		
		# FROM HERE WILL GO TO GAME SERVER>>>
	def pregame_loop(self,task):
		"""# Guess all of this should move after the if.
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
		"""
		# if in pregame state
		temp=self.server.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package) +" "+ str(package[1].getAddress())
					if len(package[0])==2:
						# if username is sent, assign to client
						if package[0][0]=='username':
							user_found=False
							valid_packet=True
							for u in range(len(self.users)):
								if self.users[u]['name']==package[0][1]:
									print "User already exists"
									user_found=True
									data = {}
									data[0] = "error"
									data[1] = "User already exists"
									self.server.sendData(data,package[1])
									# send something back to the client saying to change username
							if not user_found:
								new_user={}
								new_user['name']=package[0][1]
								new_user['connection']=package[1]
								new_user['ready']=False
								new_user['new_dest']=False
								new_user['new_spell']=False
								self.users[len(self.users)]=new_user
								data = {}
								data[0] = "which"
								data[1] = len(self.users)-1
								self.server.sendData(data,package[1])
						# else check to make sure connection has username
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
								print "Packet from "+self.users[u]['name']
								# process packet
								update_warlocks=False
								# if chat packet
								if package[0][0]=='chat':
									print "Chat: "+package[0][1]
									valid_packet=True
									# Broadcast data to all clients ("username: message")
									data = {}
									data[0]='chat'
									data[1]=self.users[u]['name']+": "+package[0][1]
									self.server.broadcastData(data)
								# else if ready packet
								elif package[0][0]=='ready':
									print self.users[u]['name']+" is ready!"
									self.users[u]['ready']=True
									valid_packet=True
									update_warlocks=True
								# else if unready packet
								elif package[0][0]=='unready':
									print self.users[u]['name']+" is not ready!"
									self.users[u]['ready']=False
									valid_packet=True
									update_warlocks=True
								if update_warlocks:
									data = {}
									data[0]='warlocks'
									data[1]=len(self.users)
									self.server.broadcastData(data)
								# break out of for loop
								break
							#else:
							#	print str(self.users[u]['connection'])+" "+str(package[1])
						if not valid_packet:
							data = {}
							data[0] = "error"
							data[1] = "Please Login"
							self.server.sendData(data,package[1])
							print "User not logged in"
					else:
						print "Data in packet wrong size"
				else:
					print "Packet wrong size"
		# if all players are ready and there is X of them
		game_ready=True
		# if there is any clients connected
		if not self.server.getClients():
			game_ready=False
		for u in range(len(self.users)):
			if self.users[u]['ready']==False:
				game_ready=False
		if game_ready:
			data = {}
			data[0]='state'
			data[1]='game'
			self.server.broadcastData(data)
			taskMgr.doMethodLater(0.5, self.preround_loop, 'Preround Loop')
			return task.done
		return task.again
		
	def preround_loop(self,task):
		print "Preround State"
		self.game_time=0
		self.tick=0
		self.showbase.num_warlocks=len(self.users)
		
		# i guess this shit should be in the pregame part, so people can choose their spells based of these
		# also it will need to be created in there from data passed from the server (where it will be procedurally generated)
		# spell0
		spell0=Spell()
		
		spell0.damage=10
		spell0.target_knockback=20
		spell0.self_knockback=0
		spell0.range=25
		spell0.speed=15
		spell0.aoe=False
		spell0.aoe_range=0
		spell0.targeting=False
		spell0.casting_time=0
		spell0.interruptable=False
		spell0.model="media/spells/blockyball"
		
		# spell1
		spell1=Spell()
		
		spell1.damage=25
		spell1.target_knockback=10
		spell1.self_knockback=0
		spell1.range=50
		spell1.speed=25
		spell1.aoe=False
		spell1.aoe_range=0
		spell1.targeting=False
		spell1.casting_time=0
		spell1.interruptable=False
		spell1.model="media/spells/pointyball"
		
		# spell2
		spell2=Spell()
		
		spell2.damage=50
		spell2.target_knockback=10
		spell2.self_knockback=30
		spell2.range=50
		spell2.speed=15
		spell2.aoe=False
		spell2.aoe_range=0
		spell2.targeting=False
		spell2.casting_time=0
		spell2.interruptable=False
		spell2.model="media/spells/blockyball"
		
		# spell3
		spell3=Spell()
		
		spell3.model="media/spells/pointyball"
		
		# maybe this shit too, or this can stay here and just pass in an array of spells 
		self.showbase.spell_man=SpellManager(self.showbase.num_warlocks) # until the Game() class is created in here which i think it should
		self.showbase.spell_man.add_spell(spell0)
		self.showbase.spell_man.add_spell(spell1)
		self.showbase.spell_man.add_spell(spell2)
		self.showbase.spell_man.add_spell(spell3)
		
		self.game=Game(self.showbase,game_tick)
		for u in range(self.showbase.num_warlocks):
			self.users[u]['warlock']=self.game.warlock[u]
		taskMgr.doMethodLater(0.5, self.game_loop, 'Game Loop')
		return task.done
		#return task.again
	
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
							#print "packet right size"
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
								#else:
								#	print "couldnt find connection"+str(self.users[u]['connection'])+" "+str(package[1])
			# get frame delta time
			dt=globalClock.getDt()
			self.game_time+=dt
			# if time is less than 3 secs (countdown for determining pings of clients)
			# tick out for clients
			if (self.game_time>game_tick):
				# update all clients with new info before saying tick
				for u in range(self.showbase.num_warlocks):
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
				if not self.game.run_tick():
					print 'Game Over'
			return task.cont
		else:
			#taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
			return task.done

si = ServerInst()
run()

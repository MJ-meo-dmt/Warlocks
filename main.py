from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""    
	window-title WARLOCKS
	fullscreen 0
	win-size 1024 768
	cursor-hidden 0
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText  import OnscreenText

from pandac.PandaModules      import *
import sys

from client							import Client

from prelobby import PreLobby
from mainmenu import MainMenu
from pregame import Pregame
from preround import Preround
from playstate import Playstate
from client_config import *


class Main(ShowBase):
	def __init__(self):
		self.created_client=False
		ShowBase.__init__(self)
		self.prelobby=PreLobby(self)
		self.which=0
		# Client username
		self.username = ""
		#self.status=OnscreenText(text = "Attempting to login...", pos = Vec3(0, -0.4, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter)
	
	def login(self, username, password):
		# This should move maybe im not sure.
		self.client = Client(LOGIN_IP, LOGIN_PORT, compress=True)
		
		# Add the handler for the login stage.
		taskMgr.doMethodLater(0.2, self.login_packetReader, 'Update Login')
		
		if self.client.getConnected():
			if username and password:
				self.username=username
				# Setup the un/up sendpacket, this will be changed. later :P
				data = {}
				data[0] = 'login_request'
				data[1] = {}
				data[1][0] = username
				data[1][1] = password
				self.client.sendData(data)
				return True
			else:
				False
				# Create account?
				'''
				if self.db.username_status == True:
					self.username = username
					self.status=OnscreenText(text = "Attempting to login...", pos = Vec3(0, -0.4, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter)
					taskMgr.add(self.start_mainmenu, 'Start MainMenu')
				else:
					self.prelobby.updateStatus(self.db.status)
				'''
		else:
			# simulate authentication by delaying before continuing
			# if authentication fails, create prelobby again with status text "LOGIN FAILED!"
			
			self.prelobby=PreLobby(self)
			self.prelobby.updateStatus("Could not connect to the Login server")
			
	def login_packetReader(self, task):
		temp=self.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package)
					print "Connected to login server"
					# updates warlocks in game
					if package[0]=='error': # LOGIN FAIL
						print package
						print "User already logged"
						self.prelobby.updateStatus(package[1])
						valid_packet=True
						break
					elif package[0]=='db_reply': # DB STATUS REPLY
						print "DB: "+str(package[1])
						self.prelobby.updateStatus(package[1])
						valid_packet=True
						
					elif package[0]=='login_valid': # LOGIN ACK
						print "Login valid: "+str(package[1])
						self.prelobby.updateStatus(package[1][0])
						print "i am warlock: "+str(package[1])
						self.which=package[1][1]
						valid_packet=True
						print "I should move to main menu now..."
						taskMgr.doMethodLater(0.3, self.start_mainmenu, 'Start Main Menu')
						return task.done
					if not valid_packet:
						data = {}
						data[0] = "error" 
						data[1] = "Fail Server"
						self.client.sendData(data)
						print "Bad packet from server"
				else:
					print "Packet wrong size"
			
		return task.again
		
	def create_account(self, username, password):
		# Got the username and password now check if it exists, if not create it.
		if username and password:
			print username
			self.db.Client_acc_add(username, password)
			if self.db.newuser_created == True:
				self.prelobby.updateStatus(self.db.status)
				
			else:
				self.prelobby.updateStatus(self.db.status) # This is the error. if found in db already.
	
	def start_mainmenu(self,task):
		self.prelobby.destroy()
		#self.status.destroy()   # HERE ALSO HAD TO COMMENT TO MAKE IT WORK
		self.mainmenu=MainMenu(self)
		return task.done
		
	def join_server(self,address):
		# Connect to our server
		self.lobby_con=self.client
		# Here it should either get a list from the lobby server that has a list of games avail.
		# When the client picks one, it connects to it.
		self.client = Client(address, 9099, compress=True)
		if self.client.getConnected():
			print "Connected to server"
			data = {}
			data[0]="username"
			data[1]=self.username # This will end up being the selected server?
			self.client.sendData(data)
			taskMgr.doMethodLater(0.03, self.start_pregame, 'Start Pregame') # I guess this should change to Pregame.
			return True
		else:
			return False
		
	def start_pregame(self,task):
		self.mainmenu.hide()
		#self.status.destroy() ## HERE ALSO HAD TO COMMENT TO MAKE IT WORK
		self.pregame=Pregame(self)
		return task.done
		
	def begin_preround(self):
		print "Game Starting"
		taskMgr.doMethodLater(0.01, self.start_preround, 'Start Preround')
	
	def start_preround(self,task):
		self.pregame.hide()
		#self.status.destroy()
		self.preround=Preround(self)
		return task.done
		
	def begin_round(self):
		print "Round Starting"
		taskMgr.doMethodLater(0.01, self.start_round, 'Start Round')
	
	def start_round(self,task):
		#self.preround.hide()
		#self.status.destroy()
		self.playstate=Playstate(self)
		return task.done
	
	def quit(self):
		sys.exit()

game = Main()
game.run()

from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

class MainMenu():
	def __init__(self, game):
		self.game=game
		
		self.status=OnscreenText(text = "", pos = Vec3(0, -0.35, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter, mayChange=True)
		
		self.background = OnscreenImage(
			image  = 'media/gui/mainmenu/menu.png',
			parent = render2d
		)

		self.title = OnscreenText(
			text   = 'Main Menu',
			fg     = (1, 1, 1, 1),
			parent = self.background,
			pos    = (-0.6, 0.1),
			scale  = 0.06
		)

		self.ip = "127.0.0.1" # Should make this write to file... so that the user can save ip's...

		self.buttons = []
		# Buttons
		boxloc = Vec3(0.0, 0.0, 0.0)
		# Host
		p = boxloc + Vec3(-0.85, 0, -0.79)
		self.hostButton = DirectButton(text="Host", pos = p,  scale = 0.048, relief=DGG.GROOVE, command='')
		
		p = boxloc + Vec3(-0.65, 0, -0.79)
		self.joinButton = DirectButton(text="Join", pos=p, scale=0.048, relief=DGG.GROOVE, command=self.join_server)
		
		
		self.addButton("Join Server",  self.join_server,1, -.1)
		
		self.entry = DirectEntry(
			command = self.setIp,
			focusInCommand = self.clearText,
			frameSize   = (-3, 3, -.5, 1),
			initialText = self.ip,
			parent      = self.buttons[0],
			pos         = (0, -0.6, -1.5),
			text        = "" ,
			text_align  = TextNode.ACenter,
		)
		
		self.addButton("QUIT!",  game.quit,1, -.5)

	def join_chat(self):
		pass
		# Let the client mini auth with the lobby server(lobby_loop) by "Loging into the chat"
		# Since everything will be in the main menu? like a main chat window.. something similar to HoN i guess?
		# When the player opens the Join game by button, a list will be send from the lobby server telling it what games are active.
		# Then the player picks one and it connects via the host name/ip or whatever.
		# While this is busy happening the client stays connected to the lobby server.
		
	# Check here for the blocking.
	def join_server(self):
		self.setIp(self.entry.get())
		self.status.setText("Attempting to join server @ "+self.ip+"...")
		if self.game.join_server(self.ip):
			self.status.setText("")
		else:
			self.status.setText("Could not Connect...")

	def addButton(self, text, command,xPos, zPos):
		button = DirectButton(
			command   = command,
			frameSize = (-2, 2, -.3, 1),
			pos       = (xPos, 0.0, zPos),
			scale     = .1,
			text      = text,
		)

		self.buttons.append(button)

	def clearText(self):
		self.entry.enterText('')

	def hide(self):
		self.background.hide()
		for b in self.buttons:
			b.hide()

	def setIp(self, ip):
		print "set ip", ip
		self.ip = ip

from math import pi, sin, cos, atan2, floor, degrees
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3, CollisionSphere, CollisionNode
from direct.showbase.PythonUtil import fitDestAngle2Src

from pandac.PandaModules import *
from util import *
import math

# Warlock Class
class Warlock(Actor):
	POSITIONS = [
		[(6, 10, 0),    (-30,  0, 0)],
		[(-6, -10, 0),  (-210, 0, 0)],
		[(12, 10, 0),   (-30,  0, 0)],
		[(-12, -10, 0), (-210, 0, 0)],
		[(6, 20, 0),    (-30,  0, 0)],
		[(-6, -20, 0),  (-210, 0, 0)],
		[(12, 20, 0),   (-30,  0, 0)],
		[(-12, -20, 0), (-210, 0, 0)]
	]

	def __init__(self,showbase,index):
		self.index=index
		
		# Load warlock model
		Actor.__init__(self,"models/warlock")
		# Reparent the model to render.
		self.reparentTo(render)
		
		self.setPos(self.POSITIONS[index][0])
		self.setHpr(self.POSITIONS[index][1])
		
		self.destination=(self.POSITIONS[index][0])
		self.new_destination=False
		self.dest_node=showbase.loader.loadModel("models/dest")
		# Reparent the model to render
		self.dest_node.reparentTo(render)
		self.dest_node.setScale(0.25)

		self.colSphere = CollisionSphere(0, 0, 2.5, 3)
		self.colNode = self.attachNewNode(CollisionNode('playerNode'))
		self.colNode.node().addSolid(self.colSphere)
		self.colNode.show()
		
		self.dest_vel=Vec3(0,0,0)
		self.spell_vel=Vec3(0,0,0)
		
		self.damage=1
		
	def set_destination(self,destination):
		# set destination of warlock to input
		self.destination=destination
		self.destination.setX(clamp(self.destination.getX(),-80,80))
		self.destination.setY(clamp(self.destination.getY(),-80,80))
		self.new_destination=True
		self.dest_node.setPos(self.destination)
	
	def adjust_angle(self,angle,dt):
		targetH = angle
		oldH = self.getH()
		targetH = fitDestAngle2Src(oldH,targetH)
		magnitude = abs(targetH-oldH)+90.0
		if magnitude>92.5:
			if (targetH-oldH)<0:
				self.setH((self.getH()-(magnitude*2.5*dt))%360)
			else:
				self.setH((self.getH()+(magnitude*2.5*dt))%360)
		else:
			self.setH((self.getH()+(targetH-oldH))%360)
		# turns with speed relating to difference in angle (too slow when low angles i think)
		#self.setH(self,(3*(targetH-oldH)*dt)%360)
		
	def add_spell_vel(self,spell_vel):
		self.spell_vel.setX(self.spell_vel.getX()+spell_vel.getX())
		self.spell_vel.setY(self.spell_vel.getY()+spell_vel.getY())
		
	def add_damage(self,damage):
		self.damage+=damage

	def update(self,dt):
		self.dest_node.setH(self.getH())
		if self.damage<1:
			self.damage=1
		# if spell is being cast
			# if not facing target
				# turn to face target
			# else
				# cast spell
		# else if moving to new destination
		if self.new_destination:
			# calculate difference in angles between warlock and destination
			self.diff_angle = ((atan2(self.destination.getY()-self.getY(),self.destination.getX()-self.getX()) * (180 / pi)) + 270.0)%360.0
			# turn to face target
			self.adjust_angle(self.diff_angle,dt)
			# increase movement vector in direction of destination (limit to a max speed from this, physics can make it more)
			# so if its already more, dont increase, only if it is less
			self.dest_vel=move_forwards(self.getH(),12.5)
			
			# if warlock has reached destination
			if self.getDistance(self.dest_node)<1.5:
				self.new_destination=False
				self.dest_node.setZ(-10)
				# set animation to idle
		else:
			self.dest_vel.setX(self.dest_vel.getX()*(1-2.5*dt))
			self.dest_vel.setY(self.dest_vel.getY()*(1-2.5*dt))
		
		# decrease spell velocity (friction)
		self.spell_vel.setX(self.spell_vel.getX()*(1-1.25*dt*(5.0/self.damage)))
		self.spell_vel.setY(self.spell_vel.getY()*(1-1.25*dt*(5.0/self.damage)))
		
		# process velocitys from both destination
		self.setX(self.getX()+self.dest_vel.getX()*dt)
		self.setY(self.getY()+self.dest_vel.getY()*dt)
		# and spells
		self.setX(self.getX()+self.spell_vel.getX()*dt)
		self.setY(self.getY()+self.spell_vel.getY()*dt)

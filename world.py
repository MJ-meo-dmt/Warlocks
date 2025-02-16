from pandac.PandaModules import *
from util import *
from panda3d.bullet import *
from bitmasks import *

# World Class
class World():
	def __init__(self,showbase,num_warlocks,worldNP,bullet):
		# Load the environment model (Ground and Lava Rocks)
		#self.model = showbase.loader.loadModel("media/world/arena")
		# Reparent the model to render
		#self.model.reparentTo(render)
		model = showbase.loader.loadModel("media/world/world")
		
		# generate n gon for platform
		world_col=BulletTriangleMesh()
		n_gon=self.create_world(num_warlocks,world_col)
		self.world=render.attachNewNode(n_gon)
		shape = BulletTriangleMeshShape(world_col, dynamic=False)
		
		self.arena = worldNP.attachNewNode(BulletGhostNode('Mesh'))
		self.arena.node().addShape(shape)
		self.arena.setPos(0, 0, 0)
		self.arena.setCollideMask(ARENAMASK)

		bullet.attachGhost(self.arena.node())
		
		# extract lava from the model
		self.lava=model.find("**/Lava")
		self.lava.reparentTo(render)
		
		#shape = BulletPlaneShape(Vec3(0, 0, 1), 0)

		#self.lava = worldNP.attachNewNode(BulletGhostNode('Lava'))
		#self.lava.node().addShape(shape)
		#self.lava.setPos(0, 0, 0)
		# lava does not need collision bitmask as it only has the rays cast against it
		#self.lava.setCollideMask(LAVAMASK)

		#bullet.attachGhost(self.lava.node())
		
		self.proj = render.attachNewNode(LensNode('proj'))
		self.lens = OrthographicLens()
		self.lens.setFilmSize(250)
		self.proj.node().setLens(self.lens)
		self.proj.reparentTo(render)
		self.proj.setPos(0,0,1)
		self.proj.lookAt(0,0,0)

		self.tex = loader.loadTexture('media/world/textures/Mapzone Editz/fieldstone-c.jpg')
		#self.norm = loader.loadTexture('media/world/textures/Mapzone Editz/fieldstone-n.jpg')
		self.ts = TextureStage('ts')
		
	def raise_lava(self):
		self.world.setScale(self.world,0.9999)
		self.arena.setScale(self.arena,0.9999)
		self.world.clearTexture()
		#self.ts.setMode(TextureStage.MReplace)
		self.world.projectTexture(self.ts, self.tex, self.proj)
		#self.ts.setMode(TextureStage.MNormal)
		#self.world.projectTexture(self.ts, self.norm, self.proj)
	
	def create_world(self,n,world_col):
		# make it at least a square
		if n<4:
			n=4
		
		points={}
		
		# rotation between each warlock for even spacing
		rotation=360.0/n
		
		for i in range(n):
			# adjust rotation for this warlock
			rot=rotation*(i+1)
			
			# set its position 10*n+15 units from center
			points[i]=move_forwards(rot,-5.0*n-25.0)
			
		nnode=GeomNode('n_gon')
		for i in range(n):
			triangle=self.create_triangle(points[i],points[(i+1)%n])
			nnode.addGeom(triangle)
			world_col.addGeom(triangle)
			
		return nnode
		
	def create_triangle(self,point1,point2):
		format=GeomVertexFormat.getV3n3cpt2()
		vdata=GeomVertexData('triangle', format, Geom.UHStatic)

		vertex=GeomVertexWriter(vdata, 'vertex')
		normal=GeomVertexWriter(vdata, 'normal')
		color=GeomVertexWriter(vdata, 'color')
		texcoord=GeomVertexWriter(vdata, 'texcoord')
		
		# first point
		vertex.addData3f(point1.getX(), point1.getY(), 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(1, 0)

		# second point
		vertex.addData3f(point2.getX(), point2.getY(), 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(1, 1)

		# center point (0,0,0)
		vertex.addData3f(0, 0, 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(0, 1)
		
		tri1=GeomTriangles(Geom.UHStatic)

		tri1.addVertex(0)
		tri1.addVertex(1)
		tri1.addVertex(2)
		
		tri1.closePrimitive()
		
		triangle=Geom(vdata)
		triangle.addPrimitive(tri1)
		
		return triangle

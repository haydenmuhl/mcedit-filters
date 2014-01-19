import os
import errno

from os.path import expanduser
from pymclevel.infiniteworld import MCInfdevOldLevel
from pymclevel.minecraft_server import MCServerChunkGenerator

workDirLabel = "Work directory"

homeDir = expanduser("~")
inputs = (
    (workDirLabel, ("string", "value=" + homeDir + "/.mcedit")),
)

displayName = "Import stone variants"

########## Fast data access ##########
# Based on code taken from sethbling's The Floor is Lava filter
from pymclevel import ChunkNotPresent

LevelCache = {}

def getChunk(level, x, z):
	global LevelCache
	
	if level.filename not in LevelCache:
		LevelCache[level.filename] = {}
	cachedChunks = LevelCache[level.filename]
	
	chunkCoords = (x>>4, z>>4)
	if chunkCoords not in cachedChunks:
		try:
			cachedChunks[chunkCoords] = level.getChunk(x>>4, z>>4)
		except ChunkNotPresent:
			return None
	
	return cachedChunks[chunkCoords]

def blockAt(level, x, y, z):
	chunk = getChunk(level, x, z)
	if chunk == None:
		return 0
	return chunk.Blocks[x%16][z%16][y]

def dataAt(level, x, y, z):
	chunk = getChunk(level, x, z)
	if chunk == None:
		return 0
	return chunk.Data[x%16][z%16][y]
	
def setBlockAt(level, x, y, z, block):
	chunk = getChunk(level, x, z)
	if chunk == None:
		return 0
	chunk.Blocks[x%16][z%16][y] = block

def setDataAt(level, x, y, z, data):
	chunk = getChunk(level, x, z)
	if chunk == None:
		return 0
	chunk.Data[x%16][z%16][y] = data
	
def tileEntityAt(level, x, y, z):
	chunk = getChunk(level, x, z)
	if chunk == None:
		return 0
	return chunk.tileEntityAt(x, y, z)
	
########## End fast data access ##########

def getLogFile():
	f = open("/Users/hmuhl/tmp/mceditFilter.log", "w")
	return f


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def perform(level, box, options):
	level17 = level
	
	log = getLogFile()
	
	log.write("Filter starting...\n")
	log.flush()
	
	seed = level.RandomSeed
	chunks = []
	workDir = options[workDirLabel]
	mkdir_p(workDir)
	level18 = MCInfdevOldLevel(workDir + "/" + str(seed), True, seed)
	
	log.write("Calculating chunk coordinates\n")
	log.flush()
	for cx in range(box.minx >> 4, (box.maxx >> 4) + 1):
	    for cz in range(box.minz >> 4, (box.maxz >> 4) + 1):
	    	if level.containsChunk(cx, cz):
	    		chunks.append((cx, cz))
	
	generator = MCServerChunkGenerator("Release 14w03b")
	log.write("Generating chunks\n")
	log.write(str(chunks) + "\n");
	log.flush()
	generator.generateChunksInLevel(level18, chunks)
	log.write("Done generating chunks\n")
	log.flush()
	
	stoneId = 1
	smoothStone = 0
	stoneVariants = [1, 3, 5]
	
	log.write("Checking each block\n")
	log.flush()
	for x in (box.minx, box.maxx):
	    for y in (box.miny, box.maxy):
	        for z in (box.minz, box.maxz):
	        	block18 = blockAt(level18, x, y, z)
	        	data18 = dataAt(level18, x, y, z)
	        	if (block18 == stoneId and data18 in stoneVariants):
	        		block17 = blockAt(level17, x, y, z)
	        		data17 = dataAt(level17, x, y, z)
	        		if (block17 == stoneId and data17 == smoothStone):
	        		    setDataAt(level17, x, y, z, data18)
	
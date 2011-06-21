from core.packet import TibiaPacket
from core.game import enum
from core.game.map import placeCreature, removeCreature
from twisted.python import log

class TibiaPlayer:
    def __init__(self, client, data):
        self.data = data
        self.client = client
        self.creatureType = 0
        self.direction = 0
        self.position = [50,50,7]

    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.client.client_id
    def sendFirstPacket(self):
        stream = TibiaPacket()
        stream.uint8(0x0A) # Packet type
        stream.uint32(self.clientId()) # Cid
        stream.uint16(0x0032) # Speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.position)
        stream.map_description((self.position[0] - 8, self.position[1] - 6, self.position[2]), 18, 14)

        for slot in range(enum.SLOT_FIRST,enum.SLOT_LAST):
            stream.uint8(0x78)
            stream.uint8(slot)
            if slot is 3:
                stream.uint16(2853)
            elif slot is 1:
                stream.uint16(7992)
            elif slot is 2:
                stream.uint16(3008)
            elif slot is 4:
                stream.uint16(3357)
            elif slot is 5:
                stream.uint16(7449)
            elif slot is 10:
                stream.uint16(3449)
                stream.uint8(20)
        self.stream_status(stream)
        self.stream_skills(stream)
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.client.client_id, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

        stream.send(self.client)
        
    def stream_status(self, stream):
        stream.uint8(0xA0)
        stream.uint16(150)
        stream.uint16(150)
        stream.uint32(10000) # TODO: Free Capasity
        stream.uint32(8000) # TODO: Capasity
        stream.uint64(65000) # TODO: Virtual cap? Experience
        stream.uint16(100) # TODO: Virtual cap? Level
        stream.uint8(0) # % to next level, TODO
        stream.uint16(1000) # mana
        stream.uint16(1000) # mana max
        stream.uint8(1) # TODO: Virtual cap? Manalevel
        stream.uint8(1) # TODO: Virtual cap? ManaBase
        stream.uint8(0) # % to next level, TODO
        stream.uint8(0) # TODO: Virtual cap? Soul
        stream.uint16(60) # Stamina minutes
        stream.uint16(0x0032) # Speed
        
        stream.uint16(0x00) # Condition

    def stream_skills(self, stream):
        stream.uint8(0xA1) # Skill type
        for x in range(0,7): # 7 skill types
            stream.uint8(1) # Value / Level
            stream.uint8(1) # Base
            stream.uint8(0) # %
            
            
    def turn(self, direction):
        if self.direction is direction:
	    return
	    
        self.direction = direction
        
        # Make package
        stream = TibiaPacket()
        stream.uint8(0x6B) # Package type
        stream.position(self.position)
        stream.uint8(1)
        stream.uint16(0x63)
        stream.uint16(self.clientId())
        stream.uint8(direction)
		
        # Send to everyone
        # Actually, since we only got one player, jsut send to us
        stream.send(self.client)

    def move(self, direction):
        self.direction = direction
        
        # Make packet
        stream = TibiaPacket()
        stream.uint8(0x6D)
        stream.position(self.position)
        log.msg("Move on pos %d,%d" % (self.position[0], self.position[1]))
        stream.uint8(1)
        
        removeCreature(self, self.position)
        
        # Recalculate position
        if direction is 0:
           self.position[1] = self.position[1] - 1
        elif direction is 1:
           self.position[0] = self.position[0] + 1
        elif direction is 2:
           self.position[1] = self.position[1] + 1
        else:
           self.position[0] = self.position[0] - 1
           
        stream.position(self.position)
        log.msg("Move on dest %d,%d" % (self.position[0], self.position[1]))
        placeCreature(self, self.position)
        
        # Send to everyone
        stream.send(self.client)
        
        self.updateMap(direction)
        
    def pong(self):
        stream = TibiaPacket()
        stream.uint8(0x1E)
        stream.send(self.client)
        
    def updateMap(self, direction):
        stream = TibiaPacket()
        stream.uint8(0x65 + direction)
        if direction is 0:
            stream.map_description((self.position[0] - 8, self.position[1] - 5, self.position[2]), 18, 1)
        elif direction is 1:
            stream.map_description((self.position[0] + 8, self.position[1] - 6, self.position[2]), 1, 14)
        elif direction is 2:
            stream.map_description((self.position[0] - 8, self.position[1] + 6, self.position[2]), 18, 1)
        elif direction is 3:
            stream.map_description((self.position[0] - 7, self.position[1] - 6, self.position[2]), 1, 14)

        stream.send(self.client)
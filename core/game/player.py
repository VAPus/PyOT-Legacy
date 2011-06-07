from core.packet import TibiaPacket
from core.game import enum

class TibiaPlayer:
    def __init__(self, client, data):
        self.data = data
        self.client = client

    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.client.client_id
    def sendFirstPacket(self):
        stream = TibiaPacket()
        stream.uint8(0x0A) # Packet type
        stream.uint32(self.client.client_id) # Cid
        stream.uint16(0x0032) # Speed
        stream.uint8(1) # Rule violations?

        stream.uint8(0x64) # Map description
        stream.position(self.client.position)
        stream.map_description((self.client.position[0] - 8, self.client.position[1] - 6, self.client.position[2]), 18, 14)

        for slot in range(enum.SLOT_FIRST,enum.SLOT_LAST):
            stream.uint8(0x78)
            stream.uint8(slot)
        
        self.stream_status(stream)
        self.stream_skills(stream)
        
        stream.worldlight(enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.creaturelight(self.client.client_id, enum.LIGHTLEVEL_WORLD, enum.LIGHTCOLOR_WHITE)
        stream.uint8(0xA2) # Icons
        stream.uint16(0) # TODO: Icons

        stream.send(self.client)
        
    def stream_status(self, stream):
        stream.uint8(0xA0)
        stream.uint16(self.data["health"])
        stream.uint16(self.data["healthmax"])
        stream.uint32(1000) # TODO: Capasity
        stream.uint64(self.data["experience"]) # TODO: Virtual cap?
        stream.uint16(self.data["level"]) # TODO: Virtual cap?
        stream.uint8(0) # % to next level, TODO
        stream.uint16(self.data["mana"])
        stream.uint16(self.data["manamax"])
        stream.uint8(self.data["maglevel"]) # TODO: Virtual cap?
        stream.uint8(0) # % to next level, TODO
        stream.uint8(self.data["soul"]) # TODO: Virtual cap?
        stream.uint16(self.data["stamina"] / 60000)

    def stream_skills(self, stream):
        stream.uint8(0xA1) # Skill type
        for x in range(0,7): # 7 skill types
            stream.uint8(1) # Value / Level
            stream.uint8(0) # %

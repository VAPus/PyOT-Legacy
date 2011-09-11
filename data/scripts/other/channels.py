import game.chat

# Register channels
# Note: This is NOT reload safe, well, thats a TODO

game.chat.openChannel("<Guild>", 0) # Special channel, TODO
game.chat.openChannel("Party")
game.chat.openChannel("Counselor")
game.chat.openChannel("World Chat")
game.chat.openChannel("Staff")
game.chat.openChannel("Advertising")
#game.chat.openChannel("Advertising-Rookgaard")
game.chat.openChannel("Help")
game.chat.openChannel("Private", 0xFFFF) # Also special
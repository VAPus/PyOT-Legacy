import game.chat

# Register channels
# Note: This is NOT reload safe, well, thats a TODO

game.chat.openChannel("<Guild>", 0, False) # Special channel, TODO
game.chat.openChannel("Party", public=False)
game.chat.openChannel("Counselor")
game.chat.openChannel("World Chat")
game.chat.openChannel("Staff", public=False)
game.chat.openChannel("Advertising")
game.chat.openChannel("Advertising-Rookgaard")
game.chat.openChannel("Help")
game.chat.openChannel("Private", 0xFFFF, public=False) # Also special

asdasdasd
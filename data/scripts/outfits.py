# Example of outfits (resource) file

import game.resource

# The system will id them 1,2,3,4,5....

# Here, we'll make a Citizen look
outfit = game.resource.genOutfit("Citizen") # genOutfit autoregister it, you can also use Outfit(name, premium=False) + regOutfit(outfit)
outfit.look(128, gender=0)
outfit.look(136, gender=1)

# Thats it, feel free to make yet anther, like Mage
# Ow, and by the way, gender 0 is boy
outfit = game.resource.genOutfit("Mage")
outfit.look(130, gender=0)
outfit.look(138, gender=1)
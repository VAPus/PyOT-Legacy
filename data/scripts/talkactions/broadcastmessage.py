classes = {'red':MSG_STATUS_CONSOLE_RED, 'white':MSG_EVENT_ADVANCE, 'green':MSG_INFO_DESCR, 'warning':MSG_STATUS_WARNING}

@register("talkactionFirstWord", "/b") #/b msg;color
@access("TALK_RED")
def broadcastMessage(creature, text):
    msgclass = MSG_STATUS_WARNING
    msgcolor = 'red'
    
    if not text:
        return False
        
    split = text.split(";")
    if split:
        msg,msgcolor = split
    else:
        msg = text

    try:
        msgclass = classes[msgcolor.lower().strip()]
    except:
        creature.message('Invalid message type!')
        return False
        
    for name in game.player.allPlayers:
        player = game.player.allPlayers[name]
        if player.alive and player.client.ready:
            player.message(msg, msgclass)
    return False
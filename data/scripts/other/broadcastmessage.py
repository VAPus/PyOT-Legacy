@register("talkactionFirstWord", "/b") #/b msg;color
@access("TALK_RED")
def broadcastMessage(creature, text):
    msgclass = 'MSG_STATUS_WARNING'
    msgcolor = 'red'
    classes = {'red':'MSG_STATUS_CONSOLE_RED', 'white':'MSG_EVENT_ADVANCE', 'green':'MSG_INFO_DESCR', 'warning':'MSG_STATUS_WARNING'}
    if not text:
        return False
    try:
        msg,msgcolor = text.split(';')
    except:
        msg = text
    if msgcolor:
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
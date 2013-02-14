@registerClass('webPage', 'clientDynamics')
class ClientProtocol(WebPage):
    def render_GET(self, req):
        return """
// Protocol
wgRegisterOpcode(0x00, function(data) { // Evaluate javascript
    eval(data.string());
});

wgRegisterOpcode(0x01, function(data) { // Register data assert
    var type = data.uint8();
    if(type == 0) { // Item.
        var id = data.uint16();
        var width = data.uint8();
        var height = data.uint8();
        var frames = data.uint8();
        wgRegisterItemSprite(id, width, height, frames, data.string());
    }
    if(type == 1) { // Outfit.
        var id = data.uint16();
        var width = data.uint8();
        var height = data.uint8();
        var phases = data.uint8();
        wgRegisterOutfitSprite(id, width, height, phases, data.string());
    }
});

// Default hotkeys.
$(document).bind('keydown.left', function(e) {
    wgMoveLeft();
    return false;
});
$(document).bind('keydown.right', function(e) {
    wgMoveRight();
    return false;
});
$(document).bind('keydown.up', function(e) {
    wgMoveUp();
    return false;
});
$(document).bind('keydown.down', function(e) {
    wgMoveDown();
    return false;
});
$(document).bind('keydown.t', function(e) {
    alert(wgGetTileByView(0, 0));
    return false;
});
"""

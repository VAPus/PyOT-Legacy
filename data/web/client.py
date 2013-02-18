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

wgRegisterOpcode(0x02, function(data) { // Exit with error.
    alert(data.string());
    wgSocketClose();
});

wgRegisterOpcode(0x03, function(data) { // Character list.
    length = data.uint8();
    while(length--) {
        last = data.string();
        alert(last);
    }
    
    pkg = PacketWriter();
    pkg.string(last);
    
    wgSocketSend(pkg);
});

wgRegisterOpcode(0x04, function(data) { // Initial game packet.
    position = data.position(); // center camera.
    cid = data.uint32();
});

function wgHandleTile(data, x, y, z) {
    // Read until we hit 0x0000.
    items = [];
    while(type = data.uint16()) {
        if(type >= 100) { // Item
            var elm = $('<div></div>');
            elm.wgItemSprite(type);
            items.push(elm);
            
            
        }
    }
    $("#map").append(wgTile([x, y, z], [elm]).dom);
}

wgRegisterOpcode(0x05, function(data) { // Full Map 
    position = data.position(); // Start corner position.
    counter = 0;
    if(position.z >= 127)
        floors = (position.z - 127) + 7; // Flawed.
    else {
        floors = 5; // 3 below, two above
    }
    endCounter = floors * 16 * 16; // Accurate for now.
    floor = 16 * 16;
    while(counter < endCounter) {
        // Skip op, 255. Tile op 0.
        if(data.uint8() == 0xFF)
            counter += data.uint8();
        else {
            z = Math.floor(counter // floor);
            mod = counter % floor;
            x = mod >> 4;
            y = mod & 0xf;
            wgHandleTile(data, x, y, z);
        }
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

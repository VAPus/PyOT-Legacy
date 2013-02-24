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
        var itemtype = data.uint8();
        var subtype = data.uint8();
        var movetype = data.uint8();
        var animateAlways = data.uint8();
        wgRegisterItemSprite(id, width, height, frames, itemtype, subtype, movetype, animateAlways, data.string());
    }
    if(type == 1) { // Outfit.
        var id = data.uint16();
        var width = data.uint8();
        var height = data.uint8();
        var phases = data.uint8();
        data.pos += 4;
        wgRegisterOutfitSprite(id, width, height, phases, data.string());
    }
});

wgRegisterOpcode(0x02, function(data) { // Exit with error.
    alert(data.string());
    wgSocketClose();
});

wgRegisterOpcode(0x03, function(data) { // Character list.
    var length = data.uint8();
    for(var i = 0; i < length; i++) {
        last = data.string();
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
    var type = data.uint16();
    while(type) {
        if(type >= 100) { // Item
            var elm = $('<div></div>');
            elm.wgItemSprite(type);
            items.push(elm);            
        }
        type = data.uint16();
    }
    $("#map").append(wgTile([x, y, z], [elm]).dom);
}

wgRegisterOpcode(0x05, function(data) { // Full Map
    var position = data.position(); // Start center position.
    var counter = 0;
    if(position.z >= 127) {
        var floors = (position.z - 127) + 7; // Flawed.
    } else {
        var floors = 1; // Flawed
    }
    var endCounter = floors * 25 * 17; // Accurate for now.
    var floor = 25 * 17;
    var items = [];
    var orgX = position.x;
    var orgY = position.y;
    var orgZ = position.z;

    var map = $("#map");

    while(counter < endCounter) {
        var mapOp = data.uint16();
        
        if(mapOp >= 0xFF00) {
            // Reposition. New item array.
            // XXX: Render other floors

            var move = mapOp - 0xFEFF; // 0xFF00 - 1

            if(move == 1 && position.z == 7)
                map.append(wgTile([position.x - orgX, position.y - orgY, position.z - 7], items).dom);

            counter += move;
            moveY = counter % 17;
            moveX = Math.floor((counter % floor) / 17);
            moveZ = Math.floor(counter / floor); 
            items = []
            position = Position(orgX + moveX, orgY + moveY, orgZ + moveZ);

        } else {
            var elm = $('<div></div>');
            elm.wgItemSprite(mapOp); // For now only items.
            items.push(elm);

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

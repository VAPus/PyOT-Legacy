@registerClass('webPage', 'clientProtocol')
class ClientProtocol(WebPage):
    def render_GET(self, req):
        return """
wgRegisterOpcode(0x00, function(data) { // Evaluate javascript
    eval(data.string());
});

wgRegisterOpcode(0x01, function(data) { // Register data assert
    var type = data.uint8();
    if(type == 0) { // Item.
        var id = data.uint16();
        var frames = data.uint8();
        wgRegisterItemSprite(id, frames, data.string());
    }
});
"""

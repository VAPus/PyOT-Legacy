var WGMOVELOCK = 0;
//jQuery.fx.interval = 20; // 50fps.

function wgTile(pos, items) {
    this.dom = $("<div>");
    this.position = pos;
    this.dom.css("left", pos[0]*32).css("top", pos[1]*32);
    this.items = items;
    for(var i = 0; i < items.length; i++) {
        this.dom.append(items[i]);
    }
    return this;
}

function wgFullRender() {
    map = $("#map");
    // XXX: 16x16 static map now.
    //map.find("*").remove();

    for(var x = 0; x < 16; x++) {
        for(var y = 0; y < 16; y++) {
            var elm = $('<div>');
            map.append(wgTile([x, y], [elm]).dom);
            elm.wgSprite(3031);
        }
    }
}
function wgGetTileByView(viewX, viewY) {
    fields = $("#map div");
    length = fields.length;
    var rX = (viewX * 32) + 'px';
    var rY = (viewY * 32) + 'px';
    while(length--) {
        if(fields[length].style.left == rX && fields[length].style.left == rY)
            return $(fields[length]); 
    }
}
// To be moved.
function wgReleaseMoveLock() {
    WGMOVELOCK = 0;
}
function wgMoveLeft() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var y = 0; y < 16; y++) {
        var elm = $('<div>');
        map.append(wgTile([-1, y], [elm]).dom);
        
    }
    var fields = map.children();

    map.animate({"left": "+=32px"}, 480, 'linear', function() {
        wgReleaseMoveLock();
        fields.each(function() { 
            var elm = $(this);
            var left = parseInt(elm.css("left"));
            if(left >= 480) {
                elm.remove();
            } else {
                elm.css("left", left+32);
            }
        }); 
        map.css("left", 0);
       
    });
}
function wgMoveRight() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var y = 0; y < 16; y++) {
        var elm = $('<div>');
        map.append(wgTile([16, y], [elm]).dom);

    }
    var fields = map.children();

    map.animate({"left": "-=32px"}, {"duration": 480, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var left = parseInt(elm.css("left"));
            if(left < 32) {
                elm.remove();
            } else {
                elm.css("left", left-32);
            }
        });
        map.css("left", 0);

    }});

}
function wgMoveUp() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var x = 0; x < 16; x++) {
        var elm = $('<div>');
        map.append(wgTile([x, -1], [elm]).dom);

    }
    var fields = map.children();

    map.animate({"top": "+=32px"}, {"duration": 480, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var top = parseInt(elm.css("top"));
            if(top >= 480) {
                elm.remove();
            } else {
                elm.css("top", top+32);
            }
        });
        map.css("top", 0);

    }});
}
function wgMoveDown() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var x = 0; x < 16; x++) {
        var elm = $('<div>');
        map.append(wgTile([x, 16], [elm]).dom);

    }
    var fields = map.children();

    map.animate({"top": "-=32px"}, {"duration": 480, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var top = parseInt(elm.css("top"));
            if(top < 32) {
                elm.remove();
            } else {
                elm.css("top", top-32);
            }
        });
        map.css("top", 0);

    }});
}


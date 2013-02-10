var WGMOVELOCK = 0;
//jQuery.fx.interval = 20; // 50fps.
function wgFullRender() {
    map = $("#map");
    // XXX: 16x16 static map now.
    //map.find("*").remove();

    for(var x = 0; x < 16; x++) {
        for(var y = 0; y < 16; y++) {
            var elm = $('<div>');
            elm.css("left", x*32).css("top", y*32);
            map.append(elm);
            elm.wgSprite(3031);
        }
    }
}
function wgGetTileByView(viewX, viewY) {
    fields = $("#map div");
    length = fields.length;
    var rX = (viewX * 32) + 'px';
    var rY = (viewY  *32) + 'px';
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
        elm.css("top", y*32).css("left", -32);
        map.append(elm);
        
    }
    var fields = map.find("div");

    map.animate({"left": "+=32px"}, 500, 'linear', function() {
        wgReleaseMoveLock();
        fields.each(function() { 
            var elm = $(this);
            var left = parseInt(elm.css("left"));
            if(left >= 480) {
                elm.remove();
            } else {
                elm.css("left", left+32)
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
        elm.css("top", y*32).css("left", 512);
        map.append(elm);

    }
    var fields = map.find("div");

    map.animate({"left": "-=32px"}, {"duration": 500, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var left = parseInt(elm.css("left"));
            if(left < 32) {
                elm.remove();
            } else {
                elm.css("left", left-32)
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
        elm.css("top", -32).css("left", x * 32);
        map.append(elm);

    }
    var fields = map.find("div");

    map.animate({"top": "+=32px"}, {"duration": 500, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var top = parseInt(elm.css("top"));
            if(top >= 480) {
                elm.remove();
            } else {
                elm.css("top", top+32)
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
        elm.css("top", 512).css("left", x * 32);
        map.append(elm);

    }
    var fields = map.find("div");

    map.animate({"top": "-=32px"}, {"duration": 500, easing: 'linear', queue: false, complete: function() {
        wgReleaseMoveLock();
        fields.each(function() {
            var elm = $(this);
            var top = parseInt(elm.css("top"));
            if(top < 32) {
                elm.remove();
            } else {
                elm.css("top", top-32)
            }
        });
        map.css("top", 0);

    }});
}


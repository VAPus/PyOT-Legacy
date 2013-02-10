var WGMOVELOCK = 0;

function wgFullRender() {
    map = $("#map");
    // XXX: 16x16 static map now.
    //map.find("*").remove();

    for(var x = 0; x < 16; x++) {
        for(var y = 0; y < 16; y++) {
            var elm = $('<div class="mapelm"></div>');
            elm.css("left", x*32);
            elm.css("top", y*32);
            map.append(elm);
            elm.wgSprite(3031);
        }
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
        var elm = $('<div class="mapelm"></div>');
        elm.css("top", y*32);
        elm.css("left", -32);
        map.append(elm);
        
    }
    $(".mapelm").each(function() {
        $(this).animate({"left": "+=32px"}, 500).promise().done(wgReleaseMoveLock);
    });
    setTimeout(function() { $(".mapelm").each(function() { 
        var elm = $(this);
        var left = parseInt(elm.css("left"));
        if(left >= 512) elm.remove();
    })}, 500);
}
function wgMoveRight() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var y = 0; y < 16; y++) {
        var elm = $('<div class="mapelm"></div>');
        elm.css("top", y*32);
        elm.css("left", 512);
        map.append(elm);

    }
    $(".mapelm").each(function() {
        $(this).animate({"left": "-=32px"}, 500).promise().done(wgReleaseMoveLock);
    });
    setTimeout(function() { $(".mapelm").each(function() {
        var elm = $(this);
        var left = parseInt(elm.css("left"));
        if(left < 0) elm.remove();
    })}, 500);

}
function wgMoveUp() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var x = 0; x < 16; x++) {
        var elm = $('<div class="mapelm"></div>');
        elm.css("top", -32);
        elm.css("left", x * 32);
        map.append(elm);

    }
    $(".mapelm").each(function() {
        $(this).animate({"top": "+=32px"}, 500).promise().done(wgReleaseMoveLock);
    });
    setTimeout(function() { $(".mapelm").each(function() {
        var elm = $(this);
        var top = parseInt(elm.css("top"));
        if(top >= 512) elm.remove();
    })}, 500);

}
function wgMoveDown() {
    if(WGMOVELOCK) return;
    WGMOVELOCK = 1;
    var map = $("#map");

    for(var x = 0; x < 16; x++) {
        var elm = $('<div class="mapelm"></div>');
        elm.css("top", 512);
        elm.css("left", x * 32);
        map.append(elm);

    }
    $(".mapelm").each(function() {
        $(this).animate({"top": "-=32px"}, 500).promise().done(wgReleaseMoveLock);
    });
    setTimeout(function() { $(".mapelm").each(function() {
        var elm = $(this);
        var top = parseInt(elm.css("top"));
        if(top <= 0) elm.remove();
    })}, 500);
}


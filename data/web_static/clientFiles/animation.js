var _wgItemCache = {};
var _wgItemFrames = {};

var _wgOutfitCache = {};
var _wgOutfitFrames = {};

var _wgSpriteHandlers = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}};

function wgFramesBySprite(spriteId, type) {
    if(type == 0) return _wgItemFrames[spriteId];
    else if(type == 1) return _wgOutfitFrames[spriteId];
}
function wgRegisterItemSprite(id, width, height, frames, data) {
    _wgItemFrames[id] = [width, height, frames];
    _wgItemCache[id] = data;

    wgSpriteCallbacks(0, id);
}
function wgRegisterOutfitSprite(id, width, height, phases, data) {
    _wgOutfitFrames[id] = [width, height, phases];
    _wgOutfitCache[id] = data;

    wgSpriteCallbacks(1, id);
}

function wgRequestSprite(type, id, callback) {
    if(callback) {
        if(_wgSpriteHandlers[type][id]) {
            _wgSpriteHandlers[type][id].push(callback);
        } else {
            _wgSpriteHandlers[type][id] = [callback];
        }
    }

    if(_wgSpriteHandlers[type][id].length < 2) {
        var pkg = PacketWriter();
        pkg.uint8(0x01);
        pkg.uint8(type);
        pkg.uint16(id);
        wgSocketSend(pkg);
    }
}

function wgSpriteCallbacks(type, id) {
    if(_wgSpriteHandlers[type][id]) {
        for(var i = 0; i < _wgSpriteHandlers[type][id].length; i++) {
            _wgSpriteHandlers[type][id][i]();
        }
        delete _wgSpriteHandlers[type][id];
    }
}

(function( $ ) {
jQuery.fn.intAttr = function(key) {
    return parseInt(this.attr(key));
}

jQuery.fn.wgAnimateItem = function (spriteId, options) {
    var settings = jQuery.extend( {
      'start'  : 0, // Start frame.
      'repeat' : false,
      'frames' : 0, // Frames to animate
      'move'   : 1, // Move x frames.
      'delay'  : 0.1
    }, options);

    return this.each(function() {
        var $this = $(this);
        $this.wgItemSprite(spriteId, settings['start']);
        setTimeout(function() { $this.wgMoveAnimation(settings['move'], settings['delay'], settings['repeat']); }, settings['delay'] * 1000);
    });
}

jQuery.fn.wgAnimateOutfit = function (spriteId, options) {
    var settings = jQuery.extend( {
      'start'  : 0, // Start frame.
      'repeat' : false,
      'frames' : 0, // Frames to animate
      'move'   : 4, // Move x frames.
      'delay'  : 0.1
    }, options);

    return this.each(function() {
        var $this = $(this);
        $this.wgOutfitSprite(spriteId, settings['start']);
        setTimeout(function() { $this.wgMoveAnimation(settings['move'], settings['delay'], settings['repeat']); }, settings['delay'] * 1000);
    });
}

jQuery.fn.wgMoveAnimation = function(frames, delay, repeat) {
    return this.each(function() {
        var $this = $(this);
        var spriteId = $this.intAttr("wgSpriteId");
        
        if(!spriteId) return;

        var allFrames = wgFramesBySprite(spriteId, $this.intAttr("wgSpriteType"));
        var frameSum = allFrames[0] * allFrames[1] * allFrames[2];
        var frameId = $this.intAttr("wgFrameId");
        frame = frameId + frames;
        if(frame >= frameSum) {
            if(!repeat) {
                return; // XXX: Animation over.
            } else {
                frame = frame % frameSum;
            }
        }
        $this.css("background-position", (frame * allFrames[0] * -32).toString() + 'px 0px');
        $this.attr("wgFrameId", frame);

        if(repeat || (delay && (frame + frames) < frameSum)) {
            setTimeout(function() { $this.wgMoveAnimation(frames, delay, repeat) }, delay * 1000);
        }
    });
}

jQuery.fn.wgItemSprite = function (spriteId, subId) {
    if(!subId) subId = 0;

    if(!_wgItemCache[spriteId]) {
        var $this = this;
        wgRequestSprite(0, spriteId, function() { $this.wgItemSprite(spriteId, subId); });
        return this;
    }

    return this.each(function() {
        var $this = $(this);
        $this.css("background", 'url("data:image/png;base64,' + _wgItemCache[spriteId] + '") no-repeat');
        $this.css("background-position", (subId * -_wgItemFrames[spriteId][0] * 32).toString() + "px 0px");
        $this.attr("wgSpriteId", spriteId);
        $this.css("z-index",  _wgItemFrames[spriteId][1] +  _wgItemFrames[spriteId][0]);
        $this.attr("wgFrameId", subId);
        $this.attr("wgSpriteType", 0);

        $this.css('height', 32 * _wgItemFrames[spriteId][1]);
        $this.css('width', 32 * _wgItemFrames[spriteId][0]);
        $this.css('margin-left', 32 + (-32 * _wgItemFrames[spriteId][1]));
        $this.css('margin-top', 32 + (-32 * _wgItemFrames[spriteId][0]));        
    });
} 

jQuery.fn.wgOutfitSprite = function (spriteId, subId) {
    if(!subId) subId = 0;

    if(!_wgOutfitCache[spriteId]) {
        var $this = this;
        wgRequestSprite(1, spriteId, function() { $this.wgOutfitSprite(spriteId, subId); });
        return this;
    }

    return this.each(function() {
        var $this = $(this);
        $this.css("background", 'url("data:image/png;base64,' + _wgOutfitCache[spriteId] + '") no-repeat');
        $this.css("background-position", (subId * -_wgOutfitFrames[spriteId][0] * 32).toString() + "px 0px");
        $this.attr("wgSpriteId", spriteId);
        $this.attr("wgFrameId", subId);
        $this.attr("wgSpriteType", 1);

        $this.css('height', 32 * _wgOutfitFrames[spriteId][1]);
        $this.css('width', 32 * _wgOutfitFrames[spriteId][0]);
        $this.css('margin-left', 32 + (-32 * _wgOutfitFrames[spriteId][1]));
        $this.css('margin-top', 32 + (-32 * _wgOutfitFrames[spriteId][0]));
    });
}
})( jQuery );


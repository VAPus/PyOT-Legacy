var _wgItemCache = {};
var _wgItemFrames = {};

var _wgOutfitCache = {};
var _wgOutfitFrames = {};

function wgRegisterItemSprite(id, width, height, frames, data) {
    _wgItemFrames[id] = [width, height, frames];
    _wgItemCache[id] = data;
}
function wgRegisterOutfitSprite(id, width, height, phases, data) {
    _wgOutfitFrames[id] = [width, height, phases];
    _wgOutfitCache[id] = data;
}

(function( $ ) {
jQuery.fn.intAttr = function(key) {
    return parseInt(this.attr(key));
}

jQuery.fn.wgAnimateItem = function (spriteId, options) {
    var settings = jQuery.extend( {
      'start'  : 0, // Start frame.
      'frames' : 0, // Frames to animate
      'move'   : 1, // Move x frames.
      'delay'  : 0.1
    }, options);

    return this.each(function() {
        var $this = $(this);
        $this.wgItemSprite(spriteId, settings['start']);
        setTimeout(function() { $this.wgMoveAnimation(settings['move'], settings['delay']); }, settings['delay'] * 1000);
    });
}

jQuery.fn.wgMoveAnimation = function(frames, repeat) {
    return this.each(function() {
        var $this = $(this);
        var spriteId = $this.intAttr("wgSpriteId");
        if(!spriteId) return;

        var frameId = $this.intAttr("wgFrameId");
        frame = frameId + frames;
        if(frame >= _wgItemFrames[spriteId][2]) return; // XXX: Animation over.
    
        $this.css("background-position", (frame * -32).toString() + 'px 0px');
        $this.attr("wgFrameId", frame);

        if(repeat && (frame + frames) < _wgItemFrames[spriteId][2]) {
            setTimeout(function() { $this.wgMoveAnimation(frames, repeat) }, repeat * 1000);
        }
    });
}

jQuery.fn.wgItemSprite = function (spriteId, subId) {
    if(!subId) subId = 0;

    if(!_wgItemCache[spriteId]) {
        // TODO.
    }

    return this.each(function() {
        var $this = $(this);
        $this.css("background", 'url("data:image/png;base64,' + _wgItemCache[spriteId] + '") no-repeat');
        $this.css("background-position", (subId * -32).toString() + "px 0px");
        $this.attr("wgSpriteId", spriteId);
        $this.attr("wgFrameId", subId);

        $this.css('height', 32 * _wgItemFrames[spriteId][1]);
        $this.css('width', 32 * _wgItemFrames[spriteId][0]);
        $this.css('margin-left', 32 + (-32 * _wgItemFrames[spriteId][1]));
        $this.css('margin-top', 32 + (-32 * _wgItemFrames[spriteId][0]));        
    });
} 

jQuery.fn.wgOutfitSprite = function (spriteId, subId) {
    if(!subId) subId = 0;

    if(!_wgOutfitCache[spriteId]) {
        // TODO.
    }

    return this.each(function() {
        var $this = $(this);
        $this.css("background", 'url("data:image/png;base64,' + _wgItemCache[spriteId] + '") no-repeat');
        $this.css("background-position", (subId * -32).toString() + "px 0px");
        $this.attr("wgSpriteId", spriteId);
        $this.attr("wgFrameId", subId);

    });
}
})( jQuery );


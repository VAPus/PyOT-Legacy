var _wgSpriteCache = {};
var _wgSpriteFrames = {};

function wgRegisterItemSprite(id, frames, data) {
    _wgSpriteFrames[id] = frames;
    _wgSpriteCache[id] = data;
}

(function( $ ) {
jQuery.fn.intAttr = function(key) {
    return parseInt(this.attr(key));
}

jQuery.fn.wgAnimate = function (spriteId, options) {
    var settings = jQuery.extend( {
      'start'  : 0, // Start frame.
      'frames' : 0, // Frames to animate
      'move'   : 1, // Move x frames.
      'delay'  : 0.1
    }, options);

    return this.each(function() {
        var $this = $(this);
        $this.wgSprite(spriteId, settings['start']);
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
        if(frame >= _wgSpriteFrames[spriteId]) return; // XXX: Animation over.
    
        $this.css("background-position", (frame * -32).toString() + 'px 0px');
        $this.attr("wgFrameId", frame);

        if(repeat && (frame + frames) < _wgSpriteFrames[spriteId]) {
            setTimeout(function() { $this.wgMoveAnimation(frames, repeat) }, repeat * 1000);
        }
    });
}

jQuery.fn.wgSprite = function (spriteId, subId) {
    if(!subId) subId = 0;

    if(!_wgSpriteCache[spriteId]) {
        // TODO.
    }

    return this.each(function() {
        var $this = $(this);
        $this.css("background", 'url("data:image/png;base64,' + _wgSpriteCache[spriteId] + '") no-repeat');
        $this.css("background-position", (subId * -32).toString() + "px 0px");
        $this.attr("wgSpriteId", spriteId);
        $this.attr("wgFrameId", subId);
        
    });
} 
})( jQuery );

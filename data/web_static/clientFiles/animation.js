var _wgSpriteCache = {3031: "iVBORw0KGgoAAAANSUhEUgAAAQAAAAAgCAMAAADKd1bWAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAADNQTFRFAAAAAAAAuFQA6JAA+PTA+MgQ+ORI/vrQ0G8QtWIQ74wR/qkD/8YR/+BH/u19/////fGKiWsFDQAAAAF0Uk5TAEDm2GYAAAABYktHRACIBR1IAAAACXBIWXMAAABIAAAASABGyWs+AAACE0lEQVRo3u2Y65KDIAyFTbtU99Ku7/+0q65ACDmBbq3OdMmPTgeCJV9yILXrmjVr1qxZs6cbzXb0JvYJRPWg0/l8fnsBAuVAVI9p0Dl3WYaPqgUK9lj8IRDToycx6tzg3LzusFqg9+Hj8+t6+34MQAhETHiyusc6eqEKhH/dWinBHkBv1UCpQuZATksgctynVfeIo+u3JwAoJXiKbHUZ4Y8XyxMAYGmNuVYcVgCDgnAzADDBFQCqFZ4D4BLXPSa0jnAN1RxSpkeMD9RADB+rBCm8C+IIgWQLfVS6RxAXANTVHFJmBnmCSf15Ng0o4uxEcYBbni0snCMYUKFACx7LJGQYll5vBmesz4I4cFqTFJD4pu7Q3yaZl1nCK50QXJpjxi4A6PU0o/I0xJGkFSq0eLym4Ql/ykoYLWefMcdhdv4wOerlaYojSTCKs9wJpmeYrLgQgSICSugkAIgEu18AhpJwAqsuL6gUdvvnjDw8ti/RLVAOgElqGUsdxjE+KkpDe0hXZxUiF3GiCsoZeSL8khPACQQgAPjxDMA6wdbf3RZDcdQVCm+FBSO1aoTkbAChyDmAyNIC0FcDqPsPB48KoxNU14iKI2BsQQqA6VvSyTSypVnXCOsEBQBtTV3Fifyga2I/AMa+cScImsv7/7jDTtnWyMYEyi+Msnh3eUOCNbK7HfNGqNhK/Qfb5KVYs2bNXsp+APFnJ/14SaHrAAAAAElFTkSuQmCC"};
var _wgSpriteFrames = {3031: 8};

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

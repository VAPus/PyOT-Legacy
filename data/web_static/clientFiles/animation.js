var _cssClasses = [];
function WGCreateCSSClass(className, cssProps, doc) {
    if(_cssClasses.indexOf(className) != -1) return;

    var ruleBits = [];
    for(var i in cssProps)
        ruleBits.push(i + ':' + cssProps[i] + ';');

    var style = $('<style>.'+className+'{'+ruleBits.join("")+'}</style>')
    $('html > head').append(style);
    _cssClasses.push(className);   
};
var _wgItemCache = {};
var _wgItemFrames = {};

var _wgOutfitCache = {};
var _wgOutfitFrames = {};

var _wgSpriteHandlers = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}};

function wgFramesBySprite(spriteId, type) {
    if(type == 0) return _wgItemFrames[spriteId];
    else if(type == 1) return _wgOutfitFrames[spriteId];
}
function wgRegisterItemSprite(id, width, height, frames, itemtype, subtype, movetype, animateAlways, data) {
    _wgItemFrames[id] = [width, height, frames, itemtype, subtype, movetype, animateAlways];
    _wgItemCache[id] = data;

    wgSpriteCallbacks(0, id);
}
function wgRegisterOutfitSprite(id, width, height, phases, data) {
    _wgOutfitFrames[id] = [width, height, phases, 4, 0, 0, 0];
    _wgOutfitCache[id] = data;

    wgSpriteCallbacks(1, id);
}

function wgRequestSprite(type, id, callback) {
    if(!_wgSpriteHandlers[type][id]) {
        var pkg = PacketWriter();
        pkg.uint8(0x01);
        pkg.uint8(type);
        pkg.uint16(id);
        wgSocketSend(pkg);
    }

    _wgSpriteHandlers[type][id] = callback;
    
}

function wgSpriteCallbacks(type, id) {
    if(_wgSpriteHandlers[type][id]) {
        _wgSpriteHandlers[type][id]();
       
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
        wgRequestSprite(0, spriteId, function() {
            WGCreateCSSClass('wg-sprite-item-'+spriteId+'-'+subId, {
                "background": 'url("data:image/png;base64,' + _wgItemCache[spriteId] + '") no-repeat',
                "background-position": (subId * -_wgItemFrames[spriteId][0] * 32).toString() + "px 0px",
                "z-index":  (100 * _wgItemFrames[spriteId][4]),
                'height': (32 * _wgItemFrames[spriteId][1]) + 'px !important',
                'width': (32 * _wgItemFrames[spriteId][0]) + 'px !important',
                'margin-left': (32 + (-32 * _wgItemFrames[spriteId][0])) + 'px',
                'margin-top': (0 + (-32 * _wgItemFrames[spriteId][1])) + 'px'
            });
            if(_wgItemFrames[spriteId][6])
                setTimeout(function() { $('.wg-sprite-item-'+spriteId+'-'+subId).wgMoveAnimation(1, 1, true); }, 1 * 1000);
        });
    }
    if(_cssClasses.indexOf('wg-sprite-item-'+spriteId+'-'+subId) != -1) {
            WGCreateCSSClass('wg-sprite-item-'+spriteId+'-'+subId, {
                "background": 'url("data:image/png;base64,' + _wgItemCache[spriteId] + '") no-repeat',
                "background-position": (subId * -_wgItemFrames[spriteId][0] * 32).toString() + "px 0px",
                "z-index":  (100 * _wgItemFrames[spriteId][4]),
                'height': (32 * _wgItemFrames[spriteId][1]) + 'px !important',
                'width': (32 * _wgItemFrames[spriteId][0]) + 'px !important',
                'margin-left': (32 + (-32 * _wgItemFrames[spriteId][0])) + 'px',
                'margin-top': (0 + (-32 * _wgItemFrames[spriteId][1])) + 'px'
            });
    }

    return this.each(function() {
        var $this = $(this);
        $this.addClass('wg-sprite-item-'+spriteId+'-'+subId)
        $this.attr("wgSpriteId", spriteId);
        $this.attr("wgFrameId", subId);
        $this.attr("wgSpriteType", 0);        
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


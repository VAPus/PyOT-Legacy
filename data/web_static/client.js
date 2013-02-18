// Some info about the protocol.
// WebSocket header is 2byte, including 7bit length (for packets <126 bit).
// >=126 adds 2 byte.
// >0xFFFE adds another 6 byte. (We never do this, except that we may if we send items).
// Client may add masking. (We don't like masking). It's 4 byte.
// Tibias header is 8byte. But also have to deal with adler32 and xtea.

// However, binary can't be send as binary in all browsers, so we use base64.
// Worstcase it add 33% to the size. Best case it actually adds 0 because we get closer to the padding. Normalized its 17% I believe.

// We could use base91, for less network overhead, but slower processing.

// Test opcode.
var GLOBAL_SOCKET;

$(function() {

var socket = new WebSocket("ws://"+window.location.hostname+":8081", "base64");

socket.__send = socket.send
socket.send = function(data) {
    socket.__send(window.btoa(data));
}
socket.onopen = function() {
    // Initial request.
    pkg = new PacketWriter();
    pkg.string("123");
    pkg.string("123");
    socket.send(pkg.get());
}

socket.onmessage = function(event) {
    // Data handler.
    packet = new Packet(event.data);
    opcode = packet.uint8();

	if(opcode in OPCODES) {
		wgHandleOpcode(opcode, packet);
	} else {
		alert("Unknown opcode " + opcode);
		socket.close();
	}
}
GLOBAL_SOCKET = socket;

setTimeout(function() {
        wgFullRender();
        $("#test").wgAnimateItem(3031, {'delay': 1});
        
        // Scale.
        wgScaleEvent();
}, 1000);

});

function wgScaleEvent() {
    height = $(window).height(); // Substraction required.

    bodyHeight = $("body").height();
    $("body").css('-moz-transform', 'scale('+(height/bodyHeight)+')');
    $("body").css('-webkit-transform', 'scale('+(height/bodyHeight)+')');
    $("body").css('transform', 'scale('+(height/bodyHeight)+')');
    $("body").css('width', $("#view").width());
    $("body").css('margin-left', ($(window).width() - ($("#view").width() * (height/bodyHeight))) / 2);
}

$(window).resize(wgScaleEvent);

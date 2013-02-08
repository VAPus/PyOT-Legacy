// Some info about the protocol.
// WebSocket header is 2byte, including 7bit length (for packets <126 bit).
// >=126 adds 2 byte.
// >0xFFFE adds another 6 byte. (We never do this, except that we may if we send items).
// Client may add masking. (We don't like masking). It's 4 byte.
// Tibias header is 8byte. But also have to deal with adler32 and xtea.

// However, binary can't be send as binary in all browsers, so we use base64.
// Worstcase it add 33% to the size. Best case it actually adds 0 because we get closer to the padding. Normalized its 17% I believe.

// We could use base91, for less network overhead, but slower processing.

$(function() {
// Position class.
function Position(x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
    return this;
}
// StackPosition class.
function StackPosition(x, y, z, stackPos) {
    this.x = x;
    this.y = y;
    this.z = z;
    return this;
}
// Function to read packets.
function Packet(data) {
    this.data = window.atob(data);
    this.pos = 0;

    this.uint8 = function() {
        this.pos += 1;
        return this.data.charCodeAt(this.pos - 1);
    };

    this.uint16 = function() {
        p1 = this.uint8();
        p2 = this.uint8();
        return (p1 << 8) + p2;
    }

    this.uint32 = function() {
        p1 = this.uint16();
        p2 = this.uint16();

        return (p1 << 16) + p2;
    }

    this.uint64 = function() {
        p1 = this.uint32();
        p2 = this.uint32();

        return (p1 << 32) + p2;
    }

    this.string = function() {
        length = this.uint16();
        this.pos += length;

        return self.data.slice(this.pos - length, this.pos);
    }

    this.longString = function() {
        length = this.uint32();
        this.pos += length;

        return self.data.slice(this.pos - length, this.pos);
    }

    this.position = function() {
        // Unlike Tibia, we use 127 as the ground. Allows you to have floor from 0 to 255.
        // We also use uint32. 5 versus 9 bytes.
        x = this.uint32();
        y = this.uint32();
        z = this.uint8();

        return Position(x, y, z);
    }

    this.stackPosition = function() {
        x = this.uint32();
        y = this.uint32();
        z = this.uint8();
        stackPos = this.uint8();
        return StackPosition(x, y, z, stackPos);
    }
    return this;
}

var socket = new WebSocket("ws://"+window.location.hostname+":8081", "base64");

socket.__send = socket.send
socket.send = function(data) {
    socket.__send(window.btoa(data));
}
socket.onopen = function() {
    // Initial request.
    socket.send("X");
}

socket.onmessage = function(event) {
    // Data handler.
    packet = new Packet(event.data);
    $("#log").append(packet.uint8());
    $("#log").append(" ");
    $("#log").append(packet.uint16());
}

});

// Function to read packets.
function Packet(data) {
    this.data = window.atob(data);
    this.pos = 0;

    this.uint8 = function() {
        this.pos += 1;
        var val = this.data.charCodeAt(this.pos - 1);
        if(isNaN(val)) alert("Out of range!");
        return val;
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

        return this.data.slice(this.pos - length, this.pos);
    }

    this.longString = function() {
        length = this.uint32();
        this.pos += length;

        return this.data.slice(this.pos - length, this.pos);
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

// To write packets.
function PacketWriter() {
    this.data = "";

    this.uint8 = function(code) {
        this.data += String.fromCharCode(code);
    };

    this.uint16 = function(code) {
        this.data += String.fromCharCode(code >> 8, code & 0xFF)
    }

    this.uint32 = function(code) {
        this.uint16(code >> 16);
        this.uint16(code & 0xFFFF);
    }

    this.uint64 = function(code) {
        this.uint32(code >> 32);
        this.uint32(code & 0xFFFFFFFF);
    }

    this.string = function(code) {
        this.uint16(code.length);
        this.data += code;
    }

    this.longString = function() {
        this.uint32(code.length);
        this.data += code;
    }

    this.position = function(pos) {
        // Unlike Tibia, we use 127 as the ground. Allows you to have floor from 0 to 255.
        // We also use uint32. 5 versus 9 bytes.
        this.uint32(pos.x);
        this.uint32(pos.y);
        this.uint8(pos.z);

    }

    this.stackPosition = function(pos) {
        this.uint32(pos.x);
        this.uint32(pos.y);
        this.uint8(pos.z);
        this.uint8(pos.stackPos);
    }
    
    this.get = function () {
        return this.data; //return window.btoa(this.data);
    }
    return this;
}

function wgSocketClose() {
    GLOBAL_SOCKET.close();
}

function wgSocketSend(pkg) {
    GLOBAL_SOCKET.send(pkg.get());
}

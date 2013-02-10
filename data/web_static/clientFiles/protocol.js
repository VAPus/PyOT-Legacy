var OPCODES = {}

function wgRegisterOpcode(code, callback) {
    OPCODES[code] = callback;
}

function wgHandleOpcode(code, data) {
    OPCODES[code](data);
}

local bit = require("bit")
local OPC_ADD4, OPC_XORC, OPC_ROR1 = 0, 1, 2
local CONST = {0xA3, 0x17, 0x5C, 0x99}

local function run(code, r)
    for i = 1, #code do
        local op = bit.band(code:byte(i), 0x0F)
        if     op == OPC_ADD4 then      
            r = bit.band(r + 4, 0xFF)
        elseif op == OPC_XORC then      
            r = bit.band(bit.bxor(r, 0x17), 0xFF)
        elseif op == OPC_ROR1 then      
            local bit0 = bit.band(r, 1)
            r = bit.rshift(bit.band(r, 0xFF), 1) + bit.lshift(bit0, 7)
        end
    end
    return bit.band(r, 0xFF)
end

return function(flag)
    if type(flag) ~= "string" then return "" end
    local code, out = string.char(0,1,2), {}
    for i = 1, #flag do
        out[i] = string.char(run(code, flag:byte(i)))
    end
    return table.concat(out)
end


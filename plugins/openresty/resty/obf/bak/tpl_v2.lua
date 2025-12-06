-- Copyright (C) midoks

local _M = { _VERSION = '1.0' }
local mt = { __index = _M }
local setmetatable = setmetatable

local forgejs = require "resty.obf.forgejs"

function _M.new(self)
    local self = {
    }
    return setmetatable(self, mt)
end

function _M.content(data, iv, tag, key, debug_data)
    local cc = [[
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body></body>
</html>
<script type="text/javascript">{{FORGEJS}}</script>
<script>var encrypted={{SOURCE_DATA}}; var iv_data={{IV_DATA}}; var tag_data={{TAG_DATA}}; var key={{KEY_DATA}};var d={{DEBUG_DATA}};</script>
<script>
function u8ToBytes(u8){var s="";for(var i=0;i<u8.length;i++){s+=String.fromCharCode(u8[i]);}return s;}
function evpBytesToKey(pass, keyLen, ivLen){
    var m=[]; var i=0; var md=forge.md.md5.create();
    function concatLen(arr){var n=0; for(var j=0;j<arr.length;j++){n+=arr[j].length;} return n;}
        while(concatLen(m) < (keyLen+ivLen)){
            md.start(); if(i>0){ md.update(m[i-1]); }
            md.update(pass);
            var d = md.digest().getBytes(); m.push(d); i++;
        }
    var ms = m.join(""); var key = ms.substring(0,keyLen); var iv = ms.substring(keyLen,keyLen+ivLen);
    return {key:key, iv:iv};
}

window.onload = function(){
    var startTime = Date.now();

    var dk = evpBytesToKey(u8ToBytes(key), 32, 32);
    var decipher = forge.cipher.createDecipher("AES-GCM", dk.key);
    decipher.start({iv: u8ToBytes(iv_data), tag: forge.util.createBuffer(u8ToBytes(tag_data))});
    decipher.update(forge.util.createBuffer(u8ToBytes(encrypted)));
    var ok = decipher.finish();

    if (ok) {
        var newDoc = new DOMParser().parseFromString(decipher.output, "text/html");

        if (d){
            console.log(newDoc);
            console.log(decipher.output);
        }  
        document.head.innerHTML = newDoc.head.innerHTML;
        document.open();
        document.write(decipher.output);
        document.close();
    }
    var endTime = Date.now();
    if (d){
        console.log("dec cos(ms):",endTime - startTime);
    }
}
</script>
]]
    
    local fj_content = forgejs.content()
    cc = cc:gsub("{{FORGEJS}}", function() return fj_content end)
    cc = cc:gsub("{{SOURCE_DATA}}", function() return data end)
    cc = cc:gsub("{{IV_DATA}}", function() return iv end)
    cc = cc:gsub("{{TAG_DATA}}", function() return tag end)
    cc = cc:gsub("{{KEY_DATA}}", function() return key end)
    cc = cc:gsub("{{DEBUG_DATA}}", function() return debug_data end)

    return cc
end



return _M

-- Copyright (C) midoks

local _M = { _VERSION = '1.0' }
local mt = { __index = _M }
local setmetatable = setmetatable

local forgejs = require "resty.obf.forgejs"
local util = require "resty.obf.util"
local FJ = forgejs.content()

local obf_log = require "resty.obf.log"
local log_fmt = obf_log.fmt
local log = ngx.log


function _M.new(self)
    local self = {
    }
    return setmetatable(self, mt)
end

function _M.content(data, iv, tag, key, debug_data)
    local head_html = "<!DOCTYPE html>\n<html>\n    <head>\n        <meta charset=\"utf-8\">\n        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    </head>\n    <body></body>\n</html>\n"
    local fj_open = "<script type=\"text/javascript\">"
    local fj_close = "</script>\n"

    local data_script = "<script>\nvar encrypted={{__HOLD_1__}}; var iv_data="..iv.."; var tag_data="..tag.."; var key="..key..";var d="..debug_data..";function u8ToBytes(u8){var s=\"\";for(var i=0;i<u8.length;i++){s+=String.fromCharCode(u8[i]);}return s;}\n"..
        "function evpBytesToKey(pass, keyLen, ivLen){\n"..
        "    var m=[]; var i=0; var md=forge.md.md5.create();\n"..
        "    function concatLen(arr){var n=0; for(var j=0;j<arr.length;j++){n+=arr[j].length;} return n;}\n"..
        "        while(concatLen(m) < (keyLen+ivLen)){\n"..
        "            md.start(); if(i>0){ md.update(m[i-1]); }\n"..
        "            md.update(pass);\n"..
        "            var d = md.digest().getBytes(); m.push(d); i++;\n"..
        "        }\n"..
        "    var ms = m.join(\"\"); var key = ms.substring(0,keyLen); var iv = ms.substring(keyLen,keyLen+ivLen);\n"..
        "    return {key:key, iv:iv};\n"..
        "}\n\n"..
        "window.onload = function(){\n"..
        "    var startTime = Date.now();\n\n"..
        "    var dk = evpBytesToKey(u8ToBytes(key), 32, 32);\n"..
        "    var decipher = forge.cipher.createDecipher(\"AES-GCM\", dk.key);\n"..
        "    decipher.start({iv: u8ToBytes(iv_data), tag: forge.util.createBuffer(u8ToBytes(tag_data))});\n"..
        "    decipher.update(forge.util.createBuffer(u8ToBytes(encrypted)));\n"..
        "    var ok = decipher.finish();\n\n"..
        "    if (ok) {\n"..
        "        var newDoc = new DOMParser().parseFromString(decipher.output, \"text/html\");\n\n"..
        "        if (d){\n"..
        "            console.log(newDoc);\n"..
        "            console.log(decipher.output);\n"..
        "        }\n"..
        "        document.head.innerHTML = newDoc.head.innerHTML;\n"..
        "        document.open();\n"..
        "        document.write(decipher.output);\n"..
        "        document.close();\n"..
        "    }\n"..
        "    var endTime = Date.now();\n"..
        "    if (d){\n"..
        "        console.log(\"dec cos(ms):\",endTime - startTime);\n"..
        "    }\n"..
        "}\n</script>\n"


    if not (ngx.var.obf_rand_var == "false") then
        data_script = util.obf_rand(data_script)
    end

    local prof = ngx.var.obf_prof
    if not (ngx.var.obf_rand_extra == "false") then
        local t_add0 = util.tmark()
        data_script = util.obf_rand_data(data_script)
        if prof == "true" then
            log(ngx.ERR, log_fmt("obf_prof obf_rand_data add_ms=%.2f", util.dt_ms(t_add0)))
        end
    end

    local t_df0 = util.tmark()
    data_script = util.data_filter(data_script)
    if prof == "true" then
        log(ngx.ERR, log_fmt("obf_prof data_filter ms=%.2f", util.dt_ms(t_df0)))
    end

    data_script = data_script:gsub("{{__HOLD_1__}}", data)

    return table.concat({
        head_html,
        fj_open,
        FJ,
        fj_close,
        data_script,
    })
end



return _M

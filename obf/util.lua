-- Copyright (C) midoks

local _M = {_VERSION = '1.0'}
local random = require "resty.random"
local sha256 = require "resty.sha256"
local resty_str = require "resty.string"
local byte = string.byte


function _M.tmark()
    if ngx.hrtime then
        return ngx.hrtime()
    end
    ngx.update_time()
    return ngx.now() * 1000000
end

function _M.dt_ms(start)
    if ngx.hrtime then
        return (ngx.hrtime() - start) / 1000000
    end
    ngx.update_time()
    return (ngx.now() * 1000000 - start) / 1000
end


function _M.to_uint8array(content)
    if not content then
        content = ""
    end
    local len = #content
    if len == 0 then
        return "new Uint8Array([])"
    end
    local mode = ngx.var.obf_uint8_b64
    if mode == "true" or (not mode and len >= 4096) then
        local b64 = ngx.encode_base64(content)
        return "(function(){var s='"..b64.."';var b=atob(s);var a=new Uint8Array(b.length);for(var i=0;i<b.length;i++){a[i]=b.charCodeAt(i)};return a;})()"
    end
    local arr = {}
    for i = 1, len do
        arr[i] = byte(content, i)
    end
    return "new Uint8Array([" .. table.concat(arr, ",") .. "])"
end


function _M.to_b64(content)
    if not content then
        content = ""
    end
    return ngx.encode_base64(content)
end

-- 数据过滤
function _M.data_filter(content)
    if content == nil then
        return ""
    end
    if type(content) ~= "string" then
        content = tostring(content)
    end
    -- if not string.find(content, "<script", 1, true) then
    --     return content:gsub("[\r\n]+", ""):gsub(">%s+<", "><")
    -- end
    -- content = content:gsub("<script(.-)>(.-)</script>", function(attrs, body)
    --     local b = body
    --     b = ("\n"..b):gsub("\n%s*//[^\n\r]*", "\n")
    --     b = b:gsub("([^:])%s+//[^\n\r]*", "%1")
    --     b = b:gsub("%s*([%(%),;:%{%}%[%]%+%-%*%=<>])%s*", "%1")
    --     b = b:gsub("%s+", " ")
    --     return "<script" .. attrs .. ">" .. b .. "</script>"
    -- end)
    return content:gsub(">[%s\r\n]+<", "><")
end


-- 随机变量名
function _M.obf_rand(content)
    local function rand_ident(len)
        local head = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
        local tail = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$"
        local seed = random.bytes(16, true) .. (ngx.var.request_id or "") .. tostring(ngx.time()) .. tostring(ngx.now())
        local h = sha256:new(); h:update(seed); local digest = resty_str.to_hex(h:final())
        local r = {}
        local hi = (string.byte(digest, 1) or 65) % #head + 1
        r[1] = string.sub(head, hi, hi)
        local pos, di = 2, 2
        while pos <= len do
            local c = string.byte(digest, di) or 97
            local ti = c % #tail + 1
            r[pos] = string.sub(tail, ti, ti)
            pos = pos + 1
            di = di + 1
            if di > #digest then
                h = sha256:new(); h:update(digest .. random.bytes(8, true)); digest = resty_str.to_hex(h:final()); di = 1
            end
        end
        return table.concat(r)
    end
    local ids = {"encrypted","iv_data","key","tag_data","d","u8ToBytes","evpBytesToKey","startTime","dk","decipher","ok","newDoc","endTime"}
    local map = {}
    for _, id in ipairs(ids) do
        map[id] = rand_ident(8)
    end
    for k, v in pairs(map) do
        local pat = "%f[%w_]" .. k .. "%f[^%w_]"
        content = content:gsub(pat, v)
    end
    return content
end



-- 添加混淆代码
function _M.obf_rand_data(content)
    if content == nil then
        return ""
    end
    if type(content) ~= "string" then
        content = tostring(content)
    end
    content = content:gsub("<script(.-)>(.-)</script>", function(attrs, body)
        local b = body
        local function rand_ident(len)
            local head = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
            local tail = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$"
            local seed = random.bytes(16, true) .. (ngx.var.request_id or "") .. tostring(ngx.time()) .. tostring(ngx.now())
            local h = sha256:new(); h:update(seed); local digest = resty_str.to_hex(h:final())
            local r = {}
            local hi = (string.byte(digest, 1) or 65) % #head + 1
            r[1] = string.sub(head, hi, hi)
            local pos, di = 2, 2
            while pos <= len do
                local c = string.byte(digest, di) or 97
                local ti = c % #tail + 1
                r[pos] = string.sub(tail, ti, ti)
                pos = pos + 1
                di = di + 1
                if di > #digest then
                    h = sha256:new(); h:update(digest .. random.bytes(8, true)); digest = resty_str.to_hex(h:final()); di = 1
                end
            end
            return table.concat(r)
        end
        local v1 = rand_ident(8)
        local v2 = rand_ident(8)
        local v3 = rand_ident(8)
        local f1 = rand_ident(8)
        local f2 = rand_ident(8)
        local tmp = rand_ident(8)
        local filler = "var "..v1.."=\""..ngx.encode_base64(random.bytes(8, true)).."\";"
            .."var "..v2.."=".._M.to_uint8array(random.bytes(8, true))..";"
            .."var "..v3.."="..tostring(#ngx.encode_base64(random.bytes(6, true)))..";"
            .."function "..f1.."(x){return x}"
            .."function "..f2.."(){return "..v3.."}"
            .."(function(){var "..tmp.."="..v3.."; for(var i=0;i<1;i++){"..tmp.."="..tmp.."+i}})();"
        b = filler..";"..b
        b = b:gsub("%s+", " ")
        b = b:gsub("%s*([%(%),;:%{%}%[%]%+%-%*%=<>])%s*", "%1")
        return "<script" .. attrs .. ">" .. b .. "</script>"
    end)
    return content
end

return _M

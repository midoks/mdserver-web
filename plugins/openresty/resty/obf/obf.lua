-- Copyright (C) midoks

local _M = { _VERSION = '1.0' }
local mt = { __index = _M }
local setmetatable = setmetatable

local obf_log = require "resty.obf.log"
local tpl = require "resty.obf.tpl"
local log_fmt = obf_log.fmt
local aes = require "resty.aes"
local ffi = require "ffi"
local ffi_str = ffi.string
local sha256 = require "resty.sha256"
local resty_str = require "resty.string"
local random = require "resty.random"
local lrucache = require "resty.lrucache"
local obf_cache = lrucache.new(1024)

local find = string.find
local byte = string.byte
local log = ngx.log


function _M.new(self)
    local self = {
    }
    return setmetatable(self, mt)
end


function _M.to_uint8array(content)
    if not content then
        content = ""
    end
    local arr = {}
    for i = 1, #content do
        arr[#arr + 1] = tostring(byte(content, i))
    end
    return "new Uint8Array([" .. table.concat(arr, ",") .. "])"
end

-- 数据过滤
function _M.data_filter(content)
    content = content:gsub("<script(.-)>(.-)</script>", function(attrs, body)
        local b = body
        b = b:gsub("^%s*//[^\n\r]*", "")
        b = b:gsub("\n%s*//[^\n\r]*", "\n")
        b = b:gsub("([^:])%s+//[^\n\r]*", "%1")
        b = b:gsub("%s+", " ")
        b = b:gsub("%s*([%(%),;:%{%}%[%]%+%-%*%=<>])%s*", "%1")
        return "<script" .. attrs .. ">" .. b .. "</script>"
    end)

    content = content:gsub("[\r\n]+", ""):gsub(">%s+<", "><")
    return content
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
function _M.obf_add_data(content)
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
    content = content:gsub("[\r\n]+", ""):gsub(">%s+<", "><")
    return content
end


-- 编码
function _M.obf_encode(content)
    local enc, tag, iv_bin
    local content_type = ngx.header.content_type or ""
    local upstream_ct = ngx.var.upstream_http_content_type or ""
    local cl = ngx.header["Content-Length"] or ""
    local upstream_cl = ngx.var.upstream_http_content_length or ""

    local key = random.bytes(8, true)
    -- log(ngx.ERR, log_fmt("enc=aes-256-gcm, pass_b64=%s", ngx.encode_base64(password)))
    local cipher = aes.cipher(256, "gcm")
    local a, aerr = aes:new(key, nil, cipher, aes.hash.md5, 1, 12, true)

    if not a then
        log(ngx.ERR, log_fmt("aes init error: %s", tostring(aerr)))
    else
        local key_bin = ffi_str(a._key, 32)
        iv_bin = ffi_str(a._iv, 12)
        local sh1 = sha256:new(); sh1:update(key_bin); local key_fpr = resty_str.to_hex(sh1:final())
        local sh2 = sha256:new(); sh2:update(iv_bin);  local iv_fpr  = resty_str.to_hex(sh2:final())
        local res, eerr = a:encrypt(content)
        if not res then
            log(ngx.ERR, log_fmt("aes encrypt error: %s", tostring(eerr)))
        else
            if type(res) == "table" then
                enc = res[1]
                tag = res[2]
            else
                enc = res
            end
            content = enc .. (tag or "")
        end
    end

    return enc or content, key, iv_bin, tag
end

function _M.get_cache_key()
    local args = ngx.req.get_uri_args()
    local parts = {}
    for k, v in pairs(args or {}) do
        if k ~= "obf" then
            local val = v
            if type(val) == "table" then val = val[1] end
            parts[#parts + 1] = tostring(k) .. "=" .. tostring(val)
        end
    end
    table.sort(parts)
    local q = table.concat(parts, "&")
    local cache_key = (ngx.var.scheme or "") .. "://" .. (ngx.var.host or "") .. (ngx.var.uri or "") .. (q ~= "" and ("?" .. q) or "")
    return cache_key
end

-- HTML标签混淆
function _M.obf_html()
    local content_type = ngx.header.content_type or ""
    local ctx = ngx.ctx
    local chunk, eof = ngx.arg[1], ngx.arg[2]
    local html_debug = "false"
    local cache_timeout = 300

    local args = ngx.req.get_uri_args()
    obf = args and args.obf or nil
    if  obf == "debug" then
        html_debug = "true"
    end

    local var_debug = ngx.var.close_debug
    if  var_debug == "true" then
        html_debug = "false"
    end

    local var_obf_timeout = ngx.var.obf_timeout

    if var_obf_timeout then
        cache_timeout = var_obf_timeout
    end
    -- log(ngx.ERR, log_fmt("var_obf_timeout: %s", tostring(var_obf_timeout)))


    if not ctx.obf_buffer then
        ctx.obf_buffer = {}
    end

    if chunk and chunk ~= "" then
        ctx.obf_buffer[#ctx.obf_buffer + 1] = chunk
        ngx.arg[1] = nil
    end

    if eof then
        local content = table.concat(ctx.obf_buffer)

        if find(content_type, "text/html") then

            local cache_key = _M.get_cache_key()..html_debug
            local cached = obf_cache and obf_cache:get(cache_key)
            if cached then
                ngx.arg[1] = cached
                ctx.obf_buffer = nil
                return
            end

            -- local t0 = ngx.now()
            local content,key,iv,tag = _M.obf_encode(content)
            -- local t1 = ngx.now()

            local content_data = _M.to_uint8array(content or "")
            local iv_data = _M.to_uint8array(iv or "")
            local tag_data = _M.to_uint8array(tag or "")
            local key_data = _M.to_uint8array(key or "")

            local html_data = tpl.content(content_data, iv_data, tag_data, key_data,html_debug)

            html_data = _M.obf_rand(html_data)
            html_data = _M.obf_add_data(html_data)
            if obf_cache then
                obf_cache:set(cache_key, html_data, cache_timeout)
            end
            ngx.arg[1] = html_data
        end
        
        ctx.obf_buffer = nil
    end
end


function _M.done()
    local content_type = ngx.header.content_type or ""
    if find(content_type, "text/html") then
        _M.obf_html()
    end
end   
-- 响应处理函数
function _M.process_response()

    local var_close = ngx.var.close_close
    -- log(ngx.ERR, log_fmt("var_close: %s", tostring(var_close)))
    if var_close == "true" then
        _M.done()
        return
    else
        local args = ngx.req.get_uri_args()
        local obf = args and args.obf or nil
        if  obf == "close" then
            return
        end
    end

    _M.done()
    
end

return _M

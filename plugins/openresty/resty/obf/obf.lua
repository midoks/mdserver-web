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
local util = require "resty.obf.util"
local obf_cache = lrucache.new(4096)

local find = string.find
local byte = string.byte
local log = ngx.log


function _M.new(self)
    local self = {
    }
    return setmetatable(self, mt)
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
    local cache_timeout = 600

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

            local content,key,iv,tag = _M.obf_encode(content)

            local content_data = util.to_uint8array(content or "")
            local iv_data = util.to_uint8array(iv or "")
            local tag_data = util.to_uint8array(tag or "")
            local key_data = util.to_uint8array(key or "")

            local html_data = tpl.content(content_data, iv_data, tag_data, key_data,html_debug)
            html_data = util.obf_add_data(html_data)

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
    local content_type = ngx.header.content_type or ""
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

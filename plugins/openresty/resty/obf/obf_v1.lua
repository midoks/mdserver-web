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
    
-- 响应处理函数
function _M.process_response()
    local ctx = ngx.ctx
    local chunk, eof = ngx.arg[1], ngx.arg[2]

    if not ctx.obf_buffer then
        ctx.obf_buffer = {}
    end

    if chunk and chunk ~= "" then
        ctx.obf_buffer[#ctx.obf_buffer + 1] = chunk
        ngx.arg[1] = nil
    end

    if eof then
        local content = table.concat(ctx.obf_buffer)
        local enc, tag, iv_bin
        local content_type = ngx.header.content_type or ""
        local upstream_ct = ngx.var.upstream_http_content_type or ""
        local cl = ngx.header["Content-Length"] or ""
        local upstream_cl = ngx.var.upstream_http_content_length or ""

        -- log(ngx.ERR, log_fmt("proxy content-type: %s, upstream_content_type: %s", tostring(content_type), tostring(upstream_ct)))
        -- log(ngx.ERR, log_fmt("content-length: %s, upstream_content_length: %s", tostring(cl), tostring(upstream_cl)))
        -- log(ngx.ERR, log_fmt("body len=%s", tostring(#content)))
        
        -- log(ngx.ERR, log_fmt("body: %s", content))

        local password = random.bytes(8, true)
        log(ngx.ERR, log_fmt("enc=aes-256-gcm, pass_b64=%s", ngx.encode_base64(password)))
        local cipher = aes.cipher(256, "gcm")
        local a, aerr = aes:new(password, nil, cipher, aes.hash.md5, 1, 12, true)
        if not a then
            log(ngx.ERR, log_fmt("aes init error: %s", tostring(aerr)))
        else
            local key_bin = ffi_str(a._key, 32)
            iv_bin = ffi_str(a._iv, 12)
            local sh1 = sha256:new(); sh1:update(key_bin); local key_fpr = resty_str.to_hex(sh1:final())
            local sh2 = sha256:new(); sh2:update(iv_bin);  local iv_fpr  = resty_str.to_hex(sh2:final())
            log(ngx.ERR, log_fmt("key_len=%d, key_sha256=%s", 32, key_fpr))
            log(ngx.ERR, log_fmt("iv_len=%d, iv_sha256=%s", 12, iv_fpr))
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

                local b64_ct = ngx.encode_base64(enc:sub(1, math.min(#enc, 128)))
                local b64_tag = tag and ngx.encode_base64(tag) or ""
                log(ngx.ERR, log_fmt("ciphertext len=%s, tag_len=%s, b64_ct_preview=%s, b64_tag=%s", tostring(#enc), tostring(tag and #tag or 0), b64_ct, b64_tag))
            end
        end

        -- local preview = content
        -- if #preview > 2048 then
        --     preview = preview:sub(1, 2048)
        -- end
        -- log(ngx.ERR, log_fmt("body preview: %s", preview))
        
        -- 根据内容类型进行混淆
        if find(content_type, "text/html") then
            
            -- content = obfuscate_html(content)
        end
        
        local data = _M.to_uint8array(enc or content)
        local iv_data = _M.to_uint8array(iv_bin or "")
        local tag_data = _M.to_uint8array(tag or "")
        local key_data = _M.to_uint8array(password or "")
        -- content type will be set in header_filter phase
        -- ngx.arg[1] = literal

        html_data = tpl.content(data, iv_data, tag_data, key_data)

        html_data = html_data:gsub("<script(.-)>(.-)</script>", function(attrs, body)
            local b = body
            b = b:gsub("^%s*//[^\n\r]*", "")
            b = b:gsub("\n%s*//[^\n\r]*", "\n")
            b = b:gsub("([^:])%s+//[^\n\r]*", "%1")
            b = b:gsub("%s+", " ")
            b = b:gsub("%s*([%(%),;:%{%}%[%]%+%-%*%/%=<>])%s*", "%1")
            return "<script" .. attrs .. ">" .. b .. "</script>"
        end)

        ngx.arg[1] = html_data:gsub("[\r\n]+", ""):gsub(">%s+<", "><")
        ctx.obf_buffer = nil
    end
end

return _M

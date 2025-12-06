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
local util = require "resty.obf.util"
local obf_cache = ngx.shared.obf_cache
local obf_cache_bytes = 0

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
    
    local html_debug = "false"
    local cache_timeout = 600

    local args = ngx.req.get_uri_args()
    obf = args and args.obf or nil
    if  obf == "debug" then
        html_debug = "true"
    end

    local close_debug = ngx.var.close_debug
    if  close_debug == "true" then
        html_debug = "false"
    end

    local var_obf_timeout = ngx.var.obf_timeout
    if var_obf_timeout then
        cache_timeout = var_obf_timeout
    end
    -- log(ngx.ERR, log_fmt("var_obf_timeout: %s", tostring(var_obf_timeout)))

    if not ctx.obf_buffer then
        ctx.obf_buffer = {}
        ctx.obf_passthrough = false
    end

    local chunk, eof = ngx.arg[1], ngx.arg[2]
    if chunk and chunk ~= "" then
        if not ctx.obf_first_t then
            ctx.obf_first_t = util.tmark()
        end
        if ctx.obf_passthrough then
            ngx.arg[1] = chunk
        else
            ctx.obf_buffer[#ctx.obf_buffer + 1] = chunk
            
            ngx.arg[1] = nil
        end
    end
    

    if eof then
        if ctx.obf_passthrough then
            return
        end
        local prof = ngx.var.obf_prof
        local t_all0 = util.tmark()
        local content = table.concat(ctx.obf_buffer)
        local obf_cache = ngx.shared.obf_cache

        if find(content_type, "text/html", 1, true) then

            local var_rand_var = ngx.var.obf_rand_var
            local var_b64 = ngx.var.obf_uint8_b64
            local cache_key = _M.get_cache_key()..tostring(html_debug)..tostring(var_rand_var)..tostring(var_b64)
            local cached = obf_cache and obf_cache:get(cache_key)
            if cached then
                if prof == "true" then
                    log(ngx.ERR, log_fmt("obf_prof cache_hit=1 size=%d total_ms=%.2f wait_ms=%.2f", #cached, util.dt_ms(t_all0), ctx.obf_first_t and util.dt_ms(ctx.obf_first_t) or 0))
                end
                ngx.arg[1] = cached
                ctx.obf_buffer = nil
                return
            else
                if prof == "true" then
                    log(ngx.ERR, log_fmt("obf_prof cache_miss=1"))
                end
            end
            


            local t_enc0 = util.tmark()
            local content,key,iv,tag = _M.obf_encode(content)
            local enc_ms = util.dt_ms(t_enc0)

            local t_ser0 = util.tmark()
            local content_data = util.to_uint8array(content or "")
            local iv_data = util.to_uint8array(iv or "")
            local tag_data = util.to_uint8array(tag or "")
            local key_data = util.to_uint8array(key or "")
            local ser_ms = util.dt_ms(t_ser0)

            local t_tpl0 = util.tmark()
            local html_data = tpl.content(content_data, iv_data, tag_data, key_data,tostring(html_debug))
            local tpl_ms = util.dt_ms(t_tpl0)

            local max_item = tonumber(ngx.var.obf_cache_item_max) or 0
            local max_bytes = tonumber(ngx.var.obf_cache_max_bytes) or 0
            local exptime = tonumber(cache_timeout) or 600
            if obf_cache then
                if max_item <= 0 or #html_data <= max_item then
                    if max_bytes > 0 and (obf_cache_bytes + #html_data) > max_bytes then
                        obf_cache:flush_all()
                        obf_cache_bytes = 0
                    end
                    obf_cache:set(cache_key, html_data, exptime)
                    obf_cache_bytes = obf_cache_bytes + #html_data
                end
            end
            
            if prof == "true" then
                log(ngx.ERR, log_fmt("obf_prof size=%d enc_ms=%.2f ser_ms=%.2f tpl_ms=%.2f total_ms=%.2f wait_ms=%.2f", #content, enc_ms, ser_ms, tpl_ms, util.dt_ms(t_all0), ctx.obf_first_t and util.dt_ms(ctx.obf_first_t) or 0))
            end
            ngx.arg[1] = html_data
        end
        
        ctx.obf_buffer = nil
        ctx.obf_passthrough = nil
    end
end


function _M.done()
    local content_type = ngx.header.content_type or ""
    if find(content_type, "text/html") then
        local prof = ngx.var.obf_prof
        local t_start = util.tmark()
        _M.obf_html()
        if prof == "true" then
            log(ngx.ERR, log_fmt("total_ms=%.2f", util.dt_ms(t_start)))
        end
    else
        if ngx.var.obf_prof == "true" then
            log(ngx.ERR, log_fmt("obf_prof skip_ct=1 ct=%s", tostring(content_type)))
        end
    end
end   
-- 响应处理函数
function _M.process_response()
    local content_type = ngx.header.content_type or ""
    local var_close = ngx.var.close_close
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

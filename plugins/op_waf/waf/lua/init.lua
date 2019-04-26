local cpath = "{$WAF_PATH}/"
local logdir = "{$ROOT_PATH}/wwwlogs/waf/"
local json = require "cjson"

function return_message(status,msg)
    ngx.header.content_type = "application/json;"
    ngx.status = status
    ngx.say(json.encode(msg))
    ngx.exit(status)
end


function return_html(status,html)
    ngx.header.content_type = "text/html"
    ngx.status = status
    ngx.say(html)
    ngx.exit(status)
end

function read_file_body(filename)
    fp = io.open(filename,'r')
    if fp == nil then
        return nil
    end
    fbody = fp:read("*a")
    fp:close()
    if fbody == '' then
        return nil
    end
    return fbody
end


-- local config = read_file_body(cpath .. 'config.json')
local config = json.decode(read_file_body(cpath .. 'config.json'))
-- local site_config = json.decode(read_file_body(cpath .. 'site.json'))


-- function args()
--     if not config['get']['open'] or not is_site_config('get') then return false end 
--     if is_ngx_match(args_rules,uri_request_args,'args') then
--         write_log('args','regular')
--         return_html(config['get']['status'],get_html)
--         return true
--     end
--     return false
-- end

function waf()
    -- return_html(200,cpath .. 'config.json')
    return_message(200, config)
end

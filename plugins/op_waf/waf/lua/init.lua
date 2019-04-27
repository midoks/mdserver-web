
local cpath = "{$WAF_PATH}/"
local rpath = "{$WAF_PATH}/rule/"
local logdir = "{$ROOT_PATH}/wwwlogs/waf/"
local json = require "cjson"
local ngx_match = ngx.re.find

local _C = require "common"
local C = _C.new(cpath, rpath, logdir)


function write_drop_ip(is_drop,drop_time)
    local filename = cpath .. 'drop_ip.log'
    local fp = io.open(filename,'ab')
    if fp == nil then return false end
    local logtmp = {os.time(),ip,server_name,request_uri,drop_time,is_drop}
    local logstr = json.encode(logtmp) .. "\n"
    fp:write(logstr)
    fp:flush()
    fp:close()
    return true
end




local config = C:read_file_body_decode(cpath .. 'config.json')
local site_config = C:read_file_body_decode(cpath .. 'site.json')

C.setConfData(config, site_config)


local args_rules = C:read_file_table('args')

local retry = config['retry']
local retry_time = config['retry_time']
local retry_cycle = config['retry_cycle']
local ip = C:get_client_ip()
local server_name = string.gsub(C:get_server_name(),'_','.')



function waf_args()
    uri_request_args = ngx.req.get_uri_args()
    if not config['get']['open'] or not C:is_site_config('get') then return false end
    if C:is_ngx_match(args_rules,uri_request_args,'args') then
        ngx.say('okkkkkooo')
        C:write_log(ip,'args','regular')
        C:return_html(config['get']['status'],get_html)
        return true
    end
    return false
end

function waf()
    ngx.header.content_type = "text/plain"
    waf_args()
    C:return_html(200, '11')
    -- return_message(200, config)
end

waf()

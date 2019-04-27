
local cpath = "{$WAF_PATH}/"
local rpath = "{$WAF_PATH}/rule/"
local logdir = "{$ROOT_PATH}/wwwlogs/waf/"
local json = require "cjson"
local ngx_match = ngx.re.find

local _C = require "common"
local C = _C:new(cpath, rpath, logdir)

local config = C:read_file_body_decode(cpath .. 'config.json')
local site_config = C:read_file_body_decode(cpath .. 'site.json')
C:setConfData(config, site_config)


local get_html = C:read_file_body(config["reqfile_path"] .. '/' .. config["get"]["reqfile"])
local args_rules = C:read_file_table('args')

local ip_white_rules = C:read_file('ip_white')


function initParams()
    local data = {}
    data['ip'] = C:get_client_ip()
    data['request_header'] = ngx.req.get_headers()
    data['uri'] = ngx.unescape_uri(ngx.var.uri)
    data['server_name'] = string.gsub(C:get_server_name(),'_','.')
    data['uri_request_args'] = ngx.req.get_uri_args()
    return data
end

local params = initParams()
C:setParams(params)

-- function min_route()
--     if ngx.var.remote_addr ~= '127.0.0.1' then return false end
--     if uri == '/get_waf_drop_ip' then
--         return_message(200,get_waf_drop_ip())
--     elseif uri == '/remove_waf_drop_ip' then
--         return_message(200,remove_waf_drop_ip())
--     elseif uri == '/clean_waf_drop_ip' then
--         return_message(200,clean_waf_drop_ip())
--     end
-- end

function waf_args()
    if not config['get']['open'] or not C:is_site_config('get') then return false end
    if C:is_ngx_match(args_rules, params['uri_request_args'],'args') then
        C:write_log('args','regular')
        C:return_html(config['get']['status'], get_html)
        return true
    end
    return false
end

ngx.header.content_type = "text/html"
function waf()
    waf_args()
end

waf()

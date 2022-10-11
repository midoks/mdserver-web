local json = require "cjson"
local ngx_match = ngx.re.find

local __C = require "common"
local C = __C:new()

local waf_root = "{$WAF_ROOT}"

config = C:read_file_body_decode(waf_root.."/waf/"..'config.json')
local site_config = C:read_file_body_decode(waf_root.."/waf/"..'site.json')
C:setConfData(config, site_config)
C:setDebug(true)


local get_html = C:read_file_body(config["reqfile_path"] .. '/' .. config["get"]["reqfile"])
local post_html = C:read_file_body(config["reqfile_path"] .. '/' .. config["post"]["reqfile"])
local user_agent_html = C:read_file_body(config["reqfile_path"] .. '/' .. config["user-agent"]["reqfile"])
local cc_safe_js_html = C:read_file_body(config["reqfile_path"] .. '/' .. config["cc"]["reqfile"])
local args_rules = C:read_file_table('args')
local ip_white_rules = C:read_file('ip_white')
local ip_black_rules = C:read_file('ip_black')
local ipv6_black_rules = C:read_file('ipv6_black')
local scan_black_rules = C:read_file('scan_black')
local user_agent_rules = C:read_file('user_agent')
local post_rules = C:read_file('post')
local cookie_rules = C:read_file('cookie')


local server_name = string.gsub(C:get_server_name(),'_','.')


function initParams()
    local data = {}
    data['server_name'] = server_name
    data['ip'] = C:get_real_ip(server_name)
    data['ipn'] = C:arrip(data['ip'])
    data['request_header'] = ngx.req.get_headers()
    data['uri'] = ngx.unescape_uri(ngx.var.uri)
    data['uri_request_args'] = ngx.req.get_uri_args()
    data['method'] = ngx.req.get_method()
    data['request_uri'] = ngx.var.request_uri
    data['cookie'] = ngx.var.http_cookie
    return data
end

local params = initParams()
C:setParams(params)

function get_return_state(rstate,rmsg)
    result = {}
    result['status'] = rstate
    result['msg'] = rmsg
    return result
end

function get_waf_drop_ip()
    local data =  ngx.shared.drop_ip:get_keys(0)
    return data
end


math.randomseed(os.time())
 
function get_random(n) 
    local t = {
        "0","1","2","3","4","5","6","7","8","9",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z",
        "A","B","C","D","E","F","G","H","I","J",
        "K","L","M","N","O","P","Q","R","S","T",
        "U","V","W","X","Y","Z",
    }    
    local s = ""
    for i =1, n do
        s = s .. t[math.random(#t)]        
    end
    return s
end

function is_chekc_table(data,strings)
    if type(data) ~= 'table' then return 1 end 
    if not data then return 1 end
    data=chekc_ip_timeout(data)
    for k,v in pairs(data)
    do
        if strings ==v['ip'] then
            return 3
        end
    end
    return 2
end

function save_ip_on(data)
    locak_file=read_file_body(cpath2 .. 'stop_ip.lock')
    if not locak_file then
        C:write_file(cpath2 .. 'stop_ip.lock','1')
    end
    name='stop_ip'
    local extime=18000
    data=json.encode(data)
    ngx.shared.btwaf:set(cpath2 .. name,data,extime)
    if not ngx.shared.btwaf:get(cpath2 .. name .. '_lock') then
        ngx.shared.btwaf:set(cpath2 .. name .. '_lock',1,0.5)
        C:write_file(cpath2 .. name .. '.json',data)
    end
end

function remove_waf_drop_ip()
    if not uri_request_args['ip'] or not C:is_ipaddr(uri_request_args['ip']) then return get_return_state(true,'格式错误') end
    if ngx.shared.btwaf:get(cpath2 .. 'stop_ip') then
        ret=ngx.shared.btwaf:get(cpath2 .. 'stop_ip')
        ip_data=json.decode(ret)
        result = is_chekc_table(ip_data,uri_request_args['ip'])
        os.execute("sleep " .. 0.6)
        ret2=ngx.shared.btwaf:get(cpath2 .. 'stop_ip')
        ip_data2 = json.decode(ret2)
        if result == 3 then
            for k,v in pairs(ip_data2)
            do
                if uri_request_args['ip'] == v['ip'] then 
                    v['time'] = 0
                end
            end
        end
        save_ip_on(ip_data2)
    end
    ngx.shared.drop_ip:delete(uri_request_args['ip'])
    return get_return_state(true,uri_request_args['ip'] .. '已解封')
end

function clean_waf_drop_ip()
    if ngx.shared.btwaf:get(cpath2 .. 'stop_ip') then
        ret2=ngx.shared.btwaf:get(cpath2 .. 'stop_ip')
        ip_data2=json.decode(ret2)
        for k,v in pairs(ip_data2)
        do
                v['time']=0
        end
        save_ip_on(ip_data2)
        os.execute("sleep " .. 2)
    end
    local data = get_btwaf_drop_ip()
    for _,value in ipairs(data)
    do
        ngx.shared.drop_ip:delete(value)
    end
    return get_return_state(true,'已解封所有封锁IP')
end

function min_route()
    if ngx.var.remote_addr ~= '127.0.0.1' then return false end
    if uri == '/get_waf_drop_ip' then
        return_message(200,get_waf_drop_ip())
    elseif uri == '/remove_waf_drop_ip' then
        return_message(200,remove_waf_drop_ip())
    elseif uri == '/clean_waf_drop_ip' then
        return_message(200,clean_waf_drop_ip())
    end
end

function waf_get_args()
    if not config['get']['open'] or not C:is_site_config('get') then return false end
    if C:is_ngx_match(args_rules, params['uri_request_args'],'args') then
        C:write_log('args','regular')
        C:return_html(config['get']['status'], get_html)
        return true
    end
    return false
end


function waf_ip_white()
    for _,rule in ipairs(ip_white_rules)
    do
        if C:compare_ip(rule) then 
            return true 
        end
    end
    return false
end

function waf_ip_black()
    
    -- ipv4 ip black
    for _,rule in ipairs(ip_black_rules)
    do
        if C:compare_ip(rule) then 
            ngx.exit(config['cc']['status'])
            return true 
        end
    end

    -- ipv6 ip black
    for _,rule in ipairs(ipv6_black_rules)
    do
        if rule == params['ip'] then 
            ngx.exit(config['cc']['status'])
            return true 
        end
    end
    return false
end


function waf_user_agent()
    -- user_agent 过滤
    if not config['user-agent']['open'] or not C:is_site_config('user-agent') then return false end
    if C:is_ngx_match_ua(user_agent_rules,params['request_header']['user-agent']) then
        C:write_log('user_agent','regular')
        C:return_html(config['user-agent']['status'],user_agent_html)
        return true
    end
    return false
end


function waf_drop()
    local count , _ = ngx.shared.drop_ip:get(ip)
    if not count then return false end
    if count > config['retry'] then
        ngx.exit(config['cc']['status'])
        return true
    end
    return false
end

function waf_cc()
    local ip = params['ip']

    local ip_lock = ngx.shared.drop_ip:get(ip)
    if ip_lock then
        if ip_lock > 0 then
            ngx.exit(config['cc']['status'])
            return true
        end
    end

    if not config['cc']['open'] or not C:is_site_config('cc') then return false end


    local request_uri = params['request_uri']
    local endtime = config['cc']['endtime']

    local token = ngx.md5(ip .. '_' .. request_uri)
    local count = ngx.shared.limit:get(token)

    local limit = config['cc']['limit']
    local cycle = config['cc']['cycle']

    if count then
        if count > limit then 

            local safe_count, _ = ngx.shared.drop_sum:get(ip)
            if not safe_count then
                ngx.shared.drop_sum:set(ip,1,86400)
                safe_count = 1
            else
                ngx.shared.drop_sum:incr(ip,1)
            end
            local lock_time = (endtime * safe_count)
            if lock_time > 86400 then lock_time = 86400 end

            -- lock_time = 10
            ngx.shared.drop_ip:set(ip,1,lock_time)

            C:write_log('cc',cycle..'秒内累计超过'..limit..'次请求,封锁' .. lock_time .. '秒')
            C:write_drop_ip('cc',lock_time)
            ngx.exit(config['cc']['status'])
            return true
        else
            ngx.shared.limit:incr(token,1)
        end
    else
        ngx.shared.drop_sum:set(ip,1,86400)
        ngx.shared.limit:set(token, 1, cycle)
    end
    return false
end

-- 是否符合开强制验证条件
function is_open_waf_cc_increase()

    if config['safe_verify']['open'] then
        return true
    end

    if site_config[server_name]['safe_verify']['open'] then
        return true
    end
    return false
end


--强制验证是否使用正常浏览器访问网站
function waf_cc_increase()
    local ip = params['ip']
    local uri = params['uri']

    if not is_open_waf_cc_increase() then return false end
    local cache_token = ngx.md5(ip .. '_' .. server_name)

    --判断是否已经通过验证
    if ngx.shared.limit:get(cache_token) then return false end

    local cache_rand_key = ip..':rand'
    local cache_rand = ngx.shared.limit:get(cache_rand_key)
    if not cache_rand then 
        cache_rand = get_random(8)
        ngx.shared.limit:set(cache_rand_key,cache_rand,10)
    end

    make_uri_str = "unbind_"..cache_rand.."_"..cache_token
    make_uri = "/"..make_uri_str
    if uri == make_uri then
        ngx.shared.limit:set(cache_token,1, config['safe_verify']['time'])
        C:return_message(200, get_return_state(0,'ok'))
    end

    local cc_html = ngx.re.gsub(cc_safe_js_html, "{uri}", make_uri_str)
    C:return_html(200, cc_html)
end


function waf_url()
    if not config['get']['open'] or not C:is_site_config('get') then return false end
    --正则--
    if C:is_ngx_match(url_rules,params["uri"],'url') then
        C:write_log('url','regular')
        C:return_html(config['get']['status'],get_html)
        return true
    end
    return false
end


function waf_scan_black()
    -- 扫描软件禁止
    if not config['scan']['open'] or not C:is_site_config('scan') then return false end
    if not params["cookie"] then
        if C:ngx_match_string(scan_black_rules['cookie'], tostring(params["cookie"]),'scan') then
            C:write_log('scan','regular')
            ngx.exit(config['scan']['status'])
            return true
        end
    end

    if C:ngx_match_string(scan_black_rules['args'], params["request_uri"], 'scan') then
        C:write_log('scan','regular')
        ngx.exit(config['scan']['status'])
        return true
    end

    for key,value in pairs(params["request_header"])
    do
        if C:ngx_match_string(scan_black_rules['header'], key, 'scan') then
            C:write_log('scan','regular')
            ngx.exit(config['scan']['status'])
            return true
        end
    end
    return false
end

function waf_post()
    if not config['post']['open'] or not C:is_site_config('post') then return false end   
    if params['method'] ~= "POST" then return false end
    content_length = tonumber(params["request_header"]['content-length'])
    max_len = 640 * 1020000
    if content_length > max_len then return false end
    if C:get_boundary() then return false end
    ngx.req.read_body()
    request_args = ngx.req.get_post_args()
    if not request_args then
        return false
    end

    for key, val in pairs(request_args) do
        if type(val) == "table" then
            if type(val[1]) == "boolean" then
                return false
            end
            data = table.concat(val, ", ")
        else
            data = val
        end
        
    end

    if C:is_ngx_match_post(post_rules,data) then
        C:write_log('post','regular')
        C:return_html(config['post']['status'],post_html)
        return true
    end
    return false
end


function  post_data_chekc()
    if params['method'] =="POST" then
        if C:return_post_data() then return false end
        ngx.req.read_body()
        request_args = ngx.req.get_post_args()
        if not request_args then return false end

        if request_header then
            if not request_header['Content-Type'] then return false end
            av = string.match(request_header['Content-Type'],"=.+")
        end

        if not av then return false end
        ac = split(av,'=')

        if not ac then return false end 

        list_list=nil
        for i,v in ipairs(ac)
        do
             list_list='--'..v
        end
        
        if not list_list then return false end 
        
        aaa = nil
        for k,v in pairs(request_args)
        do
            aaa = v
        end

        if not aaa then return false end 
        if tostring(aaa) == 'true' then return false end
        if type(aaa) ~= "string" then return false end
        data_len=split(aaa,list_list)
        
        --return return_message(200,data_len)
        if not data_len then return false end
        if arrlen(data_len) ==0 then return false end

        if C:is_ngx_match_post(post_rules , data_len) then
            C:write_log('post','regular')
            C:return_html(config['post']['status'],post_html)
            return true
        end

    end
end


function X_Forwarded()
    if params['method'] ~= "GET" then return false end
    if not config['get']['open'] or not C:is_site_config('get') then return false end 
    if C:is_ngx_match(args_rules,params["request_header"]['X-forwarded-For'],'args') then
        C:write_log('args','regular')
        C:return_html(config['get']['status'],get_html)
        return true
    end
    return false
end


function post_X_Forwarded()
    if not config['post']['open'] or not C:is_site_config('post') then return false end   
    if params['method'] ~= "POST" then return false end
    if C:is_ngx_match_post(post_rules,params["request_header"]['X-forwarded-For']) then
        C:write_log('post','regular')
        C:return_html(config['post']['status'],post_html)
        return true
    end
    return false
end


-- function php_path()
--     if site_config[server_name] == nil then return false end
--     for _,rule in ipairs(site_config[server_name]['disable_php_path'])
--     do
--         if C:ngx_match_string(params['uri'],rule .. "/?.*\\.php$","isjo") then
--             C:write_log('php_path','regular')
--             C:return_html(config['other']['status'],other_html)
--             return C:return_message(200,uri)
--         end
--     end
--     return false
-- end

-- function url_path()
--     if site_config[server_name] == nil then return false end
--     for _,rule in ipairs(site_config[server_name]['disable_path'])
--     do
--         if ngx_match(uri,rule,"isjo") then
--             C:write_log('path','regular')
--             C:return_html(config['other']['status'],other_html)
--             return true
--         end
--     end
--     return false
-- end

function url_ext()
    if site_config[server_name] == nil then return false end
    for _,rule in ipairs(site_config[server_name]['disable_ext'])
    do
        if C:ngx_match_string("\\."..rule.."$", params['uri'],'url_ext') then
            C:write_log('url_ext','regular')
            C:return_html(config['other']['status'], other_html)
            return true
        end
    end
    return false
end

function url_rule_ex()
    if site_config[server_name] == nil then return false end
    if method == "POST" and not request_args then
        content_length=tonumber(request_header['content-length'])
        max_len = 640 * 102400000
        request_args = nil
        if content_length < max_len then
            ngx.req.read_body()
            request_args = ngx.req.get_post_args()
        end
    end
    for _,rule in ipairs(site_config[server_name]['url_rule'])
    do
        if ngx_match(uri,rule[1],"isjo") then
            if C:is_ngx_match(rule[2],uri_request_args,false) then
                C:write_log('url_rule','regular')
                C:return_html(config['other']['status'],other_html)
                return true
            end
            
            if params['method'] == "POST" and request_args ~= nil then 
                if C:is_ngx_match(rule[2],request_args,'post') then
                    C:write_log('post','regular')
                    C:return_html(config['other']['status'],other_html)
                    return true
                end
            end
        end
    end
    return false
end

function url_tell()
    if site_config[server_name] == nil then return false end
    for _,rule in ipairs(site_config[server_name]['url_tell'])
    do
        if ngx_match(uri,rule[1],"isjo") then
            if uri_request_args[rule[2]] ~= rule[3] then
                C:write_log('url_tell','regular')
                C:return_html(config['other']['status'],other_html)
                return true
            end
        end
    end
    return false
end


function disable_upload_ext(ext)
    if not ext then return false end
    ext = string.lower(ext)
    if is_key(site_config[server_name]['disable_upload_ext'],ext) then
        C:write_log('upload_ext','上传扩展名黑名单')
        C:return_html(config['other']['status'],other_html)
        return true
    end
end

function data_in_php(data)
    if not data then
        return false
    else
        if C:is_ngx_match('php',data,'post') then
            C:write_log('upload_ext','上传扩展名黑名单')
            C:return_html(config['other']['status'],other_html)
            return true
        else
            return false
        end
    end
end

function post_data()
    if params["method"] ~= "POST" then return false end
    content_length = tonumber(params["request_header"]['content-length'])
    if not content_length then return false end
    max_len = 2560 * 1024000
    if content_length > max_len then return false end
    local boundary = C:get_boundary()
    if boundary then
        ngx.req.read_body()
        local data = ngx.req.get_body_data()
        if not data then return false end
        local tmp = ngx.re.match(data,[[filename=\"(.+)\.(.*)\"]])
        if not tmp then return false end
        if not tmp[2] then return false end
        local tmp2=ngx.re.match(ngx.req.get_body_data(),[[Content-Type:[^\+]{45}]]) 
        --return return_message(200,tmp2[0])
        disable_upload_ext(tmp[2])
        if tmp2 == nil then return false end 
        data_in_php(tmp2[0])
        
    end
    return false
end

function waf_cookie()
    if not config['cookie']['open'] or not C:is_site_config('cookie') then return false end
    if not params["request_header"]['cookie'] then return false end
    if type(params["request_header"]['cookie']) ~= "string" then return false end
    request_cookie = string.lower(params["request_header"]['cookie'])
    if C:ngx_match_list(cookie_rules,request_cookie,'cookie') then
        C:write_log('cookie','regular')
        C:return_html(config['cookie']['status'],cookie_html)
        return true
    end
    return false
end


function waf()
    min_route()

    -- white ip
    if waf_ip_white() then return true end

    -- black ip
    if waf_ip_black() then return true end


    -- cc setting
    if waf_drop() then return true end
    if waf_cc_increase() then return true end
    if waf_cc() then return true end

    -- ua check
    if waf_user_agent() then return true end
    if waf_url() then return true end

    -- cookie检查
    if waf_cookie() then return true end
    
    -- args参数拦截
    if waf_get_args() then return true end

    -- 扫描软件禁止
    if waf_scan_black() then return true end

    if waf_post() then return true end
    if post_data_chekc() then return true end
    
    if site_config[server_name]['open'] then
        if X_Forwarded() then return true end
        if post_X_Forwarded() then return true end
        -- url_path()
        if url_ext() then return true end
        -- url_rule_ex()
        -- url_tell()
        -- post_data()
    end
end

waf()
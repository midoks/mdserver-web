
local cpath = "{$WAF_PATH}/"
local rpath = "{$WAF_PATH}/rule/"
local logdir = "{$ROOT_PATH}/wwwlogs/waf/"
local json = require "cjson"
local ngx_match = ngx.re.find

local _C = require "common"
local C = _C.new(cpath, rpath)


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


ngx.header.content_type = "text/plain"

local config = C:read_file_body_decode(cpath .. 'config.json')
local site_config = C:read_file_body_decode(cpath .. 'site.json')





function get_client_ip()
    local client_ip = "unknown"
    if site_config[server_name] then
        if site_config[server_name]['cdn'] then
            for _,v in ipairs(site_config[server_name]['cdn_header'])
            do
                if request_header[v] ~= nil and request_header[v] ~= "" then
                    local header_tmp = request_header[v]
                    if type(header_tmp) == "table" then header_tmp = header_tmp[1] end
                    client_ip = split(header_tmp,',')[1]
                    break;
                end
            end 
        end
    end
    if string.match(client_ip,"%d+%.%d+%.%d+%.%d+") == nil or not is_ipaddr(client_ip) then
        client_ip = ngx.var.remote_addr
        if client_ip == nil then
            client_ip = "unknown"
        end
    end
    return client_ip
end


function get_server_name()
    local c_name = ngx.var.server_name
    local my_name = ngx.shared.limit:get(c_name)
    if my_name then return my_name end
    local tmp = C:read_file_body(cpath .. 'domains.json')
    if not tmp then return c_name end
    local domains = json.decode(tmp)
    for _,v in ipairs(domains)
    do
        for _,d_name in ipairs(v['domains'])
        do
            if c_name == d_name then
                ngx.shared.limit:set(c_name,v['name'],3600)
                return v['name']
            end
        end
    end
    return c_name
end

local args_rules = C:select_rule(C:read_file('args'))

local retry = config['retry']
local retry_time = config['retry_time']
local retry_cycle = config['retry_cycle']
local ip
local server_name


function continue_key(key)
    key = tostring(key)
    if string.len(key) > 64 then return false end;
    local keys = {"content","contents","body","msg","file","files","img","newcontent"}
    for _,k in ipairs(keys)
    do
        ngx.say(k..'---'..key)
        if k == key then return false end;
    end
    ngx.say('ok:'..key)
    return true;
end

function is_ngx_match(rules,sbody,rule_name)

    ngx.say(rules)
    if rules == nil or sbody == nil then return false end
    if type(sbody) == "string" then
        sbody = {sbody}
    end
    
    if type(rules) == "string" then
        rules = {rules}
    end

    for k,body in pairs(sbody)
    do
        ngx.say('k:'..k..',body:'..body..tostring(continue_key(k)))
        if continue_key(k) then
            ngx.say('ddddd-----dddd')
            for i,rule in ipairs(rules)
            do
                ngx.say('i:'..i..',body:'..rule)
                if site_config[server_name] and rule_name then
                    local n = i - 1
                    for _,j in ipairs(site_config[server_name]['disable_rule'][rule_name])
                    do
                        if n == j then
                            rule = ""
                        end
                    end
                end
                
                if body and rule ~="" then
                    if type(body) == "string" then
                        if ngx_match(ngx.unescape_uri(body),rule,"isjo") then
                            error_rule = rule .. ' >> ' .. k .. ':' .. body
                            return true
                        end
                    end
                    if type(k) == "string" then
                        if ngx_match(ngx.unescape_uri(k),rule,"isjo") then
                            error_rule = rule .. ' >> ' .. k
                            return true
                        end
                    end
                end
            end
        end
    end
    return false
end

function is_site_config(cname)
    if site_config[server_name] ~= nil then
        if cname == 'cc' then
            return site_config[server_name][cname]['open']
        else
            return site_config[server_name][cname]
        end
    end
    return true
end

function write_file(filename,body)
    fp = io.open(filename,'w')
    if fp == nil then
        return nil
    end
    fp:write(body)
    fp:flush()
    fp:close()
    return true
end

function write_log(name,rule)
    local count,_ = ngx.shared.drop_ip:get(ip)
    if count then
        ngx.shared.drop_ip:incr(ip,1)
    else
        ngx.shared.drop_ip:set(ip,1,retry_cycle)
    end
    if config['log'] ~= true or is_site_config('log') ~= true then return false end
    local method = ngx.req.get_method()
    if error_rule then 
        rule = error_rule
        error_rule = nil
    end
    
    local logtmp = {ngx.localtime(),ip,method,request_uri,ngx.var.http_user_agent,name,rule}
    local logstr = json.encode(logtmp) .. "\n"
    local count,_ = ngx.shared.drop_ip:get(ip)  
    if count > retry and name ~= 'cc' then
        local safe_count,_ = ngx.shared.drop_sum:get(ip)
        if not safe_count then
            ngx.shared.drop_sum:set(ip,1,86400)
            safe_count = 1
        else
            ngx.shared.drop_sum:incr(ip,1)
        end
        local lock_time = retry_time * safe_count
        if lock_time > 86400 then lock_time = 86400 end
        logtmp = {ngx.localtime(),ip,method,request_uri,ngx.var.http_user_agent,name,retry_cycle .. '秒以内累计超过'..retry..'次以上非法请求,封锁'.. lock_time ..'秒'}
        logstr = logstr .. json.encode(logtmp) .. "\n"
        ngx.shared.drop_ip:set(ip,retry+1,lock_time)
        write_drop_ip('inc',lock_time)
    end
    write_to_file(logstr)
    inc_log(name,rule)
end

function inc_log(name,rule)
    local total_path = cpath .. 'total.json'
    local tbody = ngx.shared.limit:get(total_path)
    if not tbody then
        tbody = C:read_file_body(total_path)
        if not tbody then return false end
    end
    local total = json.decode(tbody)
    if not total['sites'] then total['sites'] = {} end
    if not total['sites'][server_name] then total['sites'][server_name] = {} end
    if not total['sites'][server_name][name] then total['sites'][server_name][name] = 0 end
    if not total['rules'] then total['rules'] = {} end
    if not total['rules'][name] then total['rules'][name] = 0 end
    if not total['total'] then total['total'] = 0 end
    total['total'] = total['total'] + 1
    total['sites'][server_name][name] = total['sites'][server_name][name] + 1
    total['rules'][name] = total['rules'][name] + 1
    local total_log = json.encode(total)
    if not total_log then return false end
    ngx.shared.limit:set(total_path,total_log)
    if not ngx.shared.limit:get('b_btwaf_timeout') then
        write_file(total_path,total_log)
        ngx.shared.limit:set('b_btwaf_timeout',1,5)
    end
end

function write_to_file(logstr)
    local filename = logdir .. '/' .. server_name .. '_' .. ngx.today() .. '.log'
    local fp = io.open(filename,'ab')
    if fp == nil then return false end
    fp:write(logstr)
    fp:flush()
    fp:close()
    return true
end

function args()
    uri_request_args = ngx.req.get_uri_args()
    ngx.say('123123123----111')
    if not config['get']['open'] or not is_site_config('get') then return false end
    ngx.say('123123123----22'..json.encode(uri_request_args))

    if is_ngx_match(args_rules,uri_request_args,'args') then
        ngx.say('123123123----4')
        ngx.say(get_html)
        write_log('args','regular')
        C:return_html(config['get']['status'],get_html)
        return true
    end
    return false
end

function waf()

    -- server_name = string.gsub(get_server_name(),'_','.')
    ngx.header.content_type = "text/plain"
    -- ip = get_client_ip()
    C:t()
    -- ngx.say(read_file('args'));
    -- args()
    C:return_html(200, '11')
    -- return_message(200, config)
end

waf()

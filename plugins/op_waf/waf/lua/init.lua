
local cpath = "{$WAF_PATH}/"
local rpath = cpath.."rule/"
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

function return_text(status,html)
    ngx.header.content_type = "text/plain"
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


function read_file(name)
    fbody = read_file_body(rpath .. name .. '.json')
    if fbody == nil then
        return {}
    end
    return json.decode(fbody)
end



function select_rule(rules)
    if not rules then return {} end
    new_rules = {}
    for i,v in ipairs(rules)
    do 
        if v[1] == 1 then
            table.insert(new_rules,v[2])
        end
    end
    return new_rules
end


local config = json.decode(read_file_body(cpath .. 'config.json'))
local site_config = json.decode(read_file_body(cpath .. 'site.json'))

local args_rules = select_rule(read_file('args'))

function continue_key(key)
    key = tostring(key)
    if string.len(key) > 64 then return false end;
    local keys = {"content","contents","body","msg","file","files","img","newcontent",""}
    for _,k in ipairs(keys)
    do
        if k == key then return false end;
    end
    return true;
end

function is_ngx_match(rules,sbody,rule_name)
    if rules == nil or sbody == nil then return false end
    if type(sbody) == "string" then
        sbody = {sbody}
    end
    
    if type(rules) == "string" then
        rules = {rules}
    end

    for k,body in pairs(sbody)
    do
        ngx.say('k:'..k..',body:'..body)
        if continue_key(k) then
            for i,rule in ipairs(rules)
            do
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
    local tbody = ngx.shared.btwaf:get(total_path)
    if not tbody then
        tbody = read_file_body(total_path)
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
    ngx.shared.btwaf:set(total_path,total_log)
    if not ngx.shared.btwaf:get('b_btwaf_timeout') then
        write_file(total_path,total_log)
        ngx.shared.btwaf:set('b_btwaf_timeout',1,5)
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
        write_log('args','regular')
        return_text(config['get']['status'],get_html)
        return true
    end
    return false
end

function waf()
    args()
    return_html(200, json.encode(config))
    -- return_message(200, config)
end

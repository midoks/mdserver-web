

local setmetatable = setmetatable
local _M = { _VERSION = '0.01' }
local mt = { __index = _M }
local json = require "cjson"
local ngx_match = ngx.re.find


function _M.new(cpath, rpath, logdir)
    -- ngx.log(ngx.ERR,"read:"..cpath..",rpath:"..rpath)
    local self = {
         cpath = cpath,
         rpath = rpath,
         logdir = logdir,
         config = '',
         site_config = ''
    }
    local p = setmetatable(self, mt)
    return p
end


function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config
end



function _M.return_message(self, status, msg)
    ngx.header.content_type = "application/json;"
    ngx.status = status
    ngx.say(json.encode(msg))
    ngx.exit(status)
end


function _M.return_html(self,status,html)
    ngx.header.content_type = "text/html"
    ngx.status = status
    ngx.say(html)
    ngx.exit(status)
end

function _M.read_file_body(self, filename)
    -- ngx.log(ngx.ERR,"read_file_body:"..filename)
	fp = io.open(filename, 'r')
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



function _M.write_file(self, filename, body)
    fp = io.open(filename,'w')
    if fp == nil then
        return nil
    end
    fp:write(body)
    fp:flush()
    fp:close()
    return true
end


function _M.write_to_file(logstr)
    local filename = self.logdir .. '/' .. server_name .. '_' .. ngx.today() .. '.log'
    self:write_file(filename, logstr)
    return true
end

function _M.continue_key(self,key)
    key = tostring(key)
    if string.len(key) > 64 then return false end;
    local keys = {"content","contents","body","msg","file","files","img","newcontent"}
    for _,k in ipairs(keys)
    do
        if k == key then return false end;
    end
    return true;
end


function _M.array_len(self, arr)
    if not arr then return 0 end
    local count = 0
    for _,v in ipairs(arr)
    do
        count = count + 1
    end
    return count
end

function _M.is_ipaddr(self, client_ip)
    local cipn = split(client_ip,'.')
    if self:array_len(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end


function _M.read_file_body_decode(self, filename)
    return json.decode(self:read_file_body(filename))
end

function _M.select_rule(self, rules)
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



function _M.read_file(self, name)
    f = self.rpath .. name .. '.json'   
    fbody = self:read_file_body(f)
    if fbody == nil then
        return {}
    end
    return json.decode(fbody)
end

function _M.read_file_table( self, name )
    return self:select_rule(self:read_file('args'))
end


function _M.inc_log(self, name, rule)
    local total_path = cpath .. 'total.json'
    local tbody = ngx.shared.limit:get(total_path)
    if not tbody then
        tbody = self:read_file_body(total_path)
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
        self:write_file(total_path,total_log)
        ngx.shared.limit:set('b_btwaf_timeout',1,5)
    end
end


---------------------------------------------------

function _M.get_server_name(self)
    local c_name = ngx.var.server_name
    local my_name = ngx.shared.limit:get(c_name)
    if my_name then return my_name end
    local tmp = self:read_file_body(self.cpath .. 'domains.json')
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


-- function _M.get_sn(self)
--     retun string.gsub(self:get_server_name(),'_','.')
-- end


function _M.is_ngx_match(self, rules, sbody, rule_name)
    ngx.say()
    if rules == nil or sbody == nil then return false end
    if type(sbody) == "string" then
        sbody = {sbody}
    end
    
    if type(rules) == "string" then
        rules = {rules}
    end

    for k,body in pairs(sbody)
    do
        if self:continue_key(k) then
            for i,rule in ipairs(rules)
            do
                ngx.say("i:"..i..",rule:"..rule)
                if self.site_config[server_name] and rule_name then
                    local n = i - 1
                    for _,j in ipairs(self.site_config[server_name]['disable_rule'][rule_name])
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


function _M.write_log(self, name, rule)
    ngx.say('name:'..name)
    local ip = C:get_client_ip()
    

    
    local count,_ = ngx.shared.drop_ip:get(ip)
    if count then
        ngx.shared.drop_ip:incr(ip,1)
    else
        ngx.shared.drop_ip:set(ip,1,retry_cycle)
    end
    if self.config['log'] ~= true or self:is_site_config('log') ~= true then return false end
    local method = ngx.req.get_method()
    if error_rule then 
        rule = error_rule
        error_rule = nil
    end
    

    local logtmp = {ngx.localtime(), ip, method,request_uri, ngx.var.http_user_agent, name, rule}
    ngx.say('logtmp:'..logtmp)
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
        self:write_drop_ip('inc',lock_time)
    end
    self:write_to_file(logstr)
    self:inc_log(name,rule)
end


function _M.get_client_ip(self)
    local client_ip = "unknown"
    if self.site_config[server_name] then
        if self.site_config[server_name]['cdn'] then
            for _,v in ipairs(self.site_config[server_name]['cdn_header'])
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
    if string.match(client_ip,"%d+%.%d+%.%d+%.%d+") == nil or not self:is_ipaddr(client_ip) then
        client_ip = ngx.var.remote_addr
        if client_ip == nil then
            client_ip = "unknown"
        end
    end
    return client_ip
end


function _M.is_site_config(self,cname)
    if self.site_config[server_name] ~= nil then
        if cname == 'cc' then
            return self.site_config[server_name][cname]['open']
        else
            return self.site_config[server_name][cname]
        end
    end
    return true
end


function _M.t(self)
    ngx.say(',,,')
end


return _M

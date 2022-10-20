
local setmetatable = setmetatable
local _M = { _VERSION = '0.02' }
local mt = { __index = _M }

local json = require "cjson"

local ngx_match = ngx.re.find
local debug_mode = false

local waf_root = "{$WAF_ROOT}"
local cpath = waf_root.."/waf/"
local logdir = waf_root.."/logs/"
local rpath = cpath.."/rule/"

function _M.new(self)

    local self = {
        waf_root = waf_root,
        cpath = cpath,
        rpath = rpath,
        logdir = logdir,
        config = '',
        site_config = '',
        server_name = '',
        global_tatal = nil,
        params = nil,
        db = nil,
    }
    return setmetatable(self, mt)
end


function _M.getInstance(self)
    if rawget(self, "instance") == nil then
        rawset(self, "instance", self.new())
        self.initDB()
    end
    assert(self.instance ~= nil)
    return self.instance
end

function _M.initDB(self)
    if self.db then
        return self.db
    end

    local path = log_dir .. "/waf.db"
    db, err = sqlite3.open(path)

    if err then
        self:D("initDB err:"..tostring(err))
        return nil
    end

    db:exec([[PRAGMA synchronous = 0]])
    db:exec([[PRAGMA cache_size = 8000]])
    db:exec([[PRAGMA page_size = 32768]])
    db:exec([[PRAGMA journal_mode = wal]])
    db:exec([[PRAGMA journal_size_limit = 1073741824]])

    self.db = db
    return db
end

function _M.setDebug(self, mode)
    debug_mode = mode
end


-- 调试方式
function _M.D(self, msg)

    if not debug_mode then return true end

    local _msg = ''
    if type(msg) == 'table' then
        for key, val in pairs(msg) do
            _msg = tostring( key)..':'.."\n"
        end
    elseif type(msg) == 'string' then
        _msg = msg
     elseif type(msg) == 'nil' then
        _msg = 'nil'
    else
        _msg = msg
    end


    local fp = io.open(waf_root.."/debug.log", "ab")
    if fp == nil then
        return nil
    end

    -- local localtime = os.date("%Y-%m-%d %H:%M:%S")
    local localtime = ngx.localtime()
    if server_name then
        fp:write(tostring(_msg) .. "\n")
    else
        fp:write(localtime..":"..tostring(_msg) .. "\n")
    end

    fp:flush()
    fp:close()
    return true
end


local function write_file_clear(filename, body)
    fp = io.open(filename,'w')
    if fp == nil then
        return nil
    end
    fp:write(body)
    fp:flush()
    fp:close()
    return true
end

function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config

end


function _M.setParams( self, params )
    self.params = params
end


function _M.is_min(self, ip1, ip2)
    n = 0
    for _,v in ipairs({1,2,3,4})
    do
        if ip1[v] == ip2[v] then
            n = n + 1
        elseif ip1[v] > ip2[v] then
            break
        else
            return false
        end
    end
    return true
end

function _M.is_max(self,ip1,ip2)
    n = 0
    for _,v in ipairs({1,2,3,4})
    do
        if ip1[v] == ip2[v] then
            n = n + 1
        elseif ip1[v] < ip2[v] then
            break
        else
            return false
        end
    end
    return true
end

function _M.split(self, str,reps )
    local rsList = {}
    string.gsub(str,'[^'..reps..']+',function(w)
        table.insert(rsList,w)
    end)
    return rsList
end

function _M.arrip(self, ipstr)
    if ipstr == 'unknown' then return {0,0,0,0} end
    if string.find(ipstr,':') then return ipstr end
    iparr = self:split(ipstr,'.')
    iparr[1] = tonumber(iparr[1])
    iparr[2] = tonumber(iparr[2])
    iparr[3] = tonumber(iparr[3])
    iparr[4] = tonumber(iparr[4])
    return iparr
end


function _M.compare_ip(self,ips)
    local ip = self.params["ip"]
    local ipn = self.params["ipn"]
    if ip == 'unknown' then return true end
    if string.find(ip,':') then return false end
    if not self:is_max(ipn,ips[2]) then return false end
    if not self:is_min(ipn,ips[1]) then return false end
    return true
end



function _M.to_json(self, msg)
    return json.encode(msg)
end

function _M.return_state(status,msg)
    result = {}
    result['status'] = status
    result['msg'] = msg
    return result
end

function _M.return_message(self, status, msg)
    ngx.header.content_type = "application/json"
    local data = self:return_state(status, msg)
    ngx.say(json.encode(data))
    ngx.exit(200)
end

function _M.return_html(self, status, html)
    ngx.header.content_type = "text/html"
    ngx.say(html)
    ngx.exit(status)
end

function _M.read_file_body(self, filename)
    fp = io.open(filename, 'r')
    if fp == nil then
        return nil
    end
    local fbody = fp:read("*a")
    fp:close()
    if fbody == '' then
        return nil
    end
    return fbody
end

function _M.read_file(self, name)
    f = self.rpath .. name .. '.json'
    local fbody = self:read_file_body(f)
    if fbody == nil then
        return {}
    end

    local data = json.decode(fbody)
    return data
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

function _M.read_file_table( self, name )
    return self:select_rule(self:read_file(name))
end


function _M.read_file_body_decode(self, name)
    return json.decode(self:read_file_body(name))
end

function _M.write_file(self, filename, body)
    fp = io.open(filename,'ab')
    if fp == nil then
        return nil
    end
    fp:write(body)
    fp:flush()
    fp:close()
    return true
end

function _M.write_file_clear(self, filename, body)
    return write_file_clear(filename, body)
end

function _M.write_to_file(self, logstr)
    local server_name = self.params['server_name']
    local filename = self.logdir .. '/' .. server_name .. '_' .. ngx.today() .. '.log'
    self:write_file(filename, logstr)
    return true
end

-- 是否文件迁入数据库中
function  _M.is_migrating(self)
    local migrating = self.waf_root +"/migrating"
    local file = io.open(migrating, "rb")
    if file then return true end
    return false
end


function _M.continue_key(self,key)
    key = tostring(key)
    if string.len(key) > 64 then return false end;
    local keys = { "content", "contents", "body", "msg", "file", "files", "img", "newcontent" }
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
    local cipn = self:split(client_ip,'.')
    if self:array_len(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end

-- 定时异步同步统计信息
function _M.timer_stats_total(self)
    local total_path = self.cpath .. 'total.json'
    local total = ngx.shared.waf_limit:get(total_path)
    if not total then
        return false
    end
    return self:write_file_clear(total_path,total)
end

function _M.stats_total(self, name, rule)
    local server_name = self.params['server_name']
    local total_path = cpath .. 'total.json'
    local total = ngx.shared.waf_limit:get(total_path)

    if not total then
        local tbody = self:read_file_body(total_path)
        total = json.decode(tbody)
    else
        total = json.decode(total)
    end

    if not total then return false end

    -- 开始计算
    if not total['sites'] then total['sites'] = {} end
    if not total['sites'][server_name] then total['sites'][server_name] = {} end
    if not total['sites'][server_name][name] then total['sites'][server_name][name] = 0 end
    if not total['rules'] then total['rules'] = {} end
    if not total['rules'][name] then total['rules'][name] = 0 end
    if not total['total'] then total['total'] = 0 end
    total['total'] = total['total'] + 1
    total['sites'][server_name][name] = total['sites'][server_name][name] + 1
    total['rules'][name] = total['rules'][name] + 1

    ngx.shared.waf_limit:set(total_path,json.encode(total))

    -- 异步执行
    -- 现在改再init_workder.lua 定时执行
    -- ngx.timer.every(3, timer_stats_total_log)
end


-- 获取配置域名
function _M.get_sn(self, config_domains)
    local request_name = ngx.var.server_name
    local cache_name = ngx.shared.waf_limit:get(request_name)
    if cache_name then return cache_name end

    for _,v in ipairs(config_domains)
    do
        for _,cd_name in ipairs(v['domains'])
        do
            if request_name == cd_name then
                ngx.shared.waf_limit:set(request_name,v['name'],86400)
                return v['name']
            end
        end
    end
    return request_name
end

function _M.get_random(self,n) 
    math.randomseed(ngx.time())
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



function _M.is_ngx_match_orgin(self,rule,match, sign)
    if ngx_match(ngx.unescape_uri(match), rule,"isjo") then
        error_rule = rule .. ' >> ' .. sign .. ':' .. match
        return true
    end
    return false
end


function _M.ngx_match_string(self, rule, content,sign)
    local t = self:is_ngx_match_orgin(rule, content, sign)
    if t then
        return true
    end
  
    return false
end

function _M.ngx_match_list(self, rules, content)
    for i,rule in ipairs(rules)
    do
        if rule[1] == 1 then
            local t = self:is_ngx_match_orgin(rule[2], content, rule[3])
            if t then
                return true
            end
        end
    end
    return false
end

function _M.is_ngx_match_ua(self, rules, content)
    -- ngx.header.content_type = "text/html"
    for i,rule in ipairs(rules)
    do
        -- 开启的规则，才匹配。
        if rule[1] == 1 then
            local t = self:is_ngx_match_orgin(rule[2], content, rule[3])
            if t then
                return true
            end
        end
    end
    return false
end

function _M.is_ngx_match_post(self, rules, content)
    for i,rule in ipairs(rules)
    do
        -- 开启的规则，才匹配。
        if rule[1] == 1 then
            local t = self:is_ngx_match_orgin(rule[2],content, rule[3])
            if t then
                return true
            end
        end
    end
    return false
end


function _M.is_ngx_match(self, rules, sbody, rule_name)
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
    local config = self.config

    local ip = self.params['ip']
    
    local retry = config['retry']['retry']
    local retry_time = config['retry']['retry_time']
    local retry_cycle = config['retry']['retry_cycle']
    
    local count = ngx.shared.waf_drop_ip:get(ip)
    if count then
        ngx.shared.waf_drop_ip:incr(ip, 1)
    else
        ngx.shared.waf_drop_ip:set(ip, 1, retry_cycle)
    end

    if config['log'] ~= true or self:is_site_config('log') ~= true then return false end
    local method = self.params['method']
    if error_rule then 
        rule = error_rule
        error_rule = nil
    end

    local count = ngx.shared.waf_drop_ip:get(ip)

    if (count > retry) then
        local safe_count,_ = ngx.shared.waf_drop_sum:get(ip)
        if not safe_count then
            ngx.shared.waf_drop_sum:set(ip, 1, 86400)
            safe_count = 1
        else
            ngx.shared.waf_drop_sum:incr(ip, 1)
        end
        local lock_time = retry_time * safe_count
        if lock_time > 86400 then lock_time = 86400 end
        local logtmp = {
            ngx.localtime(),
            ip,
            method,ngx.var.request_uri,
            ngx.var.http_user_agent,
            name,
            retry_cycle .. '秒以内累计超过'..retry..'次以上非法请求,封锁'.. lock_time ..'秒'
        }
        local logstr = json.encode(logtmp) .. "\n"
        retry_times = retry + 1
        ngx.shared.waf_drop_ip:set(ip, retry_times, lock_time)
        self:write_to_file(logstr)
    else
        local logtmp = {
            ngx.localtime(),
            ip,
            method,
            ngx.var.request_uri,
            ngx.var.http_user_agent,
            name,
            rule
        }
        local logstr = json.encode(logtmp) .. "\n"
        self:write_to_file(logstr)
    end
    
    self:stats_total(name, rule)
end


function _M.get_real_ip(self, server_name)
    local client_ip = "unknown"
    local site_config = self.site_config
    if site_config[server_name] then
        if site_config[server_name]['cdn'] then
            local request_header = ngx.req.get_headers()
            for _,v in ipairs(site_config[server_name]['cdn_header'])
            do
                if request_header[v] ~= nil and request_header[v] ~= "" then
                    local header_tmp = request_header[v]
                    if type(header_tmp) == "table" then header_tmp = header_tmp[1] end
                    client_ip = self:split(header_tmp,',')[1]
                    -- return client_ip
                    break;
                end
            end 
        end
    end
    

    -- ipv6
    if type(client_ip) == 'table' then client_ip = "" end
    if client_ip ~= "unknown" and ngx.re.match(client_ip,"^([a-fA-F0-9]*):") then
        return client_ip
    end

    -- ipv4
    if  not ngx.re.match(client_ip,"\\d+\\.\\d+\\.\\d+\\.\\d+") == nil or not self:is_ipaddr(client_ip) then
        client_ip = ngx.var.remote_addr
        if client_ip == nil then
            client_ip = "unknown"
        end
    end
    return client_ip
end


function _M.is_site_config(self,cname)
    local site_config = self.site_config
    if site_config[server_name] ~= nil then
        if cname == 'cc' then
            return site_config[server_name][cname]['open']
        else
            return site_config[server_name][cname]
        end
    end
    return true
end

function _M.get_boundary(self)
    local header = self.params["request_header"]["content-type"]
    if not header then return nil end
    if type(header) == "table" then
        header = header[1]
    end

    local m = string.match(header, ";%s*boundary=\"([^\"]+)\"")
    if m then
        return m
    end
    return string.match(header, ";%s*boundary=([^\",;]+)")
end


function _M.return_post_data(self)
    if method ~= "POST" then return false end
    content_length = tonumber(self.params["request_header"]['content-length'])
    if not content_length then return false end
    max_len = 2560 * 1024000
    if content_length > max_len then return false end
    local boundary = self:get_boundary()
    if boundary then
        ngx.req.read_body()
        local data = ngx.req.get_body_data()
        if not data then return false end
        local tmp = ngx.re.match(data,[[filename=\"(.+)\.(.*)\"]])
        if not tmp then return false end
        if not tmp[2] then return false end
        return tmp[2]
        
    end
    return false
end


function _M.t(self)
    ngx.say(',,,')
end


return _M

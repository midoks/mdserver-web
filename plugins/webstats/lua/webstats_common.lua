
local setmetatable = setmetatable
local _M = { _VERSION = '1.0' }
local mt = { __index = _M }

local json = require "cjson"
local sqlite3 = require "lsqlite3"
local config = require "webstats_config"
local sites = require "webstats_sites"

local debug_mode = true
local total_key = "log_kv_total"

local unset_server_name = "unset"
local max_log_id = 99999999999999
local cache = ngx.shared.mw_total

local today = ngx.re.gsub(ngx.today(),'-','')
local request_header = ngx.req.get_headers()
local method = ngx.req.get_method()

local day = os.date("%d")
local number_day = tonumber(day)
local day_column = "day"..number_day
local flow_column = "flow"..number_day
local spider_column = "spider_flow"..number_day

local auto_config = nil

local log_dir = "{$SERVER_APP}/logs"

function _M.new(self)
    local self = {
        total_key = total_key,
        params = nil,
        site_config = nil,
        config = nil,
    }
    return setmetatable(self, mt)
end


function _M.getInstance(self)
    if self.instance == nil then
        self.instance = self:new()
        self:cron()
    end
    assert(self.instance ~= nil)
    return self.instance
end


function _M.initDB(self, input_sn)
    local path = log_dir .. '/' .. input_sn .. "/logs.db"
    local db, err = sqlite3.open(path)

    if err then
        return nil
    end

    db:exec([[PRAGMA synchronous = 0]])
    db:exec([[PRAGMA cache_size = 8000]])
    db:exec([[PRAGMA page_size = 32768]])
    db:exec([[PRAGMA journal_mode = wal]])
    db:exec([[PRAGMA journal_size_limit = 21474836480]])
    return db
end

function _M.getTotalKey(self)
    return self.total_key
end

function _M.to_json(self, msg)
    return json.encode(msg)
end

function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config
end

function _M.setParams( self, params )
    self.params = params
end

function _M.setInputSn(self, input_sn)
    local global_config = config["global"]
    if config[input_sn] == nil then
        auto_config = global_config
    else
        auto_config = config[input_sn]
        for k, v in pairs(global_config) do
            if auto_config[k] == nil then
                auto_config[k] = v
            end
        end
    end
    return auto_config
end

function _M.get_domain(self)
    local domain = ngx.req.get_headers()['host']
     -- domain = ngx.re.gsub(domain, "_", ".")
    if domain == nil then
        domain = "unknown"
    end
    return domain
end

function _M.split(self, str, reps)
    local arr = {}
    -- 修复反向代理代过来的数据
    if "table" == type(str) then
        return str
    end
    string.gsub(str,'[^'..reps..']+',function(w) table.insert(arr,w) end)
    return arr
end

function _M.arrlen(self, arr)
    if not arr then return 0 end
    local count = 0
    for _,v in ipairs(arr) do
        count = count + 1
    end
    return count
end

function _M.is_ipaddr(self, client_ip)
    local cipn = self:split(client_ip,'.')
    if self:arrlen(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end


function _M.get_sn(self, input_sn)
    local dst_name = cache:get(input_sn)
    if dst_name then return dst_name end

    -- self:D(json.encode(sites))
    for _,v in ipairs(sites)
    do
        if input_sn == v["name"] then
            cache:set(input_sn, v['name'], 86400)
            return v["name"]
        end
        -- self:D("get_sn:"..json.encode(v))
        for _,dst_domain in ipairs(v['domains'])
        do
            if input_sn == dst_domain then
                cache:set(input_sn, v['name'], 86400)
                return v['name']
            elseif string.find(dst_domain, "*") then
                local new_domain = string.gsub(dst_domain, '*', '.*')
                if string.find(input_sn, new_domain) then
                    dst_domain = v['name']
                    cache:set(input_sn, dst_domain, 86400)
                end
            end
        end
    end

    cache:set(input_sn, unset_server_name, 86400)
    return unset_server_name
end


function _M.get_store_key(self)
    return os.date("%Y%m%d%H", ngx.time())
end

function _M.get_store_key_with_time(self, htime)
    return os.date("%Y%m%d%H", htime)
end

function _M.get_length(self)
    local clen  = ngx.var.body_bytes_sent
    if clen == nil then clen = 0 end
    return tonumber(clen)
end

function _M.get_last_id(self, input_sn)
    local last_insert_id_key = input_sn .. "_last_id"
    local new_id, err = cache:incr(last_insert_id_key, 1, 0)
    if new_id >= max_log_id then
        cache:set(last_insert_id_key, 1)
        new_id = cache:get(last_insert_id_key)
    end
    return new_id
end

function _M.get_http_origin(self)
    local data = ""
    local headers = ngx.req.get_headers()
    if not headers then return data end
    
    local req_method = ngx.req.get_method()
    if req_method ~= 'GET' then
        data = ngx.var.request_body
        if not data then
            data = ngx.req.get_body_data()
        end

        if "string" == type(data) then
            headers["payload"] = data
        elseif "table" == type(data) then
            headers["payload"] = table.concat(data, "&")
        end
    end
    return json.encode(headers)
end

function _M.cronPre(self)
    self:lock_working('cron_init_stat')

    local time_key = self:get_store_key()
    local time_key_next = self:get_store_key_with_time(ngx.time()+3600)


    for site_k, site_v in ipairs(sites) do
        local input_sn = site_v["name"]

        local db = self:initDB(input_sn)

        local wc_stat = {
            'request_stat',
            'client_stat',
            'spider_stat'
        }

        local v1 = true
        local v2 = true
        for _,ws_v in pairs(wc_stat) do
            v1 = self:_update_stat_pre(db, ws_v, time_key)
            v2 = self:_update_stat_pre(db, ws_v, time_key_next)
        end

        if db and db:isopen() then
            db:execute([[COMMIT]])
            db:close()
        end

        if  not v1 or not v2 then
            return false
        end
    end

    self:unlock_working('cron_init_stat')

    return true
end

function _M.cron(self)

    local timer_every_get_data = function (premature)
        
        local llen = ngx.shared.mw_total:llen(total_key)
        if llen == 0 then
            return true
        end

        local cron_key = 'cron_every_1s'
        if self:is_working(cron_key) then
            return true
        end

        local ready_ok = self:cronPre()
        if not ready_ok then
            return true
        end

        local dbs = {}
        local stmts = {}
        local stat_fields = {}
        local ip_stats = {}
        local url_stats = {}

        local time_key = self:get_store_key()

        for _, site_v in ipairs(sites) do
            local input_sn = site_v["name"]
            if self:is_migrating(input_sn) then
                return true
            end

            if self:is_working('cron_init_stat') then
                return true
            end

            local db = self:initDB(input_sn)

            stat_fields[input_sn] = {}

            if db then
                dbs[input_sn] = db
                self:clean_stats(db, input_sn)

                local stmt = db:prepare[[INSERT INTO web_logs(
                        time, ip, domain, server_name, method, status_code, uri, body_length,
                        referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
                        VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
                        :body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
                        :request_headers, :ip_list, :client_port)]]
                stmts[input_sn] = stmt

                db:exec([[BEGIN TRANSACTION]])
            end
        end

        self:lock_working(cron_key)
        
        for i = 1, llen do
            local data = ngx.shared.mw_total:lpop(total_key)
            if not data then
                self:unlock_working(cron_key)
                break
            end

            local info = json.decode(data)
            local input_sn = info['server_name']
            local db = dbs[input_sn]
            if not db then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local stmt = stmts[input_sn]
            if not stmt then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local insert_ok = self:store_logs_line(db, stmt, input_sn, info)
            if not insert_ok then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local log_kv = info["log_kv"]
            local excluded = log_kv['excluded']
            local stat_tmp_fields = info['stat_fields']

            local stat_fields_is = stat_fields[input_sn]
            for stf_k, stf_v in pairs(stat_tmp_fields) do
                if excluded then
                    if stf_k == "spider_stat_fields" or stf_k == "client_stat_fields" then
                        break
                    end
                end

                local stf_is = stat_fields_is[stf_k]
                if not stf_is then
                    stf_is = {}
                    stat_fields_is[stf_k] = stf_is
                end
                
                for sv_k, sv_v in pairs(stf_v) do
                    stf_is[sv_k] = (stf_is[sv_k] or 0) + sv_v
                end
            end

            if not excluded then
                local ip = log_kv['ip']
                local body_length = log_kv["body_length"]

                local ip_stats_sn = ip_stats[input_sn]
                if not ip_stats_sn then
                    ip_stats_sn = {}
                    ip_stats[input_sn] = ip_stats_sn
                end

                local ip_stat = ip_stats_sn[ip]
                if not ip_stat then
                    ip_stats_sn[ip] = {ip_num = 1, body_length = body_length}
                else
                    ip_stat.ip_num = ip_stat.ip_num + 1
                    ip_stat.body_length = ip_stat.body_length + body_length
                end

                local url_stats_sn = url_stats[input_sn]
                if not url_stats_sn then
                    url_stats_sn = {}
                    url_stats[input_sn] = url_stats_sn
                end
                
                local request_uri = log_kv["request_uri"]
                local request_uri_md5 = ngx.md5(request_uri)
                local url_stat = url_stats_sn[request_uri_md5]
                if not url_stat then
                    url_stats_sn[request_uri_md5] = {url_num = 1, uri = request_uri, body_length = body_length}
                else
                    url_stat.url_num = url_stat.url_num + 1
                    url_stat.body_length = url_stat.body_length + body_length
                end
            end
        end

        local save_day = config['global']["save_day"]
        local now_date = os.date("*t")
        local save_date_timestamp = os.time{year = now_date.year, month = now_date.month, day = now_date.day - save_day, hour = 0}
        local delete_sql = "DELETE FROM web_logs WHERE time<" .. tostring(save_date_timestamp)

        for _, site_v in ipairs(sites) do
            local input_sn = site_v["name"]

            local stmt = stmts[input_sn]
            if stmt then
                local res = stmt:finalize()
                if tostring(res) == "5" then
                    self:D("Finalize res:" .. tostring(res))
                end
            end

            local stat_fields_is = stat_fields[input_sn]
            local db = dbs[input_sn]

            if db then
                for sti_k, sti_v in pairs(stat_fields_is) do
                    local vkk = ""
                    for sv_k, sv_v in pairs(sti_v) do
                        vkk = vkk .. sv_k .. "=" .. sv_k .. "+" .. sv_v .. ","
                    end
                    if vkk ~= "" then
                        vkk = string.sub(vkk, 1, string.len(vkk) - 1)
                        
                        if sti_k == 'request_stat_fields' then
                            self:update_stat(db, "request_stat", time_key, vkk)
                        elseif sti_k == 'client_stat_fields' then
                            self:update_stat(db, "client_stat", time_key, vkk)
                        elseif sti_k == 'spider_stat_fields' then
                            self:update_stat(db, "spider_stat", time_key, vkk)
                        end
                    end
                end

                local local_ip_stats = ip_stats[input_sn]
                if local_ip_stats then
                    for ip_addr, ip_val in pairs(local_ip_stats) do
                        self:update_statistics_ip(db, ip_addr, ip_val.ip_num, ip_val.body_length)
                    end
                end

                local local_url_stats = url_stats[input_sn]
                if local_url_stats then
                    for url_md5, url_val in pairs(local_url_stats) do
                        self:update_statistics_uri(db, url_val.uri, url_md5, url_val.url_num, url_val.body_length)
                    end
                end

                db:exec(delete_sql)
            end

            if db and db:isopen() then
                db:execute([[COMMIT]])
                db:close()
            end
        end
        
        self:unlock_working(cron_key)
    end

    
    function timer_every_get_data_try()
       local presult, err = pcall( function() timer_every_get_data() end)
        if not presult then
            self:D("debug cron error on :"..tostring(err))
            return true
        end
    end

    ngx.timer.every(0.5, timer_every_get_data_try)
end


function _M.store_logs_line(self, db, stmt, input_sn, info)
    local logline = info['log_kv']
    
    local excluded = logline["excluded"]
    if excluded then
        return true
    end

    local user_agent = logline["user_agent"]
    if "table" == type(user_agent) then
        user_agent = self:to_json(user_agent)
    end
    
    stmt:bind_names {
        time = logline["time"],
        ip = logline["ip"],
        domain = logline["domain"],
        server_name = logline["server_name"],
        method = logline["method"],
        status_code = logline["status_code"],
        uri = logline["request_uri"],
        body_length = logline["body_length"],
        referer = logline["referer"],
        user_agent = user_agent,
        protocol = logline["protocol"],
        request_time = logline["request_time"],
        is_spider = logline["is_spider"],
        request_headers = logline["request_headers"],
        ip_list = logline["ip_list"],
        client_port = logline["client_port"],
    }

    local res = stmt:step()
    if tostring(res) == "5" then
        stmt:reset()
        return false
    end
    stmt:reset()
    return true
end

function _M.statistics_ipc(self, input_sn, ip)
    -- 判断IP是否重复的时间限定范围是请求的当前时间+24小时
    local ipc = 0
    local ip_token = input_sn..'_'..ip
    if not cache:get(ip_token) then
        ipc = 1
        cache:set(ip_token,1, self:get_end_time())
    end
    return ipc
end

function _M.statistics_request(self, ip, is_spider, body_length)
    -- 计算pv uv
    local pvc = 0
    local uvc = 0
    local request_header = ngx.req.get_headers()
    if not is_spider and ngx.status == 200 and body_length > 0 then
        local ua = ''
        if request_header['user-agent'] then
            if "table" == type(request_header['user-agent']) then
                ua = self:to_json(request_header['user-agent'])
            else
                ua = request_header['user-agent']
            end
            ua = string.lower(ua)
        end

        pvc = 1
        if ua then
            local today = ngx.today()
            local uv_token = ngx.md5(ip .. ua .. today)
            if not cache:get(uv_token) then
                uvc = 1
                cache:set(uv_token,1, self:get_end_time())
            end
        end
    end
    return pvc, uvc
end

-- 仅计算GET/HTML
function _M.statistics_request_old(self, ip, is_spider, body_length)
    -- 计算pv uv
    local pvc = 0
    local uvc = 0
    local method = ngx.req.get_method()
    if not is_spider and method == 'GET' and ngx.status == 200 and body_length > 512 then
        local ua = ''
        if request_header['user-agent'] then
            ua = string.lower(request_header['user-agent'])
        end

        out_header = ngx.resp.get_headers()
        if out_header['content-type'] then
            if string.find(out_header['content-type'], 'text/html', 1, true) then
                pvc = 1
                if request_header['user-agent'] then
                    if string.find(ua,'mozilla') then
                        local today = ngx.today()
                        local uv_token = ngx.md5(ip .. request_header['user-agent'] .. today)
                        if not cache:get(uv_token) then
                            uvc = 1
                            cache:set(uv_token,1, self:get_end_time())
                        end
                    end
                end
            end
        end
    end
    return pvc, uvc
end

---------------------       db start   ---------------------------


local stmt_caches = {
    uri_insert = {},
    uri_update = {},
    ip_insert = {},
    ip_update = {},
    stat_insert = {},
    stat_update = {}
}

function _M.update_statistics_uri(self, db, uri, uri_md5, day_num, body_length)
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local insert_stmt = stmt_caches.uri_insert[db]
    if not insert_stmt then
        insert_stmt = db:prepare("INSERT INTO uri_stat(uri_md5, uri) SELECT :uri_md5, :uri WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5 = :uri_md5);")
        stmt_caches.uri_insert[db] = insert_stmt
    end
    
    insert_stmt:bind_names{uri_md5 = uri_md5, uri = uri}
    insert_stmt:step()
    insert_stmt:reset()

    local update_key = day_column .. "_" .. flow_column
    local update_stmt = stmt_caches.uri_update[update_key]
    if not update_stmt then
        local update_sql = "UPDATE uri_stat SET " .. day_column .. "=" .. day_column .. "+:day_num, " .. flow_column .. "=" .. flow_column .. "+:body_length WHERE uri_md5=:uri_md5;"
        update_stmt = db:prepare(update_sql)
        stmt_caches.uri_update[update_key] = update_stmt
    end
    
    update_stmt:bind_names{day_num = day_num, body_length = body_length, uri_md5 = uri_md5}
    update_stmt:step()
    update_stmt:reset()
    
    return true
end

function _M.statistics_uri(self, db, uri, uri_md5, body_length)
    -- count the number of URI requests and traffic
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local stat_sql = nil
    stat_sql = "INSERT INTO uri_stat(uri_md5,uri) SELECT \""..uri_md5.."\",\""..uri.."\" WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5=\""..uri_md5.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE uri_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE uri_md5=\""..uri_md5.."\";"
    local res, err = db:exec(stat_sql)
    return true
end


function _M.update_statistics_ip(self, db, ip, day_num, body_length)
    local open_statistics_ip = config['global']["statistics_ip"]   
    if not open_statistics_ip then return true end
    
    local insert_stmt = stmt_caches.ip_insert[db]
    if not insert_stmt then
        insert_stmt = db:prepare("INSERT INTO ip_stat(ip) SELECT :ip WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip = :ip);")
        stmt_caches.ip_insert[db] = insert_stmt
    end
    
    insert_stmt:bind_names{ip = ip}
    insert_stmt:step()
    insert_stmt:reset()

    local update_key = day_column .. "_" .. flow_column
    local update_stmt = stmt_caches.ip_update[update_key]
    if not update_stmt then
        local update_sql = "UPDATE ip_stat SET " .. day_column .. "=" .. day_column .. "+:day_num, " .. flow_column .. "=" .. flow_column .. "+:body_length WHERE ip=:ip;"
        update_stmt = db:prepare(update_sql)
        stmt_caches.ip_update[update_key] = update_stmt
    end
    
    update_stmt:bind_names{day_num = day_num, body_length = body_length, ip = ip}
    update_stmt:step()
    update_stmt:reset()
    
    return true
end

function _M.statistics_ip(self, db, ip, body_length)
    return self:update_statistics_ip(db, ip, 1, body_length)
end


function _M._update_stat_pre(self, db, stat_table, key)
    local local_sql = string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table)
    local update_stat_stmt = db:prepare(local_sql)

    if update_stat_stmt then
        update_stat_stmt:bind_names{time=key}
        update_stat_stmt:step()
        update_stat_stmt:finalize()
        return true
    end
    return false
end

function _M.update_stat_quick(self, db, stat_table, key,columns)
    if not columns then return end
    local update_sql = "UPDATE ".. stat_table .. " SET " .. columns .. " WHERE time=" .. key
    return db:exec(update_sql)
end


function _M.update_stat(self, db, stat_table, key, columns)
    if not columns then return end
    
    local insert_key = stat_table .. "_insert"
    local insert_stmt = stmt_caches.stat_insert[insert_key]
    if not insert_stmt then
        local local_sql = "INSERT INTO " .. stat_table .. "(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM " .. stat_table .. " WHERE time=:time);"
        insert_stmt = db:prepare(local_sql)
        stmt_caches.stat_insert[insert_key] = insert_stmt
    end
    
    insert_stmt:bind_names{time = key}
    insert_stmt:step()
    insert_stmt:reset()
    
    local update_sql = "UPDATE " .. stat_table .. " SET " .. columns .. " WHERE time=" .. key
    return db:exec(update_sql)
end
---------------------       db end   ---------------------------

-- debug func
function _M.D(self,msg)
    if not debug_mode then return true end
    local fp = io.open('{$SERVER_APP}/debug.log', 'ab')
    if fp == nil then
        return nil
    end
    local localtime = os.date("%Y-%m-%d %H:%M:%S")
    if server_name then
        fp:write(tostring(msg) .. "\n")
    else
        fp:write(localtime..":"..tostring(msg) .. "\n")
    end
    fp:flush()
    fp:close()
    return true
end

function _M.is_migrating(self, input_sn)
    local file = io.open("{$SERVER_APP}/migrating", "rb")
    if file then return true end
    local file = io.open("{$SERVER_APP}/logs/"..input_sn.."/migrating", "rb")
    if file then return true end
    return false
end

function _M.is_working(self,sign)
    local work_status = cache:get(sign.."_working")
    if work_status ~= nil and work_status == true then
        return true 
    end
    return false
end

function _M.lock_working(self, sign)
    local working_key = sign.."_working"
    cache:set(working_key, true, 60)
end

function _M.unlock_working(self, sign)
    local working_key = sign.."_working"
    cache:set(working_key, false)
end

function _M.write_file(self, filename, body, mode)
        local fp = io.open(filename, mode)
        if fp == nil then
            return nil
        end
        fp:write(body)
        fp:flush()
        fp:close()
        return true
    end
    
function _M.read_file_body(self, filename)
    local fp = io.open(filename,'rb')
    if not fp then
        return nil
    end
    local fbody = fp:read("*a")
    fp:close()
    if fbody == '' then
        return nil
    end
    return fbody
end

function _M.load_update_day(self, input_sn)
    local _file = "{$SERVER_APP}/logs/"..input_sn.."/update_day.log"
    return self:read_file_body(_file)
end

function _M.write_update_day(self, input_sn)
    local _file = "{$SERVER_APP}/logs/"..input_sn.."/update_day.log"
    return self:write_file(_file, today, "w")
end

function _M.clean_stats(self, db, input_sn)
    -- 清空 uri,ip 汇总的信息[昨日]
    local update_day = self:load_update_day(input_sn)
    if not update_day or update_day ~= today then

        local update_sql = "UPDATE uri_stat SET "..day_column.."=0,"..flow_column.."=0"
        db:exec(update_sql)

        update_sql = "UPDATE ip_stat SET "..day_column.."=0,"..flow_column.."=0"
        db:exec(update_sql)
        self:write_update_day(input_sn)
    end
end

function _M.lpop(self)
    local cache = ngx.shared.mw_total
    return cache:lpop(total_key)
end

function _M.rpop(self)
    local cache = ngx.shared.mw_total
    return cache:rpop(total_key)
end


function _M.get_update_field(self, field, value)
    return field.."="..field.."+"..tostring(value)
end

function _M.get_request_time(self)
    local request_time = math.floor((ngx.now() - ngx.req.start_time()) * 1000)
    if request_time == 0 then  request_time = 1 end
    return request_time
end


function _M.get_end_time(self)
    local s_time = ngx.time()
    local n_date = os.date("*t",s_time + 86400)
    n_date.hour = 0
    n_date.min = 0
    n_date.sec = 0
    local d_time = ngx.time(n_date)
    return d_time - s_time
end


local spider_table = {
    ["baidu"] = 1,
    ["bing"] = 2,
    ["qh360"] = 3,
    ["google"] = 4,
    ["bytes"] = 5,
    ["sogou"] = 6,
    ["youdao"] = 7,
    ["soso"] = 8,
    ["dnspod"] = 9,
    ["yandex"] = 10,
    ["yisou"] = 11,
    ["other"] = 12,
    ["mpcrawler"] = 13,
    ["yahoo"] = 14,
    ["duckduckgo"] = 15
}

local spider_keywords = {
    ["baidu"] = "baidu",
    ["bytes"] = "bytes",
    ["360spider"] = "qh360",
    ["sogou"] = "sogou",
    ["soso"] = "soso",
    ["google"] = "google",
    ["bingbot"] = "bing",
    ["youdao"] = "youdao",
    ["dnspod"] = "dnspod",
    ["yandex"] = "yandex",
    ["yisou"] = "yisou",
    ["mpcrawler"] = "mpcrawler",
    ["yahoo"] = "yahoo",
    ["slurp"] = "other",
    ["duckduckgo"] = "other",
    ["semrush"] = "other",
    ["spider"] = "other",
    ["bot"] = "other",
    ["crawler"] = "other"
}

function _M.match_spider(self, ua)
    local is_spider = false
    local spider_name = ""
    
    if not ua then
        return false, "", 0
    end
    
    local lower_ua = string.lower(ua)
    
    for kw, name in pairs(spider_keywords) do
        if string.find(lower_ua, kw, 1, true) then
            is_spider = true
            spider_name = name
            break
        end
    end
    
    if is_spider then
        return is_spider, spider_name, spider_table[spider_name]
    end
    
    return false, "", 0
end


local clients_map = {
    ["android"] = "android",
    ["iphone"] = "iphone",
    ["ipod"] = "iphone",
    ["ipad"] = "iphone",
    ["firefox"] = "firefox",
    ["msie"] = "msie",
    ["trident"] = "msie",
    ["360se"] = "qh360",
    ["360ee"] = "qh360",
    ["360browser"] = "qh360",
    ["qihoo"] = "qh360",
    ["theworld"] = "theworld",
    ["tencenttraveler"] = "tt",
    ["maxthon"] = "maxthon",
    ["opera"] = "opera",
    ["qqbrowser"] = "qq",
    ["ucweb"] = "uc",
    ["ubrowser"] = "uc",
    ["safari"] = "safari",
    ["chrome"] = "chrome",
    ["metasr"] = "metasr",
    ["2345explorer"] = "pc2345",
    ["edge"] = "edg",
    ["edg"] = "edg",
    ["windows"] = "windows",
    ["linux"] = "linux",
    ["macintosh"] = "mac",
    ["mobile"] = "mobile"
}

local mobile_keywords = {"mobile", "android", "iphone", "ipod", "ipad"}
local pc_browser_keywords = {
    ["360se"] = "qh360",
    ["360ee"] = "qh360",
    ["360browser"] = "qh360",
    ["qihoo"] = "qh360",
    ["theworld"] = "theworld",
    ["tencenttraveler"] = "tt",
    ["maxthon"] = "maxthon",
    ["opera"] = "opera",
    ["qqbrowser"] = "qq",
    ["ucweb"] = "uc",
    ["ubrowser"] = "uc",
    ["metasr"] = "metasr",
    ["2345explorer"] = "pc2345",
    ["edge"] = "edg",
    ["firefox"] = "firefox",
    ["chrome"] = "chrome",
    ["safari"] = "safari",
    ["msie"] = "msie",
    ["trident"] = "msie"
}
local os_keywords = {"windows", "linux", "macintosh"}
local machine_keywords = {"apachebench", "curl", "headlesschrome", "wget", "spider", "crawler", "scrapy", "zgrab", "python", "java"}

local function _match_client_table(self, ua)
    local client_stat_fields = {}
    
    if not ua then
        return client_stat_fields
    end
    
    if "table" == type(ua) then
        ua = self:to_json(ua)
    end
    
    local lower_ua = string.lower(ua)
    
    local is_mobile = false
    for _, kw in ipairs(mobile_keywords) do
        if string.find(lower_ua, kw, 1, true) then
            is_mobile = true
            client_stat_fields["mobile"] = 1
            if kw ~= "mobile" then
                client_stat_fields[clients_map[kw]] = 1
            end
            break
        end
    end
    
    if not is_mobile then
        local cls_pc = nil
        for kw, name in pairs(pc_browser_keywords) do
            if string.find(lower_ua, kw, 1, true) then
                cls_pc = name
                break
            end
        end
        
        if cls_pc then
            client_stat_fields[cls_pc] = 1
        else
            local is_machine = false
            for _, kw in ipairs(machine_keywords) do
                if string.find(lower_ua, kw, 1, true) then
                    is_machine = true
                    break
                end
            end
            
            if is_machine then
                client_stat_fields["machine"] = 1
            else
                client_stat_fields["other"] = 1
            end
        end
        
        for _, kw in ipairs(os_keywords) do
            if string.find(lower_ua, kw, 1, true) then
                client_stat_fields[clients_map[kw]] = 1
                break
            end
        end
    end
    
    if string.find(lower_ua, "micromessenger", 1, true) then
        client_stat_fields["weixin"] = 1
    end
    
    return client_stat_fields
end

function _M.match_client_arr(self, ua)
    return _match_client_table(self, ua)
end

function _M.match_client(self, ua)
    local client_stat_fields = _match_client_table(self, ua)
    local fields_str = ""
    
    for k, v in pairs(client_stat_fields) do
        fields_str = fields_str .. "," .. self:get_update_field(k, v)
    end
    
    if fields_str ~= "" then
        fields_str = string.sub(fields_str, 2)
    end
    
    return fields_str
end

function _M.get_client_ip(self)
    local client_ip = "unknown"
    local cdn = auto_config['cdn']
    local request_header = ngx.req.get_headers()
    if cdn == true then
        for _,v in ipairs(auto_config['cdn_headers']) do
            if request_header[v] ~= nil and request_header[v] ~= "" then
                local ip_list = request_header[v]
                client_ip = self:split(ip_list,',')[1]
                break;
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

return _M
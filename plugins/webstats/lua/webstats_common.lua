
local setmetatable = setmetatable
local _M = { _VERSION = '1.0' }
local mt = { __index = _M }

local json = require "cjson"
local sqlite3 = require "lsqlite3"
local config = require "webstats_config"
local sites = require "webstats_sites"

local debug_mode = true
local total_key = "log_kv_total"
local cache = ngx.shared.mw_total
local today = ngx.re.gsub(ngx.today(),'-','')
local day = os.date("%d")
local number_day = tonumber(day)
local day_column = "day"..number_day
local flow_column = "flow"..number_day
local spider_column = "spider_flow"..number_day

local log_dir = "{$SERVER_APP}/logs"

function _M.new(self)
    local self = {
        total_key = total_key,
        params = nil,
        site_config = nil,
        config = nil,

    }
    -- self.dbs = {}
    return setmetatable(self, mt)
end


function _M.getInstance(self)
    if rawget(self, "instance") == nil then
        rawset(self, "instance", self.new())
        self:cron()
    end
    assert(self.instance ~= nil)
    return self.instance
end


function _M.initDB(self, input_sn)
    local path = log_dir .. '/' .. input_sn .. "/logs.db"
    db, err = sqlite3.open(path)

    if err then
        return nil
    end

    db:exec([[PRAGMA synchronous = 0]])
    db:exec([[PRAGMA page_size = 4096]])
    db:exec([[PRAGMA journal_mode = wal]])
    db:exec([[PRAGMA journal_size_limit = 1073741824]])
    return db
end

function _M.getTotalKey(self)
    return self.total_key
end

function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config
end

function _M.setParams( self, params )
    self.params = params
end

function _M.split(self, str, reps)
    local arr = {}
    string.gsub(str,'[^'..reps..']+',function(w) table.insert(arr,w) end)
    return arr
end

-- 后台任务
function _M.cron(self)
    local timer_every_get_data = function (premature)
        -- self:D( json.encode (sites) )

        local dbs = {}
        for i,v in ipairs(sites) do
            local input_sn = v["name"]
            local db = self:initDB(input_sn)

            if db then
                dbs[input_sn] = db

                local update_day = self:load_update_day(input_sn)
                if not update_day or update_day ~= today then

                    local update_sql = "UPDATE uri_stat SET "..day_column.."=0,"..flow_column.."=0"
                    status, errorString = db:exec(update_sql)

                    update_sql = "UPDATE ip_stat SET "..day_column.."=0,"..flow_column.."=0"
                    status, errorString = db:exec(update_sql)
                    self:write_update_day(input_sn)
                end
            end
        end

        -- self:D( tostring (dbs["t1.cn"]) )

        local cron_key = 'cron_every_1s'
        if self:is_working(cron_key) then
            return true
        end

        self:lock_working(cron_key)



        local llen, _ = ngx.shared.mw_total:llen(total_key)
        -- 每秒100条
        for i=1,llen do
            local data, _ = ngx.shared.mw_total:lpop(total_key)
            if data then
                local info = json.decode(data)
                local input_sn = info['server_name']
                -- 迁移合并时不执行
                if self:is_migrating(input_sn) then
                    return true
                end

                local db = dbs[input_sn]
                if db then

                    if self:is_working(input_sn) then
                        ngx.shared.mw_total:rpush(total_key, data)
                        os.execute("sleep " .. 0.6)
                        return true
                    end
                    self:store_logs(db, info)
                end
            end
        end

        
        for _, local_db in pairs(dbs) do
            if local_db then

                local now_date = os.date("*t")
                local save_day = config['global']["save_day"]
                local save_date_timestamp = os.time{year=now_date.year,
                    month=now_date.month, day=now_date.day-save_day, hour=0}
                -- delete expire data
                local_db:exec("DELETE FROM web_logs WHERE time<"..tostring(save_date_timestamp))
            end

            if local_db and local_db:isopen() then
                local_db:execute([[COMMIT]])
                local_db:close()
            end
        end 
        

        -- local tmp_log = "{$SERVER_APP}/logs/tmp_" .. tostring( ngx.now() ) .. ".log"
        -- -- 空闲空间小于10M,立即存盘
        -- -- local capacity_bytes = ngx.shared.mw_total:free_space()
        -- -- self:D("capacity_bytes:"..capacity_bytes)
        -- os.execute("sleep " .. 1)
        -- local nlen = llen - 100
        -- for i = 1,llen do
        --     local data = "" 
        --     local tmp, _ = ngx.shared.mw_total:lpop(total_key)
        --     if tmp then
        --         data = data .. tmp .. "\n"
        --     end

        --     if data ~= "" then
        --         self:write_file(tmp_log, data, "ab")
        --     end
        -- end
        
        self:unlock_working(cron_key)
    end

    ngx.timer.every(3, timer_every_get_data)
end

function _M.store_logs(self, db, info)
    local input_sn = info["server_name"]

    self:lock_working(input_sn)

    local stmt2 = nil
    if db ~= nil then
        stmt2 = db:prepare[[INSERT INTO web_logs(
            time, ip, domain, server_name, method, status_code, uri, body_length,
            referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
            VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
            :body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
            :request_headers, :ip_list, :client_port)]]
    end

    status, errorString = db:exec([[BEGIN TRANSACTION]])

    

    self:store_logs_line(db, stmt2, input_sn, info)

    local res, err = stmt2:finalize()
    if tostring(res) == "5" then
        self:D("Finalize res:"..tostring(res)..",Finalize err:"..tostring(err))
    end

    self:unlock_working(input_sn)
end



function _M.store_logs_line(self, db, stmt, input_sn, info)
    local logline = info['log_kv']

    local time = logline["time"]
    local id = logline["id"]
    local protocol = logline["protocol"]
    local client_port = logline["client_port"]
    local status_code = logline["status_code"]
    local uri = logline["uri"]
    local request_uri = logline["request_uri"]
    local method = logline["method"]
    local body_length = logline["body_length"]
    local referer = logline["referer"]
    local ip = logline["ip"]
    local ip_list = logline["ip_list"]
    local request_time = logline["request_time"]
    local is_spider = logline["is_spider"]
    local domain = logline["domain"]
    local server_name = logline["server_name"]
    local user_agent = logline["user_agent"]
    local request_headers = logline["request_headers"]
    local excluded = logline["excluded"] 

    local request_stat_fields = nil 
    local client_stat_fields = nil
    local spider_stat_fields = nil
    local stat_fields = info['stat_fields']
    if stat_fields == nil then
        -- D("Log stat fields is nil.")
        -- D("Logdata:"..logvalue)
    else
        stat_fields = self:split(stat_fields, ";")
        request_stat_fields = stat_fields[1]
        client_stat_fields = stat_fields[2]
        spider_stat_fields = stat_fields[3]

        if "x" == client_stat_fields then
            client_stat_fields = nil
        end

        if "x" == spider_stat_fields then
            spider_stat_fields = nil
        end
    end

    local time_key = logline["time_key"]
    if not excluded then
        stmt:bind_names {
            time=time,
            ip=ip,
            domain=domain,
            server_name=server_name,
            method=method,
            status_code=status_code,
            uri=request_uri,
            body_length=body_length,
            referer=referer,
            user_agent=user_agent,
            protocol=protocol,
            request_time=request_time,
            is_spider=is_spider,
            request_headers=request_headers,
            ip_list=ip_list,
            client_port=client_port,
        }

        local res, err = stmt:step()
        if tostring(res) == "5" then
            self:D("step res:"..tostring(res) ..",step err:"..tostring(err))
            self:D("the step database connection is busy, so it will be stored later.")
            return false
        end
        stmt:reset()

        self:update_stat( db, "client_stat", time_key, client_stat_fields)
        self:update_stat( db, "spider_stat", time_key, spider_stat_fields)
        -- self:D("stat ok")

        -- only count non spider requests
        local ok, err = self:statistics_uri(db, request_uri, ngx.md5(request_uri), body_length)
        local ok, err = self:statistics_ip(db, ip, body_length)
        -- self:D("stat url ip ok")
    end

    self:update_stat( db, "request_stat", time_key, request_stat_fields)
    return true
end

function _M.statistics_uri(self, db, uri, uri_md5, body_length)
    -- count the number of URI requests and traffic
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local stat_sql = nil
    stat_sql = "INSERT INTO uri_stat(uri_md5,uri) SELECT \""..uri_md5.."\",\""..uri.."\" WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5=\""..uri_md5.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE uri_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE uri_md5=\""..uri_md5.."\""
    local res, err = db:exec(stat_sql)
    return true
end

function _M.statistics_ip(self, db, ip, body_length)
    local open_statistics_ip = config['global']["statistics_ip"]    
    if not open_statistics_ip then return true end
    
    local stat_sql = nil
    stat_sql = "INSERT INTO ip_stat(ip) SELECT \""..ip.."\" WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip=\""..ip.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE ip_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE ip=\""..ip.."\""
    local res, err = db:exec(stat_sql)
    return true
end


function _M.update_stat(self,db, stat_table, key, columns)
    -- 根据指定表名，更新统计数据
    if not columns then return end
    local stmt = db:prepare(string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table))
    stmt:bind_names{time=key}
    local res, err = stmt:step()
    stmt:finalize()
    local update_sql = "UPDATE ".. stat_table .. " SET " .. columns
    update_sql = update_sql .. " WHERE time=" .. key
    status, errorString = db:exec(update_sql)
end



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

function _M.is_migrating(self,input_sn)
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
    fbody = fp:read("*a")
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

function _M.lpop(self)
    local cache = ngx.shared.mw_total
    return cache:lpop(total_key)
end

function _M.rpop(self)
    local cache = ngx.shared.mw_total
    return cache:rpop(total_key)
end



return _M
local waf_root = "{$WAF_ROOT}"

-- local waf_cpath = waf_root.."/waf/lua/?.lua;"..waf_root.."/waf/conf/?.lua;"..waf_root.."/waf/html/?.lua;"
-- local waf_sopath = waf_root.."/waf/conf/?.so;"
-- if not package.path:find(waf_cpath) then
--     package.path = waf_cpath  .. package.path
-- end

-- if not package.cpath:find(waf_sopath) then
--     package.cpath = waf_sopath .. package.cpath
-- end

local json = require "cjson"

local __WAF_C = require "waf_common"
local WAF_C = __WAF_C:getInstance()

local waf_config = require "waf_config"
local waf_site_config = require "waf_site"
WAF_C:setConfData(waf_config, waf_site_config)
WAF_C:setDebug(true)

-- C:D("init worker"..tostring(ngx.worker.id()))

local function waf_timer_stats_total_log(premature)
    WAF_C:timer_stats_total()
end

local function waf_clean_expire_data(premature)
    WAF_C:clean_log()
end

ngx.shared.waf_limit:set("cpu_usage", 0, 10)
function waf_timer_every_get_cpu(premature)
    if WAF_C:file_exists('/proc/stat') then
        local lua_cpu_percent = WAF_C:get_cpu_percent()
        -- WAF_C:D("lua_cpu_percent:"..tostring(lua_cpu_percent))
        ngx.shared.waf_limit:set("cpu_usage", math.floor(lua_cpu_percent), 10)
    else
        local cpu_percent = WAF_C:read_file_body(waf_root.."/cpu.info")
        -- WAF_C:D("cpu_usage:"..tostring(cpu_percent ))
        if cpu_percent then
            ngx.shared.waf_limit:set("cpu_usage", tonumber(cpu_percent), 10)
        else
            ngx.shared.waf_limit:set("cpu_usage", 0, 10)
        end
    end
end

if ngx.worker.id() == 0 then

    ngx.timer.every(6, waf_timer_every_get_cpu)
    -- 异步执行
    ngx.timer.every(3, waf_timer_stats_total_log)
    ngx.timer.every(10, waf_clean_expire_data)

    WAF_C:cron()
end
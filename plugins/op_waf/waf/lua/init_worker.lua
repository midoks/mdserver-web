local waf_root = "{$WAF_ROOT}"
local waf_cpath = waf_root.."/waf/lua/?.lua;"..waf_root.."/waf/conf/?.lua;"..waf_root.."/waf/html/?.lua;"
local waf_sopath = waf_root.."/waf/conf/?.so;"

if not package.path:find(waf_cpath) then
    package.path = waf_cpath  .. package.path
end

if not package.cpath:find(waf_sopath) then
    package.cpath = waf_sopath .. package.cpath
end

local json = require "cjson"

local __C = require "waf_common"
local C = __C:getInstance()

local waf_config = require "waf_config"
local waf_site_config = require "waf_site"
C:setConfData(waf_config, waf_site_config)
C:setDebug(true)

if ngx.worker.id() == 0 then
    C:cron()
end
-- C:D("init worker"..tostring(ngx.worker.id()))

local function timer_stats_total_log(premature)
    C:timer_stats_total()
end


ngx.shared.waf_limit:set("cpu_usage", 0, 10)
function timer_every_get_cpu(premature)
    local cpu_percent = C:read_file_body(waf_root.."/cpu.info")
    -- C:D("cpu_usage:"..tostring(cpu_percent ))
    if cpu_percent then
        ngx.shared.waf_limit:set("cpu_usage", tonumber(cpu_percent), 10)
    else
        ngx.shared.waf_limit:set("cpu_usage", 0, 10)
    end
end

ngx.timer.every(5, timer_every_get_cpu)

-- 异步执行
ngx.timer.every(3, timer_stats_total_log)
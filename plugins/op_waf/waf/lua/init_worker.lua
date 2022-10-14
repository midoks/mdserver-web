
local json = require "cjson"

local waf_root = "{$WAF_ROOT}"
local cpath = waf_root.."/waf/"

local __C = require "common"
local C = __C:new()

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

local function timer_at_inc_log(premature)
    local total_path = cpath .. 'total.json'
    local tbody = ngx.shared.waf_waf_limit:get(total_path)
    if not tbody then
        return false
    end
    return write_file_clear(total_path, tbody)
end


ngx.shared.waf_waf_limit:set("cpu_usage", 0, 10)

function timer_every_get_cpu(premature)
    cpu_percent = 80
    ngx.shared.waf_waf_limit:set("cpu_usage", cpu_percent, 10)
end

if 0 == ngx.worker.id() then
    ngx.timer.every(5, timer_every_get_cpu)

    -- 异步执行
    ngx.timer.every(3, timer_at_inc_log)
end


ngx.shared.limit:set("cpu_usage", 0, 10)

local function excute_cmd(cmd)
    local t = io.popen(cmd)
    local ret = t:read("*all")
    return ret
end

function timer_every_get_cpu(premature)
    cpu_percent = 80
    ngx.shared.limit:set("cpu_usage", cpu_percent, 10)
end
if 0 == ngx.worker.id() then
    ngx.timer.every(5, timer_every_get_cpu)
end
-- cd /www/server/mdserver-web/plugins/op_waf/t/bench && bash bench.sh

local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

local function file_exists(path)
  local file = io.open(path, "rb")
  if file then file:close() end
  return file ~= nil
end

-- 以上为预热操作
collectgarbage()

local json = require "cjson"
local ngx_re = require "ngx.re"

local function data_split(self, str,reps )
    local rsList = {}
    string.gsub(str,'[^'..reps..']+',function(w)
        table.insert(rsList,w)
    end)
    return rsList
end

local function get_cpu_stat()
    local cpu_total = 0
    local fp = io.open('/proc/stat','r')
    local cpu_line = fp:read()
    fp:close()

    local list = ngx_re.split(cpu_line," ")
    table.remove(list,1)
    table.remove(list,1)

    local idie = list[4]
    for i,v in pairs(list)
    do
        cpu_total = cpu_total + v
    end

    local use_percent = tonumber(100-(idie/cpu_total)*100)

    return cpu_total,idie,use_percent
end

local function get_cpu_percent()
    local cpu_total,idie,use_percent = get_cpu_stat()
    ngx.sleep(2)
    local cpu_total2,idie2,use_percent2 = get_cpu_stat()
    local cpu_usage_percent = tonumber(100-(((idie2-idie)/(cpu_total2-cpu_total))*100))
    ngx.say("cpu_usage_percent:"..cpu_usage_percent)
    return cpu_usage_percent
end

ngx.update_time()
local begin = ngx.now()
local N = 1e1
for i = 1, N do
    get_cpu_stat()
end
ngx.update_time()

ngx.say("test_get_cpu elapsed: ", (ngx.now() - begin))


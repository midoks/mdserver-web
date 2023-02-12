local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

function file_exists(path)
  local file = io.open(path, "rb")
  if file then file:close() end
  return file ~= nil
end

-- 以上为预热操作
collectgarbage()


function get_cpu_stat()
    local cpu_total = 0
    local fp = io.open('/proc/stat','r')
    local cpu_line = fp:read()
    fp:close()


    local iterator, err = ngx.re.gmatch(cpu_line,"(d+)")
    while true do
        local m, err = iterator()
        if not m then
            break
        end
        cpu_total = cpu_total + m[0]
    end
    return cpu_total
end

function get_cpu_percent()
    local fp = io.open("/proc/stat","r")
    local cpu_line = fp:read()
    fp:close()
    local iterator, err = ngx.re.gmatch(cpu_line,"(d+)")
    while true do
        local m, err = iterator()
        if not m then
            break
        end
        cpu_total1 = cpu_total1 + m[0]
    end
end

ngx.update_time()
local begin = ngx.now()
local N = 1e2
for i = 1, N do
    get_cpu_stat()
end
ngx.update_time()

ngx.say("test_get_cpu elapsed: ", (ngx.now() - begin))


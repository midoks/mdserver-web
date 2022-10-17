
local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end
-- 以上为预热操作
collectgarbage()


local function get_store_key()
    return os.date("%Y%m%d%H", os.time())
end

local function get_store_key2()
    return os.date("%Y%m%d%H", ngx.time())
end


local function get_end_time()
    local s_time = os.time()
    local n_date = os.date("*t",s_time + 86400)
    n_date.hour = 0
    n_date.min = 0
    n_date.sec = 0
    local d_time = os.time(n_date)
    return d_time - s_time
end




local function get_end_time2()
    local s_time = ngx.time()
    local n_date = os.date("*t",s_time + 86400)
    n_date.hour = 0
    n_date.min = 0
    n_date.sec = 0
    local d_time = ngx.time(n_date)
    return d_time - s_time
end

local function get_update_field(field, value)
    return field.."="..field.."+"..value
end

local function get_update_field2(field, value)
    return field.."="..field.."+"..tostring(value)
end



ngx.update_time()
local begin = ngx.now()
local N = 1e3
for i = 1, N do
    get_store_key()
end
ngx.update_time()

ngx.say("get_store_key elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e3
for i = 1, N do
    get_store_key2()
end
ngx.update_time()

ngx.say("get_store_key2 elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e5
for i = 1, N do
    get_end_time()
end
ngx.update_time()

ngx.say("get_end_time elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e5
for i = 1, N do
    get_end_time2()
end
ngx.update_time()

ngx.say("get_end_time2 elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e9
for i = 1, N do
    get_update_field("ss","1")
end
ngx.update_time()

ngx.say("get_update_field elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e9
for i = 1, N do
    get_update_field2("ss",1)
end
ngx.update_time()

ngx.say("get_update_field2 elapsed: ", (ngx.now() - begin) / N)


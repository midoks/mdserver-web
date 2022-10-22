local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

-- 以上为预热操作
collectgarbage()

local ffi = require("ffi")
ffi.cdef[[
    struct timeval {
        long int tv_sec;
        long int tv_usec;
    };
    int gettimeofday(struct timeval *tv, void *tz);
]];
local tm = ffi.new("struct timeval");
 
-- 返回微秒级时间戳
local function current_time_millis()
    ffi.C.gettimeofday(tm,nil);
    local sec =  tonumber(tm.tv_sec);
    local usec =  tonumber(tm.tv_usec);
    return sec + usec * 10^-6;
end


ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    target()
end
ngx.update_time()

ngx.say("elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    target()
end
ngx.update_time()

ngx.say("elapsed[1]: ", (ngx.now() - begin) / N)




ngx.update_time()
local begin = current_time_millis()
local N = 1e7
for i = 1, N do
    target()
end
ngx.update_time()

ngx.say("ffi elapsed: ", (current_time_millis() - begin) / N)
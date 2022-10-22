
local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end
-- 以上为预热操作
collectgarbage()

local function test_string_gsub(str,reps)
    local resultStrList = {}
    string.gsub(str,'[^'..reps..']+', function(w)
        table.insert(resultStrList,w)
        return w 
    end)
end


local function test_ngx_string_gsub(str,reps)
    local resultStrList = {}
    ngx.re.gsub(str,'[^'..reps..']+', function(w)
        table.insert(resultStrList,w[0])
        return w
    end, "ijo")
end

ngx.update_time()
local begin = ngx.now()
local N = 1e6
for i = 1, N do
    test_string_gsub("2409:8a62:e20:95f0:45b7:233e:f003:c0ab",",")
end
ngx.update_time()

ngx.say("test_string_gsub elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e6
for i = 1, N do
    test_ngx_string_gsub("2409:8a62:e20:95f0:45b7:233e:f003:c0ab",",")
end
ngx.update_time()

ngx.say("test_ngx_string_gsub elapsed: ", (ngx.now() - begin) / N)

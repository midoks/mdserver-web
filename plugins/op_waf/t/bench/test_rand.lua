local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

-- 以上为预热操作
collectgarbage()



local function get_random_t1(n) 
    math.randomseed(ngx.time())
    local t = {
        "0","1","2","3","4","5","6","7","8","9",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z",
        "A","B","C","D","E","F","G","H","I","J",
        "K","L","M","N","O","P","Q","R","S","T",
        "U","V","W","X","Y","Z",
    }    
    local s = ""
    for i = 1, n do
        s = s .. t[math.random(#t)]
    end
    return s
end



local function get_random_t2(n) 
    local t = {
        "0","1","2","3","4","5","6","7","8","9",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z",
        "A","B","C","D","E","F","G","H","I","J",
        "K","L","M","N","O","P","Q","R","S","T",
        "U","V","W","X","Y","Z",
    }    
    local s = ""
    for i = 1, n do
        s = s .. t[math.random(#t)]
    end
    return s
end

ngx.update_time()
local begin = ngx.now()
local N = 1e5
for i = 1, N do
    get_random_t1(16)
end
ngx.update_time()

ngx.say("test get_random_t1 elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e5
math.randomseed(ngx.time())
for i = 1, N do
    get_random_t2(16)
end
ngx.update_time()

ngx.say("test get_random_t2 elapsed: ", (ngx.now() - begin) / N)



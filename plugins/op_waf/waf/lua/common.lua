

local setmetatable = setmetatable
local _M = { _VERSION = '0.01' }
local mt = { __index = _M }
local json = require "cjson"


function _M.new(cpath, rpath)
    -- ngx.log(ngx.ERR,"read:"..cpath..",rpath:"..rpath)
    local self = {
         cpath = cpath,
         rpath = rpath,
         config = '',
         site_config = ''
    }
    local p = setmetatable(self, mt)
    return p
end


function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config
end



function _M.return_message(self, status, msg)
    ngx.header.content_type = "application/json;"
    ngx.status = status
    ngx.say(json.encode(msg))
    ngx.exit(status)
end


function _M.return_html(self,status,html)
    ngx.header.content_type = "text/html"
    ngx.status = status
    ngx.say(html)
    ngx.exit(status)
end

function _M.read_file_body(self, filename)
    -- ngx.log(ngx.ERR,"read_file_body:"..filename)
	fp = io.open(filename, 'r')
	if fp == nil then
        return nil
    end
	fbody = fp:read("*a")
    fp:close()
    if fbody == '' then
        return nil
    end
	return fbody
end

function _M.continue_key(self,key)
    key = tostring(key)
    if string.len(key) > 64 then return false end;
    local keys = {"content","contents","body","msg","file","files","img","newcontent"}
    for _,k in ipairs(keys)
    do
        if k == key then return false end;
    end
    return true;
end


function _M.array_len(self, arr)
    if not arr then return 0 end
    local count = 0
    for _,v in ipairs(arr)
    do
        count = count + 1
    end
    return count
end

function _M.is_ipaddr(self, client_ip)
    local cipn = split(client_ip,'.')
    if self:array_len(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end


function _M.read_file_body_decode(self, filename)
    return json.decode(self:read_file_body(filename))
end

function _M.select_rule(self, rules)
    if not rules then return {} end
    new_rules = {}
    for i,v in ipairs(rules)
    do 
        if v[1] == 1 then
            table.insert(new_rules,v[2])
        end
    end
    return new_rules
end



function _M.read_file(self, name)
    f = self.rpath .. name .. '.json'   
    fbody = self:read_file_body(f)
    if fbody == nil then
        return {}
    end
    return json.decode(fbody)
end

function _M.read_file_table( self, name )
    return self:select_rule(self:read_file('args'))
end

function _M.t(self)
    ngx.say(',,,')
end


return _M

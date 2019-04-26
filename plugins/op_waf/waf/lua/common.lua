

local setmetatable = setmetatable
local _M = { _VERSION = '0.01' }
local mt = { __index = _M }


function _M.new(cpath, rpath)
    ngx.log(ngx.ERR,"read:"..cpath..",rpath:"..rpath)
    local self = {
         cpath = cpath,
         rpath = rpath,
    }
    local p = setmetatable(self, mt)
    return p
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
    ngx.log(ngx.ERR,"read_file_body:"..filename)
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
    ngx.log(ngx.ERR,"read:"..name)
    ngx.log(ngx.ERR,"read2:".. f)
   
    fbody = self:read_file_body(f)
    ngx.log(ngx.ERR,"read3:".. fbody)
    if fbody == nil then
        return {}
    end
    return json.decode(fbody)
end

function _M.t(self)
    ngx.say(',,,')
end


return _M

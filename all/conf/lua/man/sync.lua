function redirect()
    local protocol = ngx.var.http_x_forwarded_proto or 'http'
    local pixel = protocol .. '://s.opendsp.com/1x1.gif'
    return ngx.redirect(pixel, ngx.HTTP_MOVED_TEMPORARILY)
end

function status(msg)
    ngx.var.status_msg = msg
end

local query = ngx.req.get_uri_args(5)

local google_gid = query['google_gid']
if not google_gid then
    status('google_gid arg is missing')
    return redirect()
elseif #google_gid ~= 27 then
    status('google_gid arg is invalid')
    return redirect()
end

local uid = ngx.var.uid_set or ngx.var.uid_got
if not uid then
    status('uid var is missing')
    return redirect()
end
uid = uid:sub(6)

local redis = require 'resty.redis'
local parameters = {
    host = '127.0.0.1',
    port = 6379,
    database = 1,
    timeout = 2
}

local client = redis:new()
client:set_timeout(parameters.timeout * 1000)
client:connect(parameters.host, parameters.port)
client:select(parameters.database)

local ok, err = client:hset(uid, 'dbm', google_gid)
if err then
    status('hset error: ' .. err)
    return redirect()
end

local timestamp = os.time() + 15724800
local ok, err = client:expireat(uid, timestamp)
if err then
    status('expireat error: ' .. err)
end

return redirect()

local secs = "N/A"
local dec_ck = "N/A"
local proto = "http";
local step = 0
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end
-- If we don't have uid
local retag = ngx.req.get_query_args()['retag']
if not retag then
    retag = ""
end
local redir = proto .. "://s.opendsp.com/1x1.gif"
local qs = ngx.var.query_string
if qs then
    qs = "?seg=" .. ngx.var.segment .. "&" .. qs
else
    qs = "?seg=" .. ngx.var.segment
end
redir = proto .. "://s.opendsp.com/man/xchout/" .. qs
local ok = ""
local err = ""
local ok2 = ""
if ngx.var.host ~= "s.opendsp.com" then
    redir = proto .. "://s.opendsp.com/" .. ngx.var.relpath
else
    step = 1
    local redis = require "resty.redis"
    local red = redis:new()
    red:set_timeout(100)
    --	      ok, err = red:connect("segments.opendsp.com", 6379)
    ok, err = red:connect("172.31.48.243", 6379)
    step = 2

    if not err or err == ngx.null then
        err = ""
    end
    if not ok or ok == ngx.null then
        ok = ""
    end

    if not ok then
        ok = ""
        step = 3
        ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. "}"
        ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY);
        return
    end
    step = 4
    dec_ck = ngx.var.uid_got
    if not dec_ck or dec_ck == ngx.null then
        dec_ck = ngx.var.uid_set
        ok = ok .. "SET: " .. ngx.var.uid_set
        if not dec_ck or dec_ck == ngx.null then
            err = "No uid_got or uid_set"
            step = 5
            ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. "}"
            ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)
            return
        end
    end
    step = 6
    secs = math.floor(ngx.now())
    sub = string.gsub(dec_ck, ngx.var.kyku .. "=", "")
    ngx.var.comment = "SUBSTITUTION: " .. dec_ck .. ": " .. sub

    ok2, err = red:zadd("segment:" .. ngx.var.segment, secs, dec_ck)
    if not err or err == ngx.null then
        err = ""
    end

    if not ok2 or ok2 == ngx.null then
        ok2 = ""
        step = 7
        ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. "}"
        ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY);
        return
    end
    -- Hello
    -- Goodbye
    ok = ok .. "; " .. ok2
    step = 8
end
if not dec_ck then
    dec_ck = "N/A"
    secs = "N/A"
end
ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. ",segment:" .. ngx.var.segment .. ",secs:" .. secs .. ",uid:" .. dec_ck .. "}"
if ngx.var.uid_reset == "" then
    ngx.var.uid_reset = nil
end
ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)

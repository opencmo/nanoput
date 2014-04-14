local proto = "http"
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end

local scid = ngx.req.get_query_args()["scid"]
if not scid then
    scid = "0"
end
if ngx.var.uid_reset == "" then
    ngx.var.uid_reset = nil
end

redir_url = proto .. "://s.opendsp.com/man/conversion/?scid=" .. ngx.var.scid
ngx.redirect(redir_url, ngx.HTTP_MOVED_TEMPORARILY)

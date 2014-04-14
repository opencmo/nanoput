local M = {}

function M.url_encode(str)
    if (str) then
        str = string.gsub(str, "\n", "\r\n")
        str = string.gsub(str, "([^%w %-%_%.%~])",
            function(c) return string.format("%%%02X", string.byte(c)) end)
        str = string.gsub(str, " ", "+")
    end
    return str
end

function M.make_urlsafe(str)
    -- https://en.wikipedia.org/wiki/Base64#URL_applications
    return str:gsub('+', '-'):gsub('/', '_'):gsub('=', '')
end

function M.encode_userid(name, hash)
    -- http://www.lexa.ru/programs/mod-uid.html
    local binary_string = ''
    for i = #name + 2, 35, 8 do
        local chunk = tonumber(hash:sub(i, i + 7), 16)
        for j = 1, 4 do
            binary_string = binary_string .. string.char(chunk % 256)
            chunk = math.floor(chunk / 256)
        end
    end
    return ngx.encode_base64(binary_string)
end

return M
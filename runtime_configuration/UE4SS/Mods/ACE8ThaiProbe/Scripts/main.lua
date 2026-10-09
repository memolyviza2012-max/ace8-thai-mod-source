-- AC8 Thai diagnostic. Read object names only; no text/gameplay/memory changes.
local output = "ACE8Thai_RuntimeProbe.log"
local function log(message)
    local file = io.open(output, "a")
    if file then file:write(os.date("%Y-%m-%d %H:%M:%S"), " ", message, "\n"); file:close() end
    print("[ACE8ThaiProbe] " .. message .. "\n")
end
log("START: Lua loaded; read-only probe; no signature patch")
local function scan(label)
    local records = {}
    local visited = 0
    local ok, err = pcall(function()
        ForEachUObject(function(object)
            visited = visited + 1
            if #records >= 8000 then return end
            local got, name = pcall(function() return object:GetFullName() end)
            if not got or type(name) ~= "string" then return end
            local lower = string.lower(name)
            local wanted = lower:find("localiz", 1, true) or lower:find("gametext", 1, true)
                or lower:find("stringtable", 1, true) or lower:find("nui", 1, true)
                or lower:find("mainmenu", 1, true) or lower:find("font", 1, true)
                or lower:find("textblock", 1, true) or lower:find("pakfile", 1, true)
            if wanted then
                local addr = "unknown"
                pcall(function() addr = tostring(object:GetAddress()) end)
                records[#records+1] = name .. " | address=" .. addr
            end
        end)
    end)
    log(label .. " objects=" .. visited .. " matches=" .. #records .. " success=" .. tostring(ok))
    if not ok then log("ERROR: " .. tostring(err)) end
    table.sort(records)
    local file = io.open(output, "a")
    if file then
        for _, line in ipairs(records) do file:write(line, "\n") end
        file:close()
    end
    log(label .. " COMPLETE")
end
local function schedule(milliseconds, label)
    ExecuteWithDelay(milliseconds, function()
        ExecuteInGameThread(function() scan(label) end)
    end)
end
schedule(20000, "SCAN20")
schedule(50000, "SCAN50")

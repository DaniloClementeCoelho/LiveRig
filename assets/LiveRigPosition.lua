-- @description LiveRig Position Service

local resource_path = reaper.GetResourcePath()
local runtime_dir = resource_path .. "/LiveRig"

reaper.RecursiveCreateDirectory(runtime_dir, 0)

local output_file = runtime_dir .. "/position.txt"
--reaper.ShowConsoleMsg("Arquivo: " .. output_file .. "\n")
--reaper.ShowConsoleMsg(output_file .. "\n")

local project_ready = false
local last_project = ""


function Main()
    --reaper.ShowConsoleMsg("LiveRig iniciado\n")
    local _, project = reaper.EnumProjects(-1, "")

    if project ~= last_project then
        last_project = project
        project_ready = false
    end

    if not project_ready then
        project_ready = true
    end

    local playing = reaper.GetPlayState()
    local position = reaper.GetPlayPosition()

    local file, err = io.open(output_file, "w")

    if not file then
        --reaper.ShowConsoleMsg("Erro abrindo arquivo: " .. tostring(err) .. "\n")
    else
        --reaper.ShowConsoleMsg("Arquivo aberto com sucesso\n")
    end

    if file then
        file:write(string.format("%.3f\n", position))
        --file:write(string.format("%d\n", playing))
        --reaper.ShowConsoleMsg("PlayState = " .. tostring(playing) .. "\n")
        file:write(string.format("%d\n", playing))
        file:write(string.format("%d\n", project_ready and 1 or 0))
        file:close()
    end

    reaper.defer(Main)

end

Main()
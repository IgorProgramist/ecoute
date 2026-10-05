param(
    [string]$QuestionFile = "",
    [string]$OutputFile = "",
    [string]$Mode = "run",
    [int]$MinQuestions = 100,
    # -Queue: ecoute з ЧЕРГОЮ, як на інтерв'ю. Наступне питання звучить лише коли
    # стрічка доїхала до кінця і минула пауза PauseSeconds (питання не нагромаджуються).
    # Без -Queue: черга вимкнена, пауза після відповіді 10 с (старий режим)
    [switch]$Queue,
    [int]$PauseSeconds = 10
)
$ErrorActionPreference = "Continue"

$ecouteDir  = "I:\My\AI\MAIN_WORK_AI\ecouter-project\ecoute"
$logPath    = Join-Path $ecouteDir "last_run.log"
$statusPath = Join-Path $env:TEMP "opencode\qa_status.txt"
$utf8nb     = New-Object System.Text.UTF8Encoding($false)

function Set-Status([string]$s) {
    [System.IO.File]::WriteAllText($statusPath, $s + "`n", $utf8nb)
}

if (-not $QuestionFile) { Set-Status "FATAL no QuestionFile"; exit 1 }
if (-not $OutputFile)   { Set-Status "FATAL no OutputFile"; exit 1 }

$qPath  = Join-Path $ecouteDir $QuestionFile
$qaPath = Join-Path $ecouteDir $OutputFile

# ---------- questions: supports "- " and "N. " numbering ----------
$questions = @()
Get-Content $qPath -Encoding UTF8 | ForEach-Object {
    $t = $_.Trim()
    if (-not $t) { return }
    if ($t -match '^-(.+)$') { $t = $Matches[1].Trim() }
    elseif ($t -match '^(\d+)[.)]\s+(.+)$') { $t = $Matches[2].Trim() }
    else { return }
    if ($t) {
        $t = $t -replace '^\*+', ''
        if ($t) { $questions += $t }
    }
}
$Qn = $questions.Count
if ($Qn -lt $MinQuestions) { Set-Status "FATAL questions parse failed ($Qn found)"; exit 1 }

if ($Mode -eq "validate") {
    Write-Output ("VALIDATE OK | file=" + $QuestionFile + " | questions=" + $Qn)
    Write-Output ("first: " + $questions[0])
    Write-Output ("mid:   " + $questions[[int]($Qn / 2)])
    Write-Output ("last:  " + $questions[$Qn - 1])
    Write-Output ("output will be: " + $qaPath)
    exit 0
}

# ---------- clean log before every run (Igor 2026-10-04: old lines must not mix into a new test) ----------
if (Test-Path $logPath) { [System.IO.File]::WriteAllText($logPath, "") }

# ---------- ecoute log baseline (only new content counts) ----------
$script:logOffset = (Get-Item $logPath -ErrorAction Stop).Length

function Read-NewLog {
    $fs = [System.IO.File]::Open($logPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        if ($fs.Length -le $script:logOffset) { return "" }
        $fs.Position = $script:logOffset
        $sr = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8, $true, 8192)
        $text = $sr.ReadToEnd()
        $sr.Dispose()
    } finally { $fs.Dispose() }
    if (-not $text) { return "" }
    $lastNl = $text.LastIndexOf("`n")
    if ($lastNl -lt 0) { return "" }
    $complete = $text.Substring(0, $lastNl + 1)
    $script:logOffset += [System.Text.Encoding]::UTF8.GetByteCount($complete)
    # two threads of the prompter sometimes print on ONE line
    # ("[LISTEN] alive ...[MATCH] fired prepared answer: ..."); the checks below
    # look at the START of a line, so the answer was missed and the row said [none].
    # Put every log tag back on its own line.
    return [regex]::Replace($complete, '(?<!\n)(\[(?:MATCH|AI|PROMPT|TRANS|LISTEN|INFO|CONTROL|WARN)\] )', "`n`$1")
}

# ---------- launch ecoute fresh ----------
$ecouteArgs = @("-3.14","-u","main.py","--active")
if (-not $Queue) { $ecouteArgs += "--no-queue" }
$proc = Start-Process -FilePath "py" -ArgumentList $ecouteArgs `
        -WorkingDirectory $ecouteDir -WindowStyle Hidden -PassThru

$ready = $false
$deadline = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $deadline) {
    if ($proc.HasExited) { break }
    if ((Read-NewLog).Contains("READY")) { $ready = $true; break }
    Start-Sleep -Milliseconds 500
}
if (-not $ready) {
    $ex = ""
    if ($proc.HasExited) { $ex = " (process exited, code $($proc.ExitCode))" }
    Set-Status "FATAL no READY within 120s$ex"
    exit 1
}
Set-Status "RUNNING 0/$Qn | ecoute READY ($QuestionFile), warming up"
Start-Sleep -Seconds 5

# ---------- QA output header (fresh overwrite) ----------
$started = Get-Date
$header = @(
"# QA_test - ПОВНИЙ ПРОГІН $Qn/$Qn ($($started.ToString('yyyy-MM-dd')), $($started.ToString('HH:mm'))-ENDTIME)",
"",
"Setup: WHISPER_MODEL=small (CPU int8), AI=glm-5.3-flash via opencode zen (reasoning_effort=low, max_tokens=900).",
"Питання програні SAPI TTS (Microsoft Zira Desktop, en-US, rate 0) у динаміки; ecoute слухав WASAPI-loopback (--active).",
"Файл питань: $QuestionFile | окремий свіжий запуск ecoute для цього файлу.",
"HEARD = дослівний буфер питання з last_run.log ([MATCH] question complete). ANSWER = повний текст що виїхав у стрічці.",
"Джерело: [prepared] = відповідь з answers.md вербатим, [AI] = динамічна відповідь, [none] = нічого не показано.",
"Політика прогону: чекання відповіді до 85с; не почуте питання перегравалось 1 раз; наступне питання через 10с після відповіді.",
""
) -join "`r`n"
[System.IO.File]::WriteAllText($qaPath, $header + "`r`n", (New-Object System.Text.UTF8Encoding($true)))

# ---------- TTS ----------
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $synth.SelectVoice("Microsoft Zira Desktop") } catch { }

$stats = @{ prepared = 0; ai = 0; none = 0 }
$idx = 0
$prevPrepared = $false

foreach ($q in $questions) {
    $idx++
    Set-Status ("RUNNING $idx/$Qn | " + $q.Substring(0, [Math]::Min(60, $q.Length)))

    $heard = ""; $answer = ""; $src = ""; $note = ""; $heardSeen = $false; $fires = 0; $needAi = $false; $fallback = ""
    # drop log lines that belong to the PREVIOUS question (late second fire, late
    # AI answer): they used to be recorded as this question's HEARD -> rows shifted
    [void](Read-NewLog)
    $t0 = Get-Date
    $attempts = 0
    $speakS = 0

    while ($attempts -lt 2 -and -not $heard -and -not $proc.HasExited) {
        $attempts++
        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $synth.Speak($q)
            $speakS = [Math]::Round($sw.Elapsed.TotalSeconds, 1)
        } catch {
            $note = "TTS error: " + $_.Exception.Message
            break
        }
        $tSpeechEnd = Get-Date
        while (((Get-Date) -lt $tSpeechEnd.AddSeconds(22)) -and -not $heard) {
            $t = Read-NewLog
            if ($t) {
                foreach ($ln in ($t -split "`r?`n")) {
                    if (-not $ln) { continue }
                    if ($ln.StartsWith("[MATCH] question complete: ")) {
                        $fires++
                        if (-not $heard) { $heard = $ln.Substring(27); $heardSeen = $true }
                        else { $heard += " || " + $ln.Substring(27) }
                    }
                    elseif ($heardSeen -and -not $answer -and $ln.StartsWith("[MATCH] acknowledgement ignored")) {
                        $src = "ignored"; $answer = "(not a question - ribbon left alone)"
                    }
                    elseif ($ln -match '^\[MATCH\] glued prepared answers; parts left for AI: (\d+)') {
                        # prepared answers shown now, AI still owes the remaining parts
                        $needAi = ([int]$Matches[1] -gt 0)
                    }
                    elseif ($heardSeen -and -not $answer -and $ln.StartsWith("[MATCH] fired prepared answer: ")) {
                        $src = "prepared"; $answer = $ln.Substring(31)
                    }
                    elseif ($needAi -and $answer -and $ln.StartsWith("[AI] dynamic answer: ")) {
                        $src = "prepared+ai"; $answer += " ||AI|| " + $ln.Substring(21); $needAi = $false
                    }
                    elseif ($heardSeen -and -not $answer -and $ln.StartsWith("[AI] dynamic answer: ")) {
                        $src = "ai"; $answer = $ln.Substring(21)
                    }
                    elseif ($ln.StartsWith("[AI] ")) {
                        $note = $ln.Substring(0, [Math]::Min(140, $ln.Length))
                    }
                    elseif ($heardSeen -and $src -eq "ai" -and $answer -and -not $ln.StartsWith("[")) {
                        $answer += " " + $ln
                    }
                }
            }
            Start-Sleep -Milliseconds 400
        }
    }

    if ($heard -and (-not $answer -or $needAi) -and -not $proc.HasExited) {
        $ansDeadline = (Get-Date).AddSeconds(85)
        while ((Get-Date) -lt $ansDeadline -and (-not $answer -or $needAi)) {
            $t = Read-NewLog
            if ($t) {
                foreach ($ln in ($t -split "`r?`n")) {
                    if (-not $ln) { continue }
                    if ($ln.StartsWith("[MATCH] question complete: ")) {
                        $fires++
                        $heard += " || " + $ln.Substring(27)
                    }
                    elseif ($ln.StartsWith("[MATCH] acknowledgement ignored")) {
                        if (-not $src) { $src = "ignored"; $answer = "(not a question - ribbon left alone)" }
                    }
                    elseif ($ln -match '^\[MATCH\] glued prepared answers; parts left for AI: (\d+)') {
                        $needAi = ([int]$Matches[1] -gt 0)
                    }
                    elseif ($ln.StartsWith("[MATCH] fired prepared answer: ")) {
                        if (-not $src) { $src = "prepared"; $answer = $ln.Substring(31) }
                    }
                    elseif ($ln.StartsWith("[AI] dynamic answer: ")) {
                        if (-not $src) { $src = "ai"; $answer = $ln.Substring(21) }
                        elseif ($needAi) { $src = "prepared+ai"; $answer += " ||AI|| " + $ln.Substring(21); $needAi = $false }
                    }
                    elseif ($ln.StartsWith("[AI] fallback shown: ")) {
                        # the AI server is silent: the ribbon shows spare text, keep waiting for the AI
                        $fallback = $ln.Substring(21)
                    }
                    elseif ($ln.StartsWith("[AI] ")) {
                        $note = $ln.Substring(0, [Math]::Min(140, $ln.Length))
                    }
                    elseif ($src -eq "ai" -and $answer -and -not $ln.StartsWith("[")) {
                        $answer += " " + $ln
                    }
                }
            }
            if ($proc.HasExited) { break }
            Start-Sleep -Milliseconds 400
        }
        if (-not $answer -and $fallback) {
            $src = "fallback"
            $answer = $fallback
        }
        elseif (-not $answer) {
            $src = "none"
            $answer = "[none: no answer within 85s]"
            if ($note) { $answer += " | note: " + $note }
            elseif ($prevPrepared) { $answer += " | possible refire/dup-guard (nothing fired after previous prepared answer)" }
        }
    }
    elseif (-not $heard) {
        $src = "none"
        if (-not $note) { $note = "not heard in 2 attempts" }
        $answer = "[none: $note]"
    }

    if ($fallback -and $src -eq "ai") { $note = ("fallback text was on the ribbon first" + $(if ($note) { " | " + $note } else { "" })) }
    # the prompter cut ONE spoken question into several: say so in the row
    if ($fires -gt 1) { $note = ("FIRED $fires TIMES for one question" + $(if ($note) { " | " + $note } else { "" })) }
    $dur = [Math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    # how long the candidate waits: from the last spoken word to the answer on the ribbon
    # (3s of it is the prompter waiting for silence to be sure the question ended)
    $waitS = [Math]::Round(((Get-Date) - $tSpeechEnd).TotalSeconds, 1)
    $heardOut = if ($heard) { $heard } else { "(not heard)" }
    $row = "## Q{0:D3} - {1}`r`n- HEARD: {2}`r`n- ANSWER [{3}]: {4}`r`n- time: speak {5}s, answer {8}s after the question ended, total {6}s{7}`r`n`r`n" -f `
        $idx, $q, $heardOut, $src, $answer, $speakS, $dur, $(if ($note -and $heard) { " | note: " + $note } else { "" }), $waitS
    [System.IO.File]::AppendAllText($qaPath, $row, $utf8nb)

    switch ($src) {
        "prepared" { $stats.prepared++ }
        "prepared+ai" { $stats.prepared++ }
        "ai"       { $stats.ai++ }
        default    { $stats.none++ }
    }
    $prevPrepared = ($src -eq "prepared")

    if ($proc.HasExited) {
        Set-Status "FATAL ecoute exited at question $idx/$Qn"
        exit 1
    }
    if ($Queue) {
        # чекаємо, поки стрічка доїде: останній "ribbon done" пізніше за останній "START ribbon"
        $ribbonDeadline = (Get-Date).AddSeconds(150)
        while ((Get-Date) -lt $ribbonDeadline) {
            $fsQ = [System.IO.File]::Open($logPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
            try {
                $srQ = New-Object System.IO.StreamReader($fsQ, [System.Text.Encoding]::UTF8, $true, 8192)
                $all = $srQ.ReadToEnd()
                $srQ.Dispose()
            } finally { $fsQ.Dispose() }
            if ($all.LastIndexOf("[PROMPT] ribbon done") -ge $all.LastIndexOf("[PROMPT] START ribbon")) { break }
            Start-Sleep -Milliseconds 500
        }
    }
    Start-Sleep -Seconds $PauseSeconds
}

# ---------- finish ----------
if (-not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
$end = Get-Date
$qaText = [System.IO.File]::ReadAllText($qaPath)
$qaText = $qaText.Replace("-ENDTIME)", "-" + $end.ToString("HH:mm") + ")")
$summary = "----------`r`n`r`n## Підсумок`r`n" +
    "- Питань: $idx/$Qn | prepared: $($stats.prepared) | AI: $($stats.ai) | none: $($stats.none)`r`n" +
    "- Час: $($started.ToString('HH:mm')) - $($end.ToString('HH:mm')) ($([Math]::Round(($end - $started).TotalMinutes, 1)) хв)`r`n"
[System.IO.File]::WriteAllText($qaPath, $qaText + $summary, $utf8nb)
Set-Status "DONE $idx/$Qn ($QuestionFile) | prepared=$($stats.prepared) ai=$($stats.ai) none=$($stats.none) | minutes=$([Math]::Round(($end - $started).TotalMinutes, 1))"
exit 0

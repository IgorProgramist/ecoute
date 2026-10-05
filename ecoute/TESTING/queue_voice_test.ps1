# Голосовий тест ЧЕРГИ: справжній ecoute (черга ввімкнена), питання голосом,
# інтерв'юер перебиває стрічку. Запуск з теки ecoute:
#   powershell -ExecutionPolicy Bypass -File TESTING\queue_voice_test.ps1
# Під час тесту можна тиснути стрілки - у last_run.log буде рядок [QUEUE] на кожне.
$ErrorActionPreference = "Continue"
$ecoute = Split-Path -Parent $PSScriptRoot
Set-Location $ecoute
$log = Join-Path $ecoute "last_run.log"
[System.IO.File]::WriteAllText($log, "")          # чистий лог перед прогоном

$proc = Start-Process -FilePath "py" -ArgumentList "-3.14","-u","main.py","--active" -PassThru -WindowStyle Hidden
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 1
    if (Select-String -Path $log -Pattern "^READY" -Quiet) { break }
}
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$t0 = Get-Date
$marks = @()

function Say([string]$scene, [string]$text, [int]$waitAfter) {
    $at = [int]((Get-Date) - $t0).TotalSeconds
    $script:marks += ("{0,4}s  {1}  {2}" -f $at, $scene, $text)
    $voice.Speak($text)
    Start-Sleep -Seconds $waitAfter
}

Start-Sleep -Seconds 2
# сцена 1: перебивання посеред стрічки
Say "S1 main     " "How do you set up anchors for different aspect ratios?" 11
Say "S1 interrupt" "What is a Canvas?" 60
# сцена 2: дві репліки підряд під час стрічки - мають склеїтись в одну відповідь
Say "S2 main     " "How do you reduce overdraw in UI?" 10
Say "S2 remark 1 " "What is a draw call?" 6
Say "S2 remark 2 " "And what is batching?" 70
# сцена 3: уточнення, поки AI ще думає над першим питанням
Say "S3 main     " "What is the Emission module of a Particle System?" 4
Say "S3 add      " "What is a Canvas Scaler?" 50
# сцена 4: "дякую" посеред стрічки - у чергу потрапити не має
Say "S4 main     " "How do you optimize textures for mobile?" 10
Say "S4 thanks   " "Okay, great, thank you." 40
# сцена 5: уточнення "розкажи більше" під час короткої готової відповіді
Say "S5 main     " "What is an Animator?" 5
Say "S5 more     " "Tell me more about its parameters." 55

Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Get-Process -Name python -ErrorAction SilentlyContinue |
    Where-Object { $_.StartTime -gt $t0.AddMinutes(-3) } | Stop-Process -Force -ErrorAction SilentlyContinue

"=== що і коли сказано ==="
$marks
"=== лог ecoute ==="
Select-String -Path $log -Pattern "question complete|acknowledgement|QUEUE|START ribbon|latency|Traceback|Error|paused|resumed" |
    ForEach-Object { $_.Line.Substring(0, [Math]::Min(170, $_.Line.Length)) }

# Step 1: Create JSON files for each resume
$resumesCsv = "resumes.csv"

if (-Not (Test-Path $resumesCsv)) {
    Write-Host "CSV file not found!" -ForegroundColor Red
    exit
}

$resumeData = Import-Csv $resumesCsv
$i = 1

foreach ($row in $resumeData) {
    $json = @{
        resume = $row.resume
        job_description = $row.job_description
    } | ConvertTo-Json

    $json | Out-File -FilePath "resume_$i.json" -Encoding UTF8
    $i++
}

Write-Host "JSON files created for each resume." -ForegroundColor Yellow
# Step 1: Create JSON files for each resume
$resumesCsv = "resumes.csv"

if (-Not (Test-Path $resumesCsv)) {
    Write-Host "CSV file not found!" -ForegroundColor Red
    exit
}

$resumeData = Import-Csv $resumesCsv
$i = 1

foreach ($row in $resumeData) {
    $json = @{
        resume = $row.resume
        job_description = $row.job_description
    } | ConvertTo-Json

    $json | Out-File -FilePath "resume_$i.json" -Encoding UTF8
    $i++
}

Write-Host "JSON files created for each resume." -ForegroundColor Yellow

Set-Location 'C:/Users/Iqbal Dev''s/Documents/Website Al Ghifary'
$dest = Join-Path (Get-Location) 'assets'
if(!(Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }
Get-ChildItem -Path (Get-Location) -File -Include *.jpg,*.png | ForEach-Object {
    $brand = $_.BaseName.Split('-')[0]
    $target = Join-Path $dest $brand
    if(!(Test-Path $target)) { New-Item -ItemType Directory -Path $target | Out-Null }
    Move-Item -LiteralPath $_.FullName -Destination $target -Force
}
Write-Host 'Organisasi selesai'
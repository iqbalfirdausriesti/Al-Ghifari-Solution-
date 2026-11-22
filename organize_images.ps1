$repo = 'C:/Users/Iqbal Dev''s/Documents/Website Al Ghifary'
$assets = Join-Path $repo 'assets'
if(!(Test-Path $assets)){ New-Item -ItemType Directory -Path $assets | Out-Null }

Get-ChildItem -Path $repo -File | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png)$' } | ForEach-Object {
    $brand = $_.BaseName.Split('-')[0]
    $target = Join-Path $assets $brand
    if(!(Test-Path $target)){ New-Item -ItemType Directory -Path $target | Out-Null }
    $dest = Join-Path $target $_.Name
    Move-Item -LiteralPath $_.FullName -Destination $dest -Force
    Write-Host "Moved: $($_.Name) -> assets/$brand/"
}

Write-Host "SELESAI - semua gambar sudah dipindahkan ke assets/<brand>/"

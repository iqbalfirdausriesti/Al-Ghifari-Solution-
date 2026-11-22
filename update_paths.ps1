$file = 'C:/Users/Iqbal Dev''s/Documents/Website Al Ghifary/index.html'
$content = Get-Content -LiteralPath $file -Raw
$brands = @('acer','anker','apple','asus','axioo','baseus','dell','google','hp','infinix','lenovo','logitech','msi','oppo','poco','realme','samsung','tecno','vivo','xiaomi')
foreach ($brand in $brands) {
    $pattern = 'src="(' + $brand + '-[^"]+\.jpg)"'
    $replace = 'src="assets/' + $brand + '/$1"'
    $content = [regex]::Replace($content, $pattern, $replace)
}
Set-Content -LiteralPath $file -Value $content -NoNewline
Write-Host 'index.html diperbarui - semua path gambar sudah disesuaikan'

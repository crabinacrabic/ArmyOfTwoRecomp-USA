param(
    [string]$ImagePath = "C:\Users\MSI\.gemini\antigravity\brain\9544e732-c018-4f9b-922c-8b8122ffc4ba\army_of_two_gameplay_live.png"
)

Add-Type -AssemblyName System.Drawing

$bmp = [System.Drawing.Bitmap]::FromFile($ImagePath)
$w = $bmp.Width
$h = $bmp.Height
$total = $w * $h

$rect = [System.Drawing.Rectangle]::new(0, 0, $w, $h)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$bytes = [byte[]]::new($data.Stride * $h)
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $bytes, 0, $bytes.Length)
$bmp.UnlockBits($data)
$bmp.Dispose()

$blown = 0
$sumLum = 0.0
$shadows = 0
$midtones = 0
$highlights = 0

for ($i = 0; $i -lt $bytes.Length; $i += 4) {
    $b = $bytes[$i]
    $g = $bytes[$i+1]
    $r = $bytes[$i+2]
    $lum = 0.299 * $r + 0.587 * $g + 0.114 * $b
    $sumLum += $lum
    
    if ($lum -lt 50) { $shadows++ }
    elseif ($lum -lt 200) { $midtones++ }
    else { $highlights++ }

    if ($r -ge 250 -and $g -ge 250 -and $b -ge 250) {
        $blown++
    }
}

$mean = $sumLum / $total
$pctBlown = 100.0 * $blown / $total
$pctShadows = 100.0 * $shadows / $total
$pctMidtones = 100.0 * $midtones / $total
$pctHighlights = 100.0 * $highlights / $total

Write-Host "================ EXPOSURE ANALYSIS ================"
Write-Host ("Image Resolution:       {0}x{1} ({2} pixels)" -f $w, $h, $total)
Write-Host ("Mean Luminance:         {0:F2} / 255 (ideal range: 100-140)" -f $mean)
Write-Host ("Shadows (<50):          {0:F2}%" -f $pctShadows)
Write-Host ("Midtones (50-200):      {0:F2}%" -f $pctMidtones)
Write-Host ("Highlights (>200):      {0:F2}%" -f $pctHighlights)
Write-Host ("Pure White Blown (>250):{0:F2}% ({1} px)" -f $pctBlown, $blown)
Write-Host "==================================================="

param(
    [Parameter(Mandatory=$true)][string]$InDir,
    [Parameter(Mandatory=$true)][string]$OutFile
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Foundation, ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]
function Await($op, $type) {
    $t = $asTaskGeneric.MakeGenericMethod($type).Invoke($null, @($op))
    $t.Wait(-1) | Out-Null
    $t.Result
}
$lang = New-Object Windows.Globalization.Language "zh-Hans-CN"
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)

$sb = New-Object System.Text.StringBuilder
$files = Get-ChildItem -Path $InDir -Filter *.png | Sort-Object Name
$total = $files.Count
$n = 0
foreach ($f in $files) {
    $n++
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    [void]$sb.AppendLine("<<<PAGE $($f.BaseName)>>>")
    [void]$sb.AppendLine($result.Text)
    [void]$sb.AppendLine("")
    $stream.Dispose()
    if ($n % 10 -eq 0) { Write-Host "  OCR $n/$total" }
}
$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), $enc)
Write-Host "DONE $OutFile  pages=$total"

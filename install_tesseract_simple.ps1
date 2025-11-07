# Instalador simple de Tesseract OCR
Write-Host "=== INSTALADOR DE TESSERACT OCR ===" -ForegroundColor Cyan

# Verificar si ya está instalado
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
)

foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Tesseract ya está instalado en: $path" -ForegroundColor Green
        $tesseractDir = Split-Path $path
        $env:PATH = $env:PATH + ";$tesseractDir"
        & tesseract --version
        exit 0
    }
}

Write-Host "⏳ Descargando Tesseract OCR..." -ForegroundColor Yellow

# Crear directorio temporal
$tempDir = "$env:TEMP\tesseract_install"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# URL del instalador
$url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$installer = "$tempDir\tesseract-installer.exe"

try {
    # Descargar con progreso
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    Write-Host "✅ Descarga completada" -ForegroundColor Green
    
    # Ejecutar instalador silencioso
    Write-Host "⏳ Instalando Tesseract OCR..." -ForegroundColor Yellow
    Write-Host "   (Esto puede tomar unos minutos)" -ForegroundColor Gray
    
    $installArgs = "/S /D=C:\Program Files\Tesseract-OCR"
    Start-Process -FilePath $installer -ArgumentList $installArgs -Wait -NoNewWindow
    
    Write-Host "✅ Instalación completada" -ForegroundColor Green
    
    # Agregar al PATH
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    if (Test-Path "$tesseractPath\tesseract.exe") {
        Write-Host "⏳ Configurando PATH..." -ForegroundColor Yellow
        
        # PATH de la sesión actual
        $env:PATH = $env:PATH + ";$tesseractPath"
        
        # PATH del sistema (requiere permisos de admin)
        try {
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            if ($currentPath -notlike "*$tesseractPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$tesseractPath", "Machine")
                Write-Host "✅ PATH del sistema actualizado" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  No se pudo actualizar PATH del sistema (requiere admin)" -ForegroundColor Yellow
            Write-Host "   PATH de sesión actual configurado correctamente" -ForegroundColor Gray
        }
        
        # Verificar instalación
        Write-Host "`n🧪 Verificando instalación..." -ForegroundColor Cyan
        & tesseract --version
        
        Write-Host "`n✅ ¡Tesseract OCR instalado exitosamente!" -ForegroundColor Green
        Write-Host "`n🚀 Próximo paso: uv run python test_ocr.py" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Error: Tesseract no se instaló correctamente" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error durante la instalacion: $_" -ForegroundColor Red
    Write-Host "`nInstalacion manual:" -ForegroundColor Yellow
    Write-Host "   1. Descargar: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Gray
    Write-Host "   2. Ejecutar instalador como administrador" -ForegroundColor Gray
    Write-Host "   3. Instalar en: C:\Program Files\Tesseract-OCR" -ForegroundColor Gray
} finally {
    # Limpiar archivos temporales
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

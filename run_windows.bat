@echo off
echo ====================================
echo PDF Stamping Tool
echo ====================================
echo.

if "%~1"=="" (
    echo ERROR: No input folder specified
    echo.
    echo Usage: run_windows.bat ^<input_folder^> [output_folder]
    echo.
    echo Examples:
    echo   run_windows.bat C:\Documents\PDFs
    echo   run_windows.bat C:\Documents\PDFs C:\Documents\Stamped
    echo.
    echo Or drag and drop a folder onto this batch file
    echo.
    pause
    exit /b 1
)

echo Input folder: %~1
if not "%~2"=="" (
    echo Output folder: %~2
)
echo.

python stamp_pdf.py %*

if errorlevel 1 (
    echo.
    echo ERROR: Failed to process PDFs
    echo Make sure Python and dependencies are installed
    echo Run install_windows.bat first if needed
    echo.
)

echo.
pause


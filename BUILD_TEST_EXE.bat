@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CatCB v1.10.2 Builder

echo.
echo  CatCB v1.10.2 - EXE Builder
echo  Starting diagnostic build helper...
echo.

where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: Windows could not find the Python launcher ^(py^).
  echo Open CMD in this folder and run: python --version
  echo If Python works under a different command, send us the output.
  echo.
  pause
  exit /b 1
)

py "CatCB_Build_Test_Exe.py"
set "BUILD_RC=%ERRORLEVEL%"

echo.
if "%BUILD_RC%"=="0" (
  echo CatCB.exe build finished successfully.
) else (
  echo CatCB.exe build failed with exit code %BUILD_RC%.
  echo Please send CatCB_build.log from this folder.
)
echo.
pause
exit /b %BUILD_RC%

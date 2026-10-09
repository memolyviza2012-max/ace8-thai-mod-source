@echo off
setlocal
cd /d "%~dp0"
if not exist build mkdir build
"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /platform:x64 /reference:System.Windows.Forms.dll /out:build\ACE8ThaiLauncher.exe ACE8ThaiPortableLauncher.cs
exit /b %errorlevel%

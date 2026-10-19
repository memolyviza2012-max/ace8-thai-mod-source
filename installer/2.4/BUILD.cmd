@echo off
setlocal
cd /d "%~dp0"
if not exist Resources\manifest.json (
 echo First export resources from the official installer:
 echo ACE8ThaiSetup_v2.4.exe --export-resources Resources
 exit /b 1
)
"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /platform:x64 /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll /resource:Resources\manifest.json,ACE8.Manifest /resource:Resources\payload.dat.gz,ACE8.Payload /resource:Resources\Header.jpg,THub.ACE8.Header /resource:Resources\Program.ico,THub.ACE8.ProgramIcon /win32icon:Resources\Program.ico /win32manifest:app.manifest /out:ACE8ThaiSetup_v2.4.exe Engine.cs AutoGamePath.cs BrandedSetupWindow.cs Program.cs
exit /b %errorlevel%

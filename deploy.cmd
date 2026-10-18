@echo off
rem Run deploy.sh from PowerShell or cmd:  .\deploy 01
rem Uses Git Bash explicitly (plain "bash" may start WSL instead).
set "GITBASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%GITBASH%" (
    echo Git Bash not found at %GITBASH%
    exit /b 1
)
"%GITBASH%" "%~dp0deploy.sh" %*

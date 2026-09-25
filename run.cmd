@echo off
rem Double-click or run from cmd; bypasses the PowerShell script execution policy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*

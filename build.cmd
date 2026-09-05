@echo off
setlocal
pushd "%~dp0"
latexmk main.tex %*
set "build_result=%ERRORLEVEL%"
popd
exit /b %build_result%

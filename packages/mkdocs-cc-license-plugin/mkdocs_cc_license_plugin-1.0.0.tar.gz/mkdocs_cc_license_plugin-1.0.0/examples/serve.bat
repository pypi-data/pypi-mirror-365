@echo off
echo Starting MkDocs CC License Plugin - Multilingual Example Server...

:: Check if dependencies are installed
pip install -r requirements.txt >nul 2>&1
pip install -e .. >nul 2>&1

:: Start development server
echo Starting development server...
echo Open http://127.0.0.1:8000 to view the site
echo.
echo Language versions:
echo   🇬🇧 English (default): http://127.0.0.1:8000/
echo   🇫🇷 French:            http://127.0.0.1:8000/fr/
echo.
echo Press Ctrl+C to stop the server
mkdocs serve

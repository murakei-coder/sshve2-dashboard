@echo off
echo ============================================================
echo Raw Data Update Script
echo ============================================================
echo.

echo Step 1: Generating raw data chunks from source files...
python generate_raw_data_chunks_from_source.py
if errorlevel 1 (
    echo [ERROR] Failed to generate chunks
    pause
    exit /b 1
)

echo.
echo Step 2: Adding files to git...
git add data/sourcing_raw_chunks/ data/suppression_raw_chunks/ generate_raw_data_chunks_from_source.py

echo.
echo Step 3: Committing changes...
git commit -m "Update raw data chunks - %date% %time%"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo ============================================================
echo [OK] Update complete!
echo ============================================================
echo GitHub Pages will deploy automatically in 1-2 minutes.
echo.
pause

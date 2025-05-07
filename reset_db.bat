@echo off
echo *** DELETING AND CREATING DATABASE ***

REM Connect to MySQL and execute SQL commands
mysql -u habit_tracker -p -e "DROP DATABASE IF EXISTS habit_tracker_db; CREATE DATABASE habit_tracker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo *** DELETING OLD MIGRATIONS ***
cd users\migrations
del /Q *.*
echo.> __init__.py
cd ..\..

cd habit\migrations
del /Q *.*
echo.> __init__.py
cd ..\..

echo *** CREATING NEW MIGRATIONS ***
python manage.py makemigrations
python manage.py migrate

echo *** FINISHED ✅ ***
pause

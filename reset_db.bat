@echo off
REM Statements won't be display ↑↑↑
:: ===========================================
:: AUTOMATED DATABASE RESET AND MIGRATION SCRIPT
:: ===========================================
:: This script will:
:: 1. Delete and recreate the MySQL database
:: 2. Remove old migrations in Django applications
:: 3. Create new migrations for the Django project
:: ===========================================

echo *** DELETING AND CREATING DATABASE ***

REM Connect to MySQL and execute SQL commands
mysql -u %DB_USER% -p%DB_PASSWORD% -e "DROP DATABASE IF EXISTS %DB_NAME%; CREATE DATABASE %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

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

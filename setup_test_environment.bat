@echo off
echo 🚀 Setting up test environment for Social Consensus Backend...
echo ==================================================

echo 📋 Step 1: Creating database migrations...
python manage.py makemigrations custom_auth
if %errorlevel% neq 0 (
    echo ❌ Error creating custom auth migrations
    pause
    exit /b 1
)
echo ✅ Custom auth migrations created successfully

echo 📋 Step 2: Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Error running database migrations
    pause
    exit /b 1
)
echo ✅ Database migrations completed successfully

echo 📋 Step 3: Creating test data...
python manage.py create_test_data
if %errorlevel% neq 0 (
    echo ❌ Error creating test data
    pause
    exit /b 1
)
echo ✅ Test data created successfully

echo 📋 Step 4: Creating superuser (optional)...
echo Creating superuser with email: admin@test.com
echo Password: admin123
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@test.com', 'admin123') if not User.objects.filter(email='admin@test.com').exists() else print('ℹ️  Superuser already exists')"

echo.
echo 🎉 Setup completed successfully!
echo ==================================================
echo.
echo 📋 QUICK ACCESS INFORMATION:
echo.
echo 🔗 Magic Link Login Page:
echo    http://localhost:8000/auth/magic-link/
echo.
echo 👥 All Test Users:
echo    http://localhost:8000/auth/test-users/
echo.
echo ⚙️ Admin Panel:
echo    http://localhost:8000/admin/
echo    Email: admin@test.com
echo    Password: admin123
echo.
echo 📊 TEST ACCOUNTS CREATED:
echo    📧 44 Researchers: researcher01@test.com to researcher44@test.com
echo    📧 5 Companies: company01@test.com to company05@test.com
echo    🔒 Password for all: testpass123
echo.
echo 🚀 Ready for testing!
echo Start the server with: python manage.py runserver
pause

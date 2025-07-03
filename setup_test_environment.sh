#!/bin/bash

echo "🚀 Setting up test environment for Social Consensus Backend..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Step 1: Creating database migrations...${NC}"
python manage.py makemigrations custom_auth
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Custom auth migrations created successfully${NC}"
else
    echo -e "${RED}❌ Error creating custom auth migrations${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Step 2: Running database migrations...${NC}"
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Error running database migrations${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Step 3: Creating test data...${NC}"
python manage.py create_test_data
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Test data created successfully${NC}"
else
    echo -e "${RED}❌ Error creating test data${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Step 4: Creating superuser (optional)...${NC}"
echo "Creating superuser with email: admin@test.com"
echo "Password: admin123"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@test.com').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('✅ Superuser created successfully')
else:
    print('ℹ️  Superuser already exists')
"

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}📋 QUICK ACCESS INFORMATION:${NC}"
echo ""
echo "🔗 Magic Link Login Page:"
echo "   http://localhost:8000/auth/magic-link/"
echo ""
echo "👥 All Test Users:"
echo "   http://localhost:8000/auth/test-users/"
echo ""
echo "⚙️ Admin Panel:"
echo "   http://localhost:8000/admin/"
echo "   Email: admin@test.com"
echo "   Password: admin123"
echo ""
echo -e "${YELLOW}📊 TEST ACCOUNTS CREATED:${NC}"
echo "   📧 44 Researchers: researcher01@test.com to researcher44@test.com"
echo "   📧 5 Companies: company01@test.com to company05@test.com"
echo "   🔒 Password for all: testpass123"
echo ""
echo -e "${GREEN}🚀 Ready for testing!${NC}"
echo "Start the server with: python manage.py runserver"

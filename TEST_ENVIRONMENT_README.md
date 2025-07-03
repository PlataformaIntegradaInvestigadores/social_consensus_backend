# 🧪 Test Environment Setup

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Build and start services
docker-compose up -d

# Run setup inside container
docker-compose exec web python manage.py create_test_data

# Access the application
# Magic Link Login: http://localhost:8000/auth/magic-link/
```

### Option 2: Local Development
```bash
# Windows
setup_test_environment.bat

# Linux/Mac
chmod +x setup_test_environment.sh
./setup_test_environment.sh
```

## 📋 What Gets Created

### 👥 Test Users
- **44 Researchers**: researcher01@test.com to researcher44@test.com
- **5 Companies**: company01@test.com to company05@test.com
- **Password**: testpass123 (for all accounts)

### 📝 Sample Data
- **20+ Jobs** posted by companies
- **40+ Feed Posts** from researchers
- **Comments and Likes** on posts
- **Realistic user profiles** with research fields, institutions, skills

## 🔗 Magic Link Login System

### Quick Access URLs
- **Magic Link Login**: `http://localhost:8000/auth/magic-link/`
- **All Test Users**: `http://localhost:8000/auth/test-users/`
- **Admin Panel**: `http://localhost:8000/admin/` (admin@test.com / admin123)

### How Magic Links Work
1. Enter email on login page
2. Get instant magic link (no email sending in test mode)
3. Click link to login automatically
4. Link expires in 30 minutes

### One-Click Login
- Click any user card on test users page
- Automatically generates and uses magic link
- Perfect for rapid testing

## 🛠 Development Commands

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush
```

### Test Data Management
```bash
# Create test data
python manage.py create_test_data

# Clear existing test data and create new
python manage.py create_test_data --clear

# Create superuser
python manage.py createsuperuser
```

## 🎯 Testing Scenarios

### For Researchers
1. Login as researcher01@test.com
2. Browse job listings
3. Apply to jobs
4. Create feed posts
5. Comment on posts
6. Like posts

### For Companies
1. Login as company01@test.com
2. Post new jobs
3. View job applicants
4. Manage company profile
5. Browse researcher profiles

### For Admins
1. Login to admin panel
2. Manage users and companies
3. View application statistics
4. Monitor platform activity

## 🔧 Configuration Files

### Magic Link Settings
- **Token expiration**: 30 minutes
- **Storage**: Database (MagicLink model)
- **Security**: UUID-based tokens

### Test Data Configuration
- **Researcher count**: 44 (configurable in command)
- **Company count**: 5 (configurable in command)
- **Jobs per company**: 3-5 (random)
- **Posts**: 40 (random authors)

## 📊 Available Test Data

### Research Fields
- Artificial Intelligence
- Machine Learning
- Computer Vision
- Natural Language Processing
- Robotics
- Data Science
- Bioinformatics
- Cybersecurity
- And more...

### Company Industries
- Technology
- Analytics
- Biotechnology
- Finance
- Energy

### Job Types
- Full-time
- Part-time
- Contract
- Internship

## 🚨 Important Notes

### For Production
- Disable magic link system
- Enable proper email sending
- Use secure authentication
- Remove test data

### For Development
- Magic links bypass password checks
- Test data is clearly marked
- Easy to reset and regenerate
- All passwords are 'testpass123'

## 🛡 Security Considerations

### Magic Links
- ✅ Expire after 30 minutes
- ✅ Single use only
- ✅ UUID-based tokens
- ✅ Database tracking
- ⚠️ Only for testing/development

### Test Data
- ✅ All test emails contain 'test'
- ✅ Easy to identify and clean
- ✅ Separate from production data
- ✅ Can be cleared with --clear flag

## 🎉 Ready to Test!

Your test environment is now ready with:
- ✅ 44 researcher accounts
- ✅ 5 company accounts  
- ✅ Magic link login system
- ✅ Sample jobs and posts
- ✅ Realistic interaction data

Start testing at: **http://localhost:8000/auth/magic-link/**

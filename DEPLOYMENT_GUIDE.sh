#!/bin/bash
# Quick Reference Commands for Store Performance Platform
# Run these after deploying today's fixes

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Store Performance Platform - Deployment Guide${NC}\n"

# 1. Environment setup
echo -e "${YELLOW}Step 1: Environment Setup${NC}"
echo "cd /path/to/store_performance"
echo "source .store/bin/activate"
echo ""

# 2. Install dependencies
echo -e "${YELLOW}Step 2: Install Updated Dependencies${NC}"
echo "pip install -r requirements.txt --upgrade"
echo ""

# 3. Migrate database
echo -e "${YELLOW}Step 3: Apply Database Migrations${NC}"
echo "# This applies the new performance indexes"
echo "python manage.py migrate"
echo ""

# 4. Collect static files
echo -e "${YELLOW}Step 4: Collect Static Files${NC}"
echo "python manage.py collectstatic --noinput"
echo ""

# 5. Health check
echo -e "${YELLOW}Step 5: Run Health Check${NC}"
echo "python health_check.py"
echo ""

# 6. Restart services
echo -e "${YELLOW}Step 6: Restart Services${NC}"
echo "# Django development server (if using runserver)"
echo "python manage.py runserver"
echo ""
echo "# OR if using gunicorn/uWSGI:"
echo "# systemctl restart gunicorn  # (or your service name)"
echo ""

# 7. Celery (if using async tasks)
echo -e "${YELLOW}Step 7: Restart Celery (if enabled)${NC}"
echo "# In separate terminal:"
echo "celery -A performance worker --loglevel=info"
echo ""
echo "# In another terminal:"
echo "celery -A performance beat --loglevel=info"
echo ""

# 8. Verification steps
echo -e "${YELLOW}Step 8: Verification Steps${NC}"
echo -e "${GREEN}✓ Check Django admin: http://localhost:8000/admin${NC}"
echo -e "${GREEN}✓ Check dashboard: http://localhost:8000/dashboard${NC}"
echo -e "${GREEN}✓ Check API: http://localhost:8000/api${NC}"
echo -e "${GREEN}✓ Test on mobile (responsive design)${NC}"
echo ""

# Common troubleshooting commands
echo -e "${YELLOW}Troubleshooting Commands${NC}"
echo ""
echo "# Check migrations status:"
echo "python manage.py showmigrations"
echo ""
echo "# See applied migrations:"
echo "python manage.py showmigrations --list"
echo ""
echo "# Rollback migration if needed:"
echo "python manage.py migrate core 0027"
echo ""
echo "# Clear cache:"
echo "python manage.py shell"
echo "# >>> from django.core.cache import cache"
echo "# >>> cache.clear()"
echo "# >>> exit()"
echo ""
echo "# Check database indexes:"
echo "python manage.py sqlsequencereset core"
echo ""

# Performance monitoring
echo -e "${YELLOW}Performance Monitoring${NC}"
echo ""
echo "# Enable query logging (development only):"
echo "# Add to settings_dev.py:"
echo "# LOGGING = { ... 'django.db.backends': {'level': 'DEBUG'} }"
echo ""
echo "# Monitor slow queries:"
echo "# Check Django logs for query timing information"
echo ""

# Database backup (PostgreSQL example)
echo -e "${YELLOW}Database Backup (PostgreSQL)${NC}"
echo "# Backup before deployment:"
echo "pg_dump -U postgres store_performance > backup_$(date +%Y%m%d_%H%M%S).sql"
echo ""
echo "# Restore if needed:"
echo "psql -U postgres store_performance < backup_YYYYMMDD_HHMMSS.sql"
echo ""

# Rollback plan
echo -e "${YELLOW}Rollback Plan (if something goes wrong)${NC}"
echo "# 1. Revert migration:"
echo "python manage.py migrate core 0027"
echo ""
echo "# 2. Downgrade packages:"
echo "pip install Django==5.0.7 Pillow==10.4.0 celery==5.3.6"
echo ""
echo "# 3. Restart services"
echo ""

# Success indicators
echo -e "${YELLOW}Success Indicators${NC}"
echo -e "${GREEN}✓ health_check.py runs without errors${NC}"
echo -e "${GREEN}✓ Dashboard loads in < 2 seconds${NC}"
echo -e "${GREEN}✓ API endpoints respond normally${NC}"
echo -e "${GREEN}✓ Mobile menu works smoothly${NC}"
echo -e "${GREEN}✓ Forms submit without errors${NC}"
echo -e "${GREEN}✓ No JavaScript errors in console${NC}"
echo ""

# Documentation links
echo -e "${YELLOW}Documentation${NC}"
echo "📄 Read: PROJECT_AUDIT_REPORT.md"
echo "📄 Read: COMPREHENSIVE_FIXES_SUMMARY.md"
echo "📄 Read: UI_UX_FIXES_SUMMARY.md"
echo ""

echo -e "${GREEN}Deployment guide complete!${NC}"

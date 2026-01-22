# Store Performance Dashboard

A comprehensive Django-based store management and analytics dashboard for tracking products, clients, bills, and business performance metrics.

## Features

- 📊 **Analytics Dashboard** - Real-time business metrics and data visualization
- 👥 **Client Management** - Track customer information and history
- 📦 **Product Management** - Inventory and product catalog
- 🧾 **Billing System** - Create and manage bills for clients
- 📈 **Performance Reports** - Business insights and trends
- 🔐 **User Authentication** - Secure login and user management

## Tech Stack

- **Backend**: Django 5.0.7
- **Database**: SQLite (default) - easily configurable for PostgreSQL/MySQL
- **Admin Panel**: Jazzmin (enhanced Django admin)
- **Data Visualization**: Plotly, Pandas
- **Forms**: Django Crispy Forms
- **Authentication**: Custom user model with email login

## Installation

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/Mouadnait/store_performance.git
cd store_performance/performance
```

2. **Create and activate virtual environment**

```bash
# Using virtualenv
virtualenv .store
source .store/bin/activate  # On Windows: .store\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

5. **Run database migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**

```bash
python manage.py createsuperuser
```

7. **Collect static files** (for production)

```bash
python manage.py collectstatic
```

8. **Start the development server**

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## Usage

### URLs

- `/` - Login page
- `/signup/` - User registration
- `/dashboard/` - Main dashboard with analytics
- `/clients/` - Client management
- `/products/` - Product catalog
- `/create-bill/` - Create new bill
- `/analytics/` - Analytics page
- `/admin/` - Django admin panel

### Default Credentials

Create a superuser using:
```bash
python manage.py createsuperuser
```

## Project Structure

```
performance/
├── core/                      # Core application
│   ├── migrations/           # Database migrations
│   ├── admin.py             # Admin configuration
│   ├── models.py            # Database models
│   ├── views.py             # View controllers
│   ├── forms.py             # Form definitions
│   └── urls.py              # URL routing
├── userauths/                # Authentication app
│   ├── models.py            # Custom user model
│   ├── views.py             # Auth views
│   └── forms.py             # Auth forms
├── performance/              # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI config
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # User uploaded files
├── requirements.txt          # Dependencies
└── manage.py                # Django CLI

```

## Database Models

### User
Custom user model with email-based authentication

### Client
Customer information with contact details

### Product
Product catalog with pricing and inventory

### Category
Product categorization

### Bill
Transaction records linking clients and products

### ProductReview
Customer reviews and ratings

## Security Features

- Email-based authentication
- Password validation
- CSRF protection
- XSS protection
- SQL injection protection
- Secure session management
- Production-ready security settings (when DEBUG=False)

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Code Quality

The project follows Django best practices and PEP 8 style guidelines.

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Generate a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use a production database (PostgreSQL recommended)
5. Configure static file serving
6. Enable HTTPS and security headers
7. Set up proper logging

## Troubleshooting

### Common Issues

**Issue**: Database errors after model changes
```bash
python manage.py makemigrations
python manage.py migrate
```

**Issue**: Static files not loading
```bash
python manage.py collectstatic
```

**Issue**: Permission errors
```bash
# Ensure proper file permissions
chmod -R 755 media/
chmod -R 755 static/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Changelog

### Version 1.0.0
- Initial release
- Core features: Dashboard, Products, Clients, Billing
- Analytics and reporting
- User authentication 
   |
   |-- templates/                        # Root Templates Folder 
   |    |                               
   |    |-- core/       
   |    |    |-- analytics.html          # analytics component
   |    |    |-- client-bills.html       # client-bills component
   |    |    |-- clients.html            # clients Bar
   |    |    |-- create-bill.html        # create-bill Component
   |    |    |-- dashboard.html          # dashboard Component
   |    |    |-- products.html           # products Component
   |    |    |-- reports.html            # reports Component
   |    |    |-- settings.html           # settings Component
   |    |                               
   |    |-- userauths/
   |    |    |-- login.html              # Sign IN Page
   |    |    |-- signup.html             # Sign UP Page
   |    |                               
   |    |-- auth.html                    # extended authentication
   |    |-- base.html                    # extended base
   |    
   |-- ************************************************************************
```

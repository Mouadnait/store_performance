# Store Performance Dashboard

![Berry Bootstrap 5 - Dark-Mode ready, Open-source Template.](https://user-images.githubusercontent.com/51070104/215728710-d1ee7fef-8153-402b-9741-371e1c01cd36.png)

<br />

## Manual Build

> 👉 Download the code  

```bash
git clone https://github.com/Mouadnait/store_performance.git
cd performance
```

<br />

> 👉 Install modules via `VENV`  

```bash
virtualenv store
source store/bin/activate
pip install -r requirements.txt
```

<br />

> 👉 Edit the `.env` using the template `.env.example`.

```env

# True for development, False for production
SECRET_KEY="PUT_YOUR_SECRET_KEY"

```

<br />

> 👉 Set Up Database

```bash
python manage.py makemigrations
python manage.py migrate
```

<br />

> 👉 Create the Superuser

```bash
python manage.py createsuperuser
```

<br />

> 👉 Start the app

```bash
python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`.

<br />

## Codebase structure

The project is coded using a simple and intuitive structure presented below:

```bash
< PROJECT ROOT >
   |
   |-- core/                            
   |    |-- __init__.py                  # APP __init__
   |    |-- admin.py                     # APP Admin
   |    |-- apps.py                      # APP Apps 
   |    |-- forms.py                     # APP Forms 
   |    |-- models.py                    # APP Models
   |    |-- tests.py                     # APP Tests  
   |    |-- urls.py                      # APP Urls Routing
   |    |-- views.py                     # APP Views Routing
   |
   |-- performance/
   |    |-- __init__.py                  # __init__ Routing
   |    |-- asgi.py                      # asgi Routing
   |    |-- urls.py                      # urls Routing
   |    |-- settings.py                  # Project Configuration 
   |    |-- wsgi.py                      # wsgi   
   |    
   |-- userauths/
   |    |-- __init__.py                  # APP __init__
   |    |-- admin.py                     # APP Admin
   |    |-- apps.py                      # APP Apps 
   |    |-- forms.py                     # APP Forms 
   |    |-- models.py                    # APP Models
   |    |-- tests.py                     # APP Tests  
   |    |-- urls.py                      # APP Urls Routing
   |    |-- views.py                     # APP Views Routing
   |    
   |-- requirements.txt                  # Project Dependencies
   |
   |-- env.example                       # ENV Configuration (default values)
   |-- manage.py                         # Start the app - Django default start script
   |
   |-- ************************************************************************
```

<br />

## How to Customize

When a template file is loaded in the controller, `Django` scans all template directories starting from the ones defined by the user, and returns the first match or an error in case the template is not found.
The theme used to style this starter provides the following files:

```bash
# This is saved in ENV: LIB/admin
< UI_LIBRARY_ROOT > 
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

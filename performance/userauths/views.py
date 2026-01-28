from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.html import escape
import logging

# User = settings.AUTH_USER_MODEL
User = get_user_model()
logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def register(request):
    """User registration with security validation."""
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            try:
                new_user = form.save()
                username = escape(form.cleaned_data.get("username"))
                messages.success(request, "Account created successfully. Please log in.")
                logger.info(f"New user registered: {username}")
                # Authenticate the new user
                new_user = authenticate(
                    request,
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"]
                )
                # Check if authentication was successful
                if new_user is not None:
                    login(request, new_user)
                    return redirect("core:dashboard")
                else:
                    # Redirect to login instead of showing error
                    return redirect("userauths:login")
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, "An error occurred during registration. Please try again.")
        else:
            # Don't expose specific validation errors
            messages.error(request, "Please check your input and try again.")
    else:
        form = UserRegisterForm()
    return render(request, "userauths/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login with security validation and rate limiting ready."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Validate input
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "userauths/login.html", {})

        try:
            # Authenticate user (Django's authenticate method already handles password verification)
            user = authenticate(request, username=email, password=password)

            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                logger.info(f"User logged in: {user.username}")
                return redirect("core:dashboard")
            else:
                # Generic message to prevent user enumeration
                messages.error(request, "Invalid credentials. Please try again.")
                logger.warning(f"Failed login attempt for email: {escape(email)}")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
    
    return render(request, "userauths/login.html", {})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Secure user logout."""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        logger.info(f"User logged out: {username}")
    messages.success(request, "You have been logged out.")
    return redirect("userauths:login")

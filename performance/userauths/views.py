from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages

# User = settings.AUTH_USER_MODEL
User = get_user_model()

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account has been created successfully.")
            # Authenticate the new user
            new_user = authenticate(username=form.cleaned_data["username"],
                                    password=form.cleaned_data["password1"])
            # Check if authentication was successful
            if new_user is not None:
                login(request, new_user)
                return redirect("core:dashboard")
            else:
                # Handle the case where authentication fails
                messages.error(request, "Authentication failed. Please try logging in.")
    else:
        form = UserRegisterForm()
    return render(request, "userauths/signup.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in.")
        return redirect("core:dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back {request.user.username}.")
                return redirect("core:dashboard")
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.warning(request, f"User with {email} does not exist.")
    return render(request, "userauths/login.html", {})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("userauths:login")

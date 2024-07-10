from django.shortcuts import render, redirect
from django.http import JsonResponse
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from userauths.forms import UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

@login_required
def home(request):
    return render(request, "core/dashboard.html", {})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account has been created successfully.")
            new_user = authenticate(username=form.cleaned_data["username"],
                                    password=form.cleaned_data["password1"])
            login(request, new_user)
            return redirect("core:dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "userauths/signup.html", {"form": form})

def login_required_view(request):
    return render(request, "userauths/login.html", {})

# def authView(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST or None)
#         if form.is_valid():
#             form.save()
#             return redirect("userauths:login")
#     else:
#         form = UserCreationForm()
#     return render(request, "userauths/signup.html", {"form": form})

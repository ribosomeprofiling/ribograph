from django.shortcuts import render, get_object_or_404

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponseRedirect
from django.urls import reverse


###############################################################################


def login_view(request):
    form = AuthenticationForm()

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return render(
                request,
                "browser/login.html",
                {"error_message": "Wrong username or password!", "form": form},
            )
    else:
        return render(request, "browser/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("browser:index"))

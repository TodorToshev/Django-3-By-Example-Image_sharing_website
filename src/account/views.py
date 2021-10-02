from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from account.models import Profile
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.views import LoginView
# Create your views here.


# class AdminLogin(LoginView):
#     template_name = 'account/login.html'


def user_login(request):

    print("Request >>> ", request)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        print("POST ::: ", request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            '''The 'authenticate()' method takes the request object, 
            the username, and the password parameters and returns the User object if 
            the user has been successfully authenticated, or None otherwise. If the user 
            has not been authenticated, return an HttpResponse, displaying the 
            Invalid login message.'''
            user = authenticate(
                request, username=cd['username'], password=cd['password'])

            if user is not None:    #None if 'authenticate()' does not find a matching User obj in the DB.
                if user.is_active:    #If the user obj's account has not been disabled.
                    login(request, user)    #set the user in the session
                    return HttpResponse("Auth Successful.")
                else:
                    return HttpResponse("Disabled account.")
            else:
                return HttpResponse("Invalid login.")

            '''authenticate() checks user credentials and returns a User
            object if they are correct; login() sets the user in the current 
            session.'''
    else:
        form = LoginForm()
    return render(request, "account/login.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "account/dashboard.html", {"section": 'dashboard'})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            #create new user profile:
            Profile.objects.create(user=new_user)
            return render(request, "account/register_done.html", {"new_user": new_user})

        else:
            return render(request, "account/register.html", {"user_form": user_form})
    else:
        user_form = UserRegistrationForm()
        return render(request, "account/register.html", {"user_form": user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files = request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile has been updated.")
        else:
            messages.error(request, "Something went wrong.")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, "account/edit.html", {"user_form": user_form, "profile_form": profile_form})
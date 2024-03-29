from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from account.models import Profile
from actions.models import Action
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact
from actions.utils import create_action

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
    # display actions: 
    '''
    retrieve all actions from the database, excluding the ones 
    performed by the current user. By default, you retrieve the latest actions performed 
    by all users on the platform. If the user is following other users, you restrict the 
    query to retrieve only the actions performed by the users they follow. 
    '''
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]

    return render(request, "account/dashboard.html", {"section": 'dashboard', 'actions': actions})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            #create new user profile:
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
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


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, "account/user/list.html", {"section": "people", "users": users})
    

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, "account/user/detail.html", {"section": "people", "user": user})

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    print(request.POST)
    if user_id and action:
        print("id and action")
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_form=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})

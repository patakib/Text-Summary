from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # create a new user object but not saving yet
            new_user = user_form.save(commit=False)
            #set password
            new_user.set_password(
                user_form.cleaned_data['password'])
            #save user object
            new_user.save()
            return render(request, 'textsummary_app/register_done.html',{'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'textsummary_app/register.html',{'user_form':user_form})


def user_login(request):
    if request.method == 'POST': #check whether method is POST or GET
        form = LoginForm(request.POST)
        if form.is_valid(): #check whether form is valid (e.g. form is filled in where required)
            cd = form.cleaned_data #submitted data passed to the server as string, here Django converts data to the right type
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account') #if the user is not active
            else:
                return HttpResponse('Invalid login') #if the user is not authenticated
    else:
        form = LoginForm()
    return render(request, 'textsummary_app/login.html', {'form':form})

@login_required
# checks whether the current user is authenticated. If yes, it executes the view, if not, redirects to the login URL
def dashboard(request):
    return render(request, 'textsummary_app/dashboard.html',{'section': 'dashboard'})

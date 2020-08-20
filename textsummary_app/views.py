from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm

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

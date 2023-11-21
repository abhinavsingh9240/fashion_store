from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.views import View

from home.forms import NameChangeForm, EmailChangeForm


def settings_view(request):
    return render(request, "settings.html")


def change_name(request):
    form = NameChangeForm()
    message = ""
    success = False
    if request.method == "POST":
        form = NameChangeForm(request.POST, instance=request.user)
        if authenticate(username=request.user.username, password=request.POST.get('password')):
            if form.is_valid():
                form.save()
                success = True
                form = NameChangeForm()
        else:
            message = "Invalid Password"

    context = {
        'form': form,
        'message': message,
        'success': success,
    }
    return render(request, template_name='settings/change_name.html', context=context)


def change_email(request):
    form = EmailChangeForm()
    message = ""
    success = False
    if request.method == "POST":
        if authenticate(username=request.user.username, password=request.POST.get('password')):
            form = EmailChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                user_instance = form.save(commit=False)
                user_instance.username = user_instance.email
                user_instance.save()
                success = True
                form = EmailChangeForm()
        else:
            message = "Invalid Password"

    context = {
        'form': form,
        'message': message,
        'success': success,
    }
    return render(request, template_name='settings/change_email.html',context=context)


def change_password(request):
    message=''
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            message = "Your Password has successfully changed"
    else:
        form = PasswordChangeForm(request.user)
    return render(request, template_name='settings/change_password.html',context={'form':form,'message':message})


def delete_account(request):

    if request.method == "POST" and authenticate(request.user,request.POST.get('password')):
        request.user.delete()
        return redirect('home')
    return render(request, template_name='settings/delete_account.html')

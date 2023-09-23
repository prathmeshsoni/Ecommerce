from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as authlogout
from django.contrib.auth.backends import UserModel
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt


def passwardd(request):
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            data = password_form.cleaned_data['email']
            user_email = User.objects.filter(Q(email=data))
            user_obj = User.objects.filter(email=data).first()
            if user_email.exists():
                if not user_obj.is_superuser:
                    messages.success(request, "User Can't")
                    return redirect('/admin/password-reset/')
                for user in user_email:
                    subject = 'Password Resquest'
                    email_template_name = 'registration/password_reset_email.html'
                    parameters = {
                        'email': user.email,
                        'username': user.username,
                        'domain': 'musicalclub.pythonanywhere.com',
                        # 'site_name' : 'PostScribers',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
                    }
                    html_template = render_to_string(email_template_name, parameters)
                    try:
                        subject = 'Reset Sassword'

                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [user.email]

                        message = EmailMessage(subject, html_template, email_from, recipient_list)
                        message.content_subtype = 'html'
                        message.send()
                    except:
                        return redirect('/admin/password-reset/')
                    return render(request, 'admin/password_reset_done.html')
            else:
                messages.success(request, "Enter a valid email address.")
                return redirect('/admin/password-reset/')
    else:
        password_form = PasswordResetForm()
    context = {
        'password_form': password_form,
    }
    return render(request, 'admin/password_reset_form.html', context)


def some_view(request):
    # Check if session has expired
    if request.method == 'POST':

        login_time = request.session.get('login_time_admin')
        if login_time:
            login_time = datetime.fromtimestamp(login_time)
            if datetime.now() - login_time > timedelta(minutes=10):
                check = 1
            else:
                check = 0
        else:
            check = 1
        if (int(check) == 1):
            # a = {'status': True}
            a = {'status': False}
            return JsonResponse(a)
        else:
            a = {'status': False}
            return JsonResponse(a)
    else:
        return redirect('/admin/')


def dashboard(request):
    return render(request, 'admin/masterpage/index-1.html')


def dashboardd(request):
    return render(request, 'admin/masterpage/index-1.html')


def hello(request):
    del request.session['username']
    print("hello");


def geturl(request):
    if request.method == 'POST':
        urll = request.POST.get('urll')
        request.session['last_url'] = urll
        print("urll:::", urll)
        return JsonResponse({'status': True})
    else:
        return redirect('/admin/')


def logout(request):
    if 'employee' in request.session:
        del request.session['employee']
    if 'adminuser' in request.session:
        del request.session['adminuser']
    if 'login_time_admin' in request.session:
        del request.session['login_time_admin']
    del request.session['_auth_user_id']
    del request.session['_auth_user_backend']
    return redirect('/admin/accounts/login/')


def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        userobj = User.objects.filter(username=username).first()
        user_obj = User.objects.filter(email=username).first()

        if (user_obj or userobj) is None:
            messages.success(request, 'Username/Email not found.')
            return redirect(request.META.get('HTTP_REFERER'))

        if not (user_obj or userobj).is_superuser:
            messages.success(request, "User Can't login")
            return redirect(request.META.get('HTTP_REFERER'))

        if (user_obj or userobj).is_superuser:
            if not (user_obj or userobj).is_staff:
                try:
                    user = UserModel.objects.get(email=username)
                    user11 = authenticate(username=user, password=password)
                    if (user11) is None:
                        messages.success(request, 'Wrong Password.')
                        return redirect('/admin/accounts/login/')

                    login(request, user11)
                    print('no 1')
                    request.session['employee'] = user
                    if 'last_url' in request.session:
                        urls = request.session.get('last_url')
                        del request.session['last_url']
                        return redirect('/admin/order/tracker/')
                    else:
                        return redirect('/admin/order/tracker/')

                except:
                    usee = None;

                user1 = authenticate(username=username, password=password)

                if (user1 or usee) is None:
                    messages.success(request, 'Wrong Password.')
                    return redirect('/admin/accounts/login/')

                login(request, user1)
                print('no 2')
                request.session['employee'] = username
                if 'last_url' in request.session:
                    urls = request.session.get('last_url')
                    del request.session['last_url']
                    return redirect('/admin' + urls + '')
                else:
                    return redirect('/admin/')

            else:
                if userobj.is_staff == 2:
                    messages.success(request, "User Can't login")
                    return redirect(request.META.get('HTTP_REFERER'))
                else:
                    try:
                        user = UserModel.objects.get(email=username)
                        user11 = authenticate(username=user, password=password)
                        if (user11) is None:
                            messages.success(request, 'Wrong Password.')
                            return redirect('/admin/accounts/login/')
                        login(request, user11)
                        print('no 3')
                        request.session['adminuser'] = user
                        request.session['login_time_admin'] = datetime.now().timestamp()
                        if 'last_url' in request.session:
                            urls = request.session.get('last_url')
                            del request.session['last_url']
                            return redirect('/admin' + urls + '')
                        else:
                            return redirect('/admin/')

                    except:
                        usee = None;

                        user1 = authenticate(username=username, password=password)

                        if (user1 or usee) is None:
                            messages.success(request, 'Wrong Password.')
                            return redirect('/admin/accounts/login/')

                        login(request, user1)
                        request.session['adminuser'] = username
                        request.session['login_time_admin'] = datetime.now().timestamp()
                        if 'last_url' in request.session:
                            urls = request.session.get('last_url')
                            del request.session['last_url']
                            return redirect('/admin' + urls + '')
                        else:
                            return redirect('/admin/')
    # print("login", request.session['last_url'])
    return render(request, 'admin/login.html', {"checkcon": 1, "Title": "Admin "})

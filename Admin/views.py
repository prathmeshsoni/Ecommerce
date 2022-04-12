from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import UserModel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponse
from django.core.mail import send_mail , BadHeaderError

def passwardd(request):
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            data = password_form.cleaned_data['email']
            user_email = User.objects.filter(Q(email=data))
            user_obj = User.objects.filter(email = data).first()
            if user_email.exists():
                if not user_obj.is_superuser:
                    messages.success(request, "User Can't")
                    return redirect('/admin/password-reset/')
                for user in user_email:
                    subject = 'Password Resquest'
                    email_template_name = 'registration/password_reset_email.html'
                    parameters = {
                        'email' : user.email,
                        'domain' : '127.0.0.1:8000',
                        # 'site_name' : 'PostScribers',
                        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                        'token' : default_token_generator.make_token(user) ,
                        'protocol' : 'http',
                    }
                    email = render_to_string(email_template_name, parameters)
                    try:
                        send_mail(subject, email, '', [user.email], fail_silently=False)
                    except:
                        return HttpResponse('invalid Header')
                    return redirect('/admin/password-reset/done/')
            else:
                messages.success(request, "Enter a valid email address.")
                return redirect('/admin/password-reset/')
    else:
        password_form = PasswordResetForm()
    context = {
        'password_form' : password_form,
    }
    return render(request, 'admin/password_reset_form.html', context)


@login_required(login_url='/admin/accounts/login/')
def dashboard(request):
    return render(request,'admin/masterpage/index.html')

def hello(request):
    del request.session['username']
    print("hello");


def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        userobj = User.objects.filter(username = username).first()
        user_obj = User.objects.filter(email = username).first()

        if (user_obj or userobj) is None:
            messages.success(request, 'User not found.')
            return redirect('/admin/accounts/login')

        if not (user_obj or userobj).is_superuser:
            messages.success(request, "User Can't login")
            return redirect('/admin/accounts/login')
        try:
            user = UserModel.objects.get(email=username)
            usee = authenticate( username = user , password = password)
            login(request , usee)
            return redirect('/admin/')
            
        except:
            usee = None;
        
        user1 = authenticate( username = username , password = password)        
        
        if (user1 or usee ) is None:
            messages.success(request, 'Wrong password.')
            return redirect('/admin/accounts/login')
        
        login(request , user1)
        return redirect('/admin/')


    return render(request , 'admin/login.html')
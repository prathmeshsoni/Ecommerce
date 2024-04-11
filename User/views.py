import random
import uuid
from datetime import date, timedelta, datetime

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.backends import UserModel
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.category.models import categoryModel
from Admin.slider.models import GalleryModel
from .models import *
from .serializer import address_Serialize, prooSerialize


site_name = '127.0.0.1:8000'


# 404 Page Not Found
def page_not_found_view(request, exception):
    return render(request, 'user/404.html', status=404)


def tracker(request):
    return render(request, 'user/tracking.html')


# Change User Password
def change_password(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            current = request.POST.get('old_password')
            new_pas = request.POST.get('new_password1')

            user2 = request.session.get('userid')
            user = A_User.objects.get(id=user2)
            check = user.check_password(current)
            if check:
                user.set_password(new_pas)
                user.save()
                a = {'status': True}
                return JsonResponse(a)
            else:
                a = {'status': False}
                return JsonResponse(a)
        else:
            try:
                user2 = request.session.get('userid')
                count = cart_count(user2)
                user_obj2 = A_User.objects.get(id=user2)
                alldata = add_to_cart.objects.filter(user=user_obj2)
                total_price = cartdetail(alldata, user2)
            except:
                count = 0
                alldata = 0
                total_price = 0
            return render(request, "user/change-password.html",
                          {'change_active': 'password_master', 'cartt': alldata, 'total_price': total_price,
                           'cart_val': count})
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# Login Page for User
def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        userobj = A_User.objects.filter(username=username).first()
        user_obj = A_User.objects.filter(email=username).first()

        if (user_obj or userobj) is None:
            a = {'status': True, 'exists': 'notexistuser'}
            return JsonResponse(a)

        profile_obj = Profile.objects.filter(user=user_obj).first()
        profileobj = Profile.objects.filter(user=userobj).first()

        if (profile_obj or profileobj) is None:
            a = {'status': True, 'admin': 'admincant'}
            return JsonResponse(a)

        if not (profile_obj or profileobj).is_verified:
            a = {'status': True, 'verify': 'notverify'}
            return JsonResponse(a)
        try:
            user = UserModel.objects.get(email=username)
            usee = authenticate(username=user, password=password)

            if (usee) is None:
                a = {'status': True, 'wrong': 'wrongpassword'}
                return JsonResponse(a)

            request.session['userid'] = usee.id
            request.session['username'] = usee.username

            if 'redirectlurll' in request.session:
                ss = request.session.get('redirectlurll')
                del request.session['redirectlurll']
                a = {'status': True, 'success': 'loginsuccess', 'redirect': 'particularpage', 'pagelink': ss}
                return JsonResponse(a)
            else:
                a = {'status': True, 'success': 'loginsuccess', 'redirect': 'dashboard'}
                return JsonResponse(a)
        except:
            usee = None

        user1 = authenticate(username=username, password=password)

        if (user1 or usee) is None:
            a = {'status': True, 'wrong': 'wrongpassword'}
            return JsonResponse(a)

        request.session['userid'] = user1.id
        request.session['username'] = user1.username

        if 'redirectlurll' in request.session:
            ss = request.session.get('redirectlurll')
            del request.session['redirectlurll']
            a = {'status': True, 'success': 'loginsuccess', 'redirect': 'particularpage', 'pagelink': ss}
            return JsonResponse(a)
        else:
            a = {'status': True, 'success': 'loginsuccess', 'redirect': 'dashboard'}
            return JsonResponse(a)

    if 'username' in request.session:
        return redirect('/user/dashboard/')

    else:
        count = 0

        return render(request, 'user/login.html', {'cart_val': count})


# For User Logout
def logout(request):
    try:
        del request.session['userid']
    except:
        pass
    try:
        del request.session['username']
    except:
        pass

    return redirect('/user/accounts/login/')


# Registration Page for User
def register_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if A_User.objects.filter(username=username).first():
                a = {'status': True, 'exists': 'existuser'}
                return JsonResponse(a)

            if A_User.objects.filter(email=email).first():
                a = {'status': True, 'exists': 'existemail'}
                return JsonResponse(a)

            user_obj = A_User(username=username, email=email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
            profile_obj.save()
            try:
                send_mail_after_registration(email, username, auth_token)
            except:
                print('Mail Not Send')
            a = {'status': True, 'create': 'usercreate', 'u_name': username}
            return JsonResponse(a)

        except Exception as e:
            print(e)
            a = {'status': False}
            return JsonResponse(a)

    else:
        if 'userid' in request.session:
            return redirect('/user/dashboard/')
        else:
            count = 0
            return render(request, 'user/register.html', {'cart_val': count, 'cartc': '2'})


# Account Activation Mail Send
def send_mail_after_registration(email, username, token):
    email_template_name = 'user/verifymail.html'
    parameters = {
        'domain': f'{site_name}/user/verify',
        'token': f'{token}',
        'protocol': 'http',
        'username': f'{username}',

    }
    html_template = render_to_string(email_template_name, parameters)
    subject = 'Registration Complete'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    message = EmailMessage(subject, html_template, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()


# After Mail Send Page
def token_send(request):
    if 'userid' in request.session:
        return redirect('/user/dashboard')

    else:
        count = 0
        return render(request, 'user/token_send.html', {'cart_val': count, })


# check Email verification
def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                request.session['userid'] = profile_obj.user.id
                request.session['username'] = profile_obj.user.username

                return redirect('/user/dashboard/')
            profile_obj.is_verified = True
            profile_obj.save()

            request.session['userid'] = profile_obj.user.id
            request.session['username'] = profile_obj.user.username

            return redirect('/user/dashboard/')
    except:
        return redirect('/user/')


# for User Forgot Password
def forget_password(request):
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            data = password_form.cleaned_data['email']
            user_email = A_User.objects.filter(Q(email=data))
            user_obj = A_User.objects.filter(email=data).first()
            profile_obj = Profile.objects.filter(user=user_obj).first()
            if user_email.exists():
                if profile_obj is None:
                    messages.success(request, "Admin can't ")
                    return redirect('/user/password-reset/')
                for user in user_email:
                    subject = "Password Resquest"
                    email_template_name = 'registration/password_reset_email-1.html'
                    parameters = {
                        'email': user.email,
                        'username': user.username,
                        'domain': f'{site_name}',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    try:
                        message = render_to_string(email_template_name, parameters)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [user.email]
                        email = EmailMessage(subject, message, email_from, recipient_list)
                        email.content_subtype = "html"
                        email.send()
                    except:
                        return redirect('/user/password-reset/')

                    return render(request, 'user/password_reset_done.html')
            else:
                messages.success(request, "Enter a valid email address.")
                return redirect('/user/password-reset/')
    else:
        password_form = PasswordResetForm()
        try:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = A_User.objects.get(id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)
            total_price = cartdetail(alldata, user2)
        except:
            count = 0
            alldata = 0
            total_price = 0
        context = {
            'cartt': alldata,
            'total_price': total_price,
            'cart_val': count,
            'password_form': password_form,
        }
    return render(request, 'user/password_reset_form.html', context)


# Home Page
def home(request):
    get_banner = GalleryModel.objects.all()
    get_cat = categoryModel.objects.all()
    get_cat1 = productModel.objects.all()

    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
    except:
        count = 0
        alldata = 0
        total_price = 0

    alldata_ = {
        'cartt': alldata,
        'total_price': total_price,
        'cart_val': count,
        'obj': get_banner,
        'pro': get_cat,
        'pro1': get_cat1,
    }
    return render(request, 'user/home.html', alldata_)


@api_view(['GET', 'POST'])
def quickview(request):
    if request.method == 'GET':
        if 'userid' in request.session:
            return redirect('/user/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')
    else:
        id = request.POST.get('id')
        obj = productModel.objects.get(id=id)
        serializer = prooSerialize(obj)
        try:
            user2 = request.session.get('userid')
            user_obj2 = A_User.objects.get(id=user2)
            cdataa = add_to_cart.objects.get(user=user_obj2, product_id=id)
            cdata = cdataa.product_id.id
        except:
            cdata = 0

    a = {'cart_vall': cdata}
    return Response(serializer.data)


def quickviesw(request):
    if request.method == 'GET':
        if 'userid' in request.session:
            return redirect('/user/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')
    else:
        try:
            id = request.POST.get('id')
            user2 = request.session.get('userid')
            user_obj2 = A_User.objects.get(id=user2)
            cdataa = add_to_cart.objects.get(user=user_obj2, product_id=id)
            cdata = cdataa.product_id.id
        except:
            cdata = 0

    a = {'cdata': cdata}
    return JsonResponse(a)


# particular Category Display
def category(request, hid):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    try:
        pro_list = productModel.objects.filter(catname_id=hid)
        cat_obj = categoryModel.objects.get(id=hid)
    except:
        return redirect('/user/category/')
    shop_dict = {'cartt': alldata, 'total_price': total_price, 'cart_val': count, 'cat_obj': cat_obj,
                 'pro_list': pro_list, 'hid': hid}
    return render(request, 'user/category.html', shop_dict)


# All Category Display
def cat_page(request):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    cat_obj = categoryModel.objects.all()
    shop_dict = {'cartt': alldata, 'total_price': total_price, 'cart_val': count, 'cat_obj': cat_obj}
    return render(request, 'user/category-list.html', shop_dict)


# Particular Product Display
def product(request, pid):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
    except:
        count = 0
        alldata = 0
        total_price = 0

    try:
        cdataa = add_to_cart.objects.get(user=user_obj2, product_id=pid)
        cdata = cdataa.product_id.id
    except:
        cdata = 0
    try:
        pdata = productModel.objects.get(id=pid)
        cdataa = productModel.objects.filter(catname_id=pdata.catname_id.id)
        ss = pid
    except:
        return redirect('/user/product/')
    x = {'rating': '1''2''3''4''5', 'reletedskip': ss, 'cartt': alldata, 'total_price': total_price, 'pdata': pdata,
         'cart_val': count, 'cart_vall': cdata, 'releteddata': cdataa}
    return render(request, 'user/product.html', x)


# All Product Display
def pro_page(request):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    pro_obj = productModel.objects.all()
    pro_dict = {'cartt': alldata, 'total_price': total_price, 'cart_val': count, 'pro_list': pro_obj}
    return render(request, 'user/product-list.html', pro_dict)


# User Dashboard
def dashboard(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
        return render(request, 'user/dashboard.html',
                      {'email': user_obj2, 'cartt': alldata, 'total_price': total_price, 'cart_val': count,
                       'dashboard_active': 'dashboard_master', 'cartc': '2'})
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# Manage Shipping Address
def address(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        obj = stateModel.objects.all()
        address_obj = addressModel.objects.filter(user_id=user2)
        count = cart_count(user2)
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
        send_dat = {'cart_val': count, 'state_list': obj, 'cartt': alldata, 'total_price': total_price,
                    'address_obj': address_obj, 'address_active': 'address_master'}

        return render(request, 'user/address.html', send_dat)
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# Add And Update Address Url
def myaccount(request):
    if request.method == 'POST':
        user2 = request.session.get('userid')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        country = request.POST.get('country')
        locality = request.POST.get('locality')
        phone_number = request.POST.get('phone_number')
        contact = int(phone_number)
        state = request.POST.get('state')
        city = request.POST.get('city')
        street_address = request.POST.get('Street')
        pincode = request.POST.get('pincode')

        try:
            hid = request.POST.get('hid')
            address_obj = addressModel.objects.get(id=hid)
        except:
            address_obj = addressModel()

        user_id = A_User.objects.get(id=user2)

        address_obj.first_name = firstname
        address_obj.last_name = lastname
        address_obj.locality = locality
        address_obj.user_id = user_id
        address_obj.country = country
        address_obj.phone_number = contact
        state_obj = stateModel.objects.get(id=state)
        address_obj.state = state_obj
        address_obj.city = city
        address_obj.street_address = street_address
        address_obj.pincode = pincode
        address_obj.save()

        messages.success(request, "Add Address Successfully ✔")
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        if 'userid' in request.session:
            return redirect('/user/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')


# Address Update Using Ajax
@api_view(['GET', 'POST'])
def updateaddress(request):
    if request.method == 'GET':
        if 'userid' in request.session:
            return redirect('/user/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')
    else:
        id = request.POST.get('id')
        obj = addressModel.objects.get(id=id)
        serializer = address_Serialize(obj)
        return Response(serializer.data)


# Address Delete Using Ajax
def remove_address(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            try:
                a_id = request.POST.get('id')
                obj = addressModel.objects.get(id=a_id)
                aa = buyModel.objects.filter(address_id=a_id)
                aa_count = aa.count()
                if (int(aa_count) == 0):
                    confirm_delete = request.POST.get('confirm_delete')
                    if (confirm_delete == '0'):
                        obj.delete()
                        a = {'status': True, 'exists': 'done'}
                        return JsonResponse(a)
                    a = {'status': True, 'exists': 'confirmdelete'}
                    return JsonResponse(a)
                else:
                    a = {'status': True, 'exists': 'orderexist'}
                    return JsonResponse(a)
            except:
                a = {'status': True, 'exists': 'error'}
                return JsonResponse(a)
        else:
            return redirect('/user/address/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


def myorderrr(request):
    if request.method == 'GET':
        if 'userid' in request.session:
            return redirect('/user/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')
    else:
        try:
            id = request.POST.get('id')
            pro_list = Sub_bayModel.objects.filter(order_id=id)
            a = {'status': True, 'pro_list': pro_list}
        except:
            a = {'status': False}
        return JsonResponse(a)


# All Order Display
def myorder(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            id = request.POST.get('id')
            order = buyModel.objects.get(id=id)
            order_cancel = 'cancel'
            order.order_status = order_cancel
            order.save()
            a = {'status': True}
            return JsonResponse(a)
        else:
            user2 = request.session.get('userid')
            user_obj2 = A_User.objects.get(id=user2)
            order = buyModel.objects.filter(user_id=user_obj2)
            check = order.count()
            count = cart_count(user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)
            total_price = cartdetail(alldata, user2)
            send_dat = {'cartt': alldata, 'total_price': total_price, 'cart_val': count,
                        'myorder_active': 'myorder_master', 'allorder': order, 'emptyorder': check, }
            return render(request, 'user/order.html', send_dat)
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# particular Order Display  #Order Success Page
def myorder1(request, hid, sid):
    if 'userid' in request.session:
        try:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = A_User.objects.get(id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)
            total_price = cartdetail(alldata, user2)
            pro_list = Sub_bayModel.objects.filter(order_id=hid, order_id__user_id=user_obj2)
            order = buyModel.objects.get(id=hid, user_id=user_obj2)
            cart_product = [p for p in buyModel.objects.filter(id=hid, user_id=user_obj2)]
            order_date = date.today() + timedelta(days=4)

            ttotal_amount = []
            shipping_charge = 70
            for p in cart_product:
                total_amountt = p.total_amount
                ttotal_amount.append(total_amountt)
            subtotal = ttotal_amount[0] - shipping_charge
            data = {'cartt': alldata, 'total_price': total_price, 'cart_val': count, 'hid': hid, 'sid': sid,
                    'order_list': pro_list, 'order': order, 'subtotal': subtotal, 'order_date': order_date}

            return render(request, 'user/order-success.html', data)
        except:
            return redirect('/user/myorder/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# Add To Cart Page
def gocart(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        user_obj2 = A_User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata, user2)
        soo = alldata.count()
        if alldata.exists():
            var = request.POST.get('var')
            if var == '3':
                id1 = request.POST.get('id')
                cartquntity = request.POST.get('cartquntity')
                obj = add_to_cart.objects.get(id=id1)
                ss = obj.product_id.id
                assa = productModel.objects.get(id=ss)
                sa = assa.total_quantity

                if (int(sa) >= int(cartquntity)):
                    obj.quantity = cartquntity
                    obj.save()
                    cart_productt = [p for p in add_to_cart.objects.all()
                                     if p.user.id == user2]
                    total_amount = []
                    if cart_productt:
                        for p in cart_productt:
                            tempamount = (p.quantity * p.product_id.pro_price)
                            total_amount.append(tempamount)
                        amount = 0
                        shipping = 70.00
                        for i in range(0, len(total_amount)):
                            amount = amount + total_amount[i]
                        amountd = amount + shipping
                        a = {'status': True, 'total_amount_update': amount, 'total_amount': total_amount,
                             'amountd': amountd}
                        return JsonResponse(a)
                else:
                    a = {'status': False}
                    return JsonResponse(a)

            cart_product = [p for p in add_to_cart.objects.all()
                            if p.user.id == user2]

            total_amount = []
            if cart_product:
                for p in cart_product:
                    tempamount = (p.quantity * p.product_id.pro_price)
                    total_amount.append(tempamount)
                summ = 0
                for i in range(0, len(total_amount)):
                    summ = summ + total_amount[i]
            send_data = {'cartt': alldata, 'total_price': total_price, 'totall_amount': summ, 'cart_val': soo,
                         'cartc': soo}
        else:
            return render(request, 'user/cart.html', {'emptycart': 'emtycart', 'cart_val': soo})
        return render(request, 'user/cart.html', send_data)
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# Add, Update and Delete Cart Item
@csrf_exempt
def addCart(request):
    if 'username' in request.session:
        var = request.POST.get('var')
        if var == '1':
            update_cart = request.POST.get('update_cart')
            user2 = request.session.get('userid')
            user_obj = A_User.objects.get(id=user2)
            quantity = request.POST.get('ccartquntity')
            product_id = request.POST.get('id')
            product = productModel.objects.get(id=product_id)
            compair = product.total_quantity

            if (update_cart == '0'):
                add_obj = add_to_cart()
                quantityy = int(quantity)
                another = int(compair)

            else:
                add_obj = add_to_cart.objects.get(product_id=update_cart, user=user_obj)
                add_objj = add_obj.quantity
                quantityy = int(add_objj) + int(quantity)
                another = int(compair) - int(add_objj)

            if (int(quantityy) <= int(compair)):

                add_obj.quantity = quantityy
                add_obj.product_id = product

                add_obj.user = user_obj
                add_obj.save()
                c_id = add_obj.product_id.id
                a = {'status': True, 'c_id': c_id}
                return JsonResponse(a)
            else:
                a = {'status': "error", 'another': another}
                return JsonResponse(a)

        if var == '2':
            id1 = request.POST.get('id')
            obj = add_to_cart.objects.get(id=id1)
            obj.delete()
            return JsonResponse({'status': True})

    if request.method == 'GET':
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

    else:
        session_redirect = request.POST.get('session_redirect')
        if (session_redirect == '0'):
            return JsonResponse({'status': False, 'redirect': '0'})
        else:
            redirectlurll = request.POST.get('redairecturl')
            request.session['redirectlurll'] = redirectlurll
            messages.success(request, 'First You Need to Login')
            return JsonResponse({'status': False, 'redirect': '1'})


# Product Rating
def review(request):
    if request.method == 'POST':
        productid = request.POST.get("product__id")
        ratingstar = request.POST.get("ratingstar")
        user = request.POST.get("userr_name")
        email = request.POST.get("user_email")
        title = request.POST.get("review_subject")
        description = request.POST.get("review_disc")

        review = RatingModel()

        get_proid = productModel.objects.get(id=productid)
        review.product_id = get_proid
        review.ratingstar = ratingstar
        review.username = user
        review.email = email
        review.title = title
        review.description = description
        review.save()
        a = {'status': True}
        return JsonResponse(a)
    else:
        return redirect('/user/')


def checkoutt(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            userq = request.session.get('userid')
            user_obj2w = A_User.objects.get(id=userq)
            alld = add_to_cart.objects.filter(user=user_obj2w)
            objproid = []
            objproquan = []
            for i in range(0, len(alld)):
                id_pro = alld[i].product_id.id
                quan_pro = alld[i].quantity
                objproid.append(id_pro)
                objproquan.append(quan_pro)

            pas = str(random.randint(9999999, 99999999))
            user_idd = request.session.get('userid')
            address_iid = request.POST.get('hidden_address')
            address_obj = addressModel.objects.get(id=address_iid)
            order_date = date.today()

            shipping_charge = request.POST.get('hidden_shipping')
            total_quantity = request.POST.get('hidden_total_quantity')
            total_amount = request.POST.get('hidden_total_ammount')
            payment_option = request.POST.get('payment_group')
            product_iid = request.POST.getlist('hidden_product_id')

            suma = 0
            for i in range(0, len(alld)):
                product_obj = productModel.objects.get(id=product_iid[i])
                suma = suma + product_obj.total_quantity

            if int(total_quantity) <= int(suma):
                if payment_option == 'COD':
                    buy_obj = buyModel()

                    user_obj2 = A_User.objects.get(id=user_idd)
                    buy_obj.user_id = user_obj2

                    buy_obj.order_idd = pas
                    buy_obj.payment_mode = payment_option
                    buy_obj.address_id = address_obj
                    buy_obj.order_date = order_date
                    buy_obj.shipping_charge = shipping_charge

                    buy_obj.total_quantity = total_quantity
                    buy_obj.total_amount = total_amount
                    buy_obj.save()

                    id11 = buy_obj.id
                    buy_obj2 = buyModel.objects.get(id=id11)

                    for i in range(int(len(alld))):
                        sub_obj = Sub_bayModel()
                        cart_obj = productModel.objects.get(id=objproid[i])

                        getpropricee = cart_obj.pro_price
                        propricee = int(getpropricee) * int(objproquan[i])

                        sub_obj.product_id = cart_obj
                        sub_obj.quantity = objproquan[i]
                        sub_obj.total = propricee
                        sub_obj.order_id = buy_obj2

                        sub_obj.save()

                    return redirect('/user/checkout/')

            else:
                return redirect('/user/gocart/')
        else:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = A_User.objects.get(id=user2)
            obj = stateModel.objects.all()
            address_obj = addressModel.objects.filter(user_id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)

            if alldata.exists():
                cart_product = [p for p in add_to_cart.objects.all()
                                if p.user.id == user2]
                total_amount = []
                main_total_quantity = []
                total_quantity = []
                if cart_product:
                    for p in cart_product:
                        temp_quantity = p.quantity
                        mainqunatity = p.product_id.total_quantity
                        total_quantity.append(temp_quantity)
                        main_total_quantity.append(mainqunatity)
                        tempamount = (p.quantity * p.product_id.pro_price)
                        total_amount.append(tempamount)

                    qun = []
                    for i in range(0, len(main_total_quantity)):
                        if int(main_total_quantity[i]) >= int(total_quantity[i]):
                            ss = 1
                            qun.append(ss)

                    if int(len(main_total_quantity)) == int(len(qun)):

                        summ = 0
                        total_quan = 0
                        for i in range(0, len(total_amount)):
                            summ = summ + total_amount[i]
                        for i in range(0, len(total_quantity)):
                            total_quan = total_quan + total_quantity[i]
                        shipping_charge = 70
                        total_price = summ + shipping_charge

                        send_data = {'click_on': '1', 'cart_val': count, 'cartt': alldata, 'total_price': total_price,
                                     'state_list': obj, 'address_obj': address_obj, 'total_quantity': total_quan,
                                     'subtotal': summ, 'var_11': 'varr'}
                        return render(request, 'user/checkout.html', send_data)
                    else:
                        return redirect('/user/gocart/')
            else:
                return redirect('/user/category/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


def checkouut(request):
    if 'userid' in request.session:
        if request.method == 'POST':

            user_idd = request.session.get('userid')
            random_order_id = str(random.randint(9999999, 99999999))
            payment_option = request.POST.get('payment_group')
            user_obj2 = A_User.objects.get(id=user_idd)
            objaddressid = []
            try:
                address_iid = request.POST.get('hidden_address')
                address_obj = addressModel.objects.get(id=address_iid, user_id=user_obj2)
                address_oobj = addressModel.objects.filter(id=address_iid)
            except:
                address_iid = objaddressid[0]
                address_oobj = addressModel.objects.filter(user_id=user_obj2)
                for i in range(0, len(address_oobj)):
                    id_address = address_oobj[i].id
                    objaddressid.append(id_address)
                address_obj = addressModel.objects.get(id=objaddressid[0])

            order_date = date.today()
            shipping_charge = 70
            emaill = A_User.objects.filter(id=user_idd)

            alld = add_to_cart.objects.filter(user=user_obj2)
            objcartid = []
            objproid = []
            objproquan = []
            objproqprice = []

            for i in range(0, len(alld)):
                id_cart = alld[i].id
                id_pro = alld[i].product_id.id
                quan_pro = alld[i].quantity
                objcartid.append(id_cart)
                objproid.append(id_pro)
                objproquan.append(quan_pro)

                getpropricee = alld[i].product_id.pro_price
                propricee = int(getpropricee) * int(objproquan[i])
                objproqprice.append(propricee)

            total_quantity = 0
            total_amount = 0
            for i in range(0, len(alld)):
                total_amount = total_amount + objproqprice[i]
                total_quantity = total_quantity + objproquan[i]
            total_amount = total_amount + 70

            testmodelamount = int(total_amount) * 100

            order_currency = 'INR'
            order_receipt = 'order_rcptid_11'

            suma = 0
            for i in range(0, len(alld)):
                product_obj = productModel.objects.get(id=objproid[i])
                suma = suma + product_obj.total_quantity

            if (int(total_quantity) <= int(suma)):
                if payment_option == 'COD':
                    buy_obj = buyModel()

                    buy_obj.user_id = user_obj2
                    buy_obj.order_idd = random_order_id
                    buy_obj.payment_mode = payment_option

                    buy_obj.address_id = address_obj

                    buy_obj.order_date = order_date
                    buy_obj.shipping_charge = shipping_charge

                    buy_obj.total_quantity = total_quantity
                    buy_obj.total_amount = total_amount
                    buy_obj.save()

                    id11 = buy_obj.id
                    buy_obj2 = buyModel.objects.get(id=id11)

                    for i in range(int(len(alld))):
                        sub_obj = Sub_bayModel()

                        product_obj = productModel.objects.get(id=objproid[i])
                        total_quantityt = product_obj.total_quantity
                        update_quantity = int(total_quantityt) - int(objproquan[i])
                        product_obj.total_quantity = update_quantity
                        product_obj.save()

                        productID = productModel.objects.get(id=objproid[i])
                        sub_obj.product_id = productID
                        sub_obj.quantity = objproquan[i]
                        sub_obj.total = objproqprice[i]
                        sub_obj.order_id = buy_obj2
                        sub_obj.save()

                        cart_obj = add_to_cart.objects.get(id=objcartid[i])
                        cart_obj.delete()
                    userr = str(id11)
                    return redirect('/user/order/' + userr + '/1')
                elif payment_option == 'RAZORPAY':
                    x = []
                    pro_dict = {'user_id': user_idd, 'address_id': address_iid, 'total': total_amount,
                                'quan': total_quantity, 'cart_id': objcartid, 'p_id': objproid, 'pro_quan': objproquan,
                                'pro_total': objproqprice, 'order_id_id': random_order_id}
                    x.append(pro_dict)
                    request.session['order_info'] = x

                    # Creating Order
                    client = get_client()
                    response = client.order.create(dict(
                        amount=testmodelamount, currency=order_currency, receipt=order_receipt, payment_capture='0'))

                    order_id = response['id']
                    order_status = response['status']

                    if order_status == 'created':
                        context = {'product_id': objproid, 'price': total_amount, 'order_id': order_id,
                                   'quantity': total_quantity, 'payment_mode': payment_option,
                                   'address_iid': address_oobj, 'emaill': emaill, 'check_var': 'True'}

                        return render(request, 'user/checkout.html', context)
            else:
                return redirect('/user/gocart/')
        else:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = A_User.objects.get(id=user2)
            obj = stateModel.objects.all()
            address_obj = addressModel.objects.filter(user_id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)

            if alldata.exists():
                cart_product = [p for p in add_to_cart.objects.all()
                                if p.user.id == user2]
                total_amount = []
                main_total_quantity = []
                total_quantity = []
                if cart_product:
                    for p in cart_product:
                        temp_quantity = p.quantity
                        mainqunatity = p.product_id.total_quantity
                        total_quantity.append(temp_quantity)
                        main_total_quantity.append(mainqunatity)
                        tempamount = (p.quantity * p.product_id.pro_price)
                        total_amount.append(tempamount)

                    qun = []
                    for i in range(0, len(main_total_quantity)):
                        if int(main_total_quantity[i]) >= int(total_quantity[i]):
                            ss = 1
                            qun.append(ss)

                    if int(len(main_total_quantity)) == int(len(qun)):

                        summ = 0
                        total_quan = 0
                        for i in range(0, len(total_amount)):
                            summ = summ + total_amount[i]
                        for i in range(0, len(total_quantity)):
                            total_quan = total_quan + total_quantity[i]
                        shipping_charge = 70
                        total_price = summ + shipping_charge

                        send_data = {'click_on': '1', 'cart_val': count, 'cartt': alldata, 'total_price': total_price,
                                     'state_list': obj, 'address_obj': address_obj, 'total_quantity': total_quan,
                                     'subtotal': summ, 'var_11': 'varr'}
                        return render(request, 'user/checkout.html', send_data)
                    else:
                        return redirect('/user/gocart/')
            else:
                return redirect('/user/category/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


# CheckOut Page
def checkout(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            try:
                pas = str(random.randint(9999999, 99999999))
                username = request.session.get('username')
                user_idd = request.session.get('userid')
                address_iid = request.POST.get('hidden_address')
                address_obj = addressModel.objects.get(id=address_iid)
                address_oobj = addressModel.objects.filter(id=address_iid)
                emaill = A_User.objects.filter(id=user_idd)
                payment_mode = request.POST.get('payment-group')
                order_date = date.today()
                shipping_charge = request.POST.get('hidden_shipping')
                total_quantity = request.POST.get('hidden_total_quantity')
                total_amount = request.POST.get('hidden_total_ammount')
                payment_option = request.POST.get('payment_group')
                testmodelamount = int(total_amount) * 100

                cart_iid = request.POST.getlist('cart_id')
                product_iid = request.POST.getlist('hidden_product_id')
                quantity = request.POST.getlist('hidden_quantity')
                total = request.POST.getlist('hidden_total')
                order_currency = 'INR'
                order_receipt = 'order_rcptid_11'

                suma = 0
                for i in range(0, len(quantity)):
                    product_obj = productModel.objects.get(id=product_iid[i])
                    suma = suma + product_obj.total_quantity
                if (int(total_quantity) <= int(suma)):
                    if payment_option == 'COD':
                        buy_obj = buyModel()

                        user_obj2 = A_User.objects.get(id=user_idd)
                        buy_obj.user_id = user_obj2

                        buy_obj.order_idd = pas
                        buy_obj.payment_mode = payment_option
                        buy_obj.address_id = address_obj
                        buy_obj.order_date = order_date
                        buy_obj.shipping_charge = shipping_charge

                        buy_obj.total_quantity = total_quantity
                        buy_obj.total_amount = total_amount
                        buy_obj.save()

                        id11 = buy_obj.id
                        buy_obj2 = buyModel.objects.get(id=id11)

                        for i in range(int(len(quantity))):
                            sub_obj = Sub_bayModel()

                            product_obj = productModel.objects.get(id=product_iid[i])
                            total_quantityt = product_obj.total_quantity
                            update_quantity = int(total_quantityt) - int(quantity[i])
                            product_obj.total_quantity = update_quantity
                            product_obj.save()
                            sub_obj.product_id = product_obj
                            sub_obj.quantity = quantity[i]
                            sub_obj.total = total[i]
                            sub_obj.order_id = buy_obj2
                            sub_obj.save()

                            cart_obj = add_to_cart.objects.get(id=cart_iid[i])
                            cart_obj.delete()
                        userr = str(id11)
                        return redirect('/user/order/' + userr + '/1')

                    elif payment_option == 'RAZORPAY':
                        x = []
                        pro_dict = {'user_id': user_idd, 'address_id': address_iid, 'p_id': product_iid,
                                    'total': total_amount, 'quan': total_quantity, 'pro_quan': quantity,
                                    'cart_id': cart_iid, 'pro_total': total, 'order_id_id': pas}
                        x.append(pro_dict)
                        request.session['order_info'] = x

                        # Creating Order
                        client = get_client()
                        response = client.order.create(dict(
                            amount=testmodelamount, currency=order_currency, receipt=order_receipt,
                            payment_capture='0'))

                        order_id = response['id']
                        order_status = response['status']

                        if order_status == 'created':
                            context = {'product_id': product_iid, 'price': total_amount, 'order_id': order_id,
                                       'quantity': total_quantity, 'payment_mode': payment_mode,
                                       'address_id': address_obj, 'address_iid': address_oobj, 'emaill': emaill,
                                       'check_var': 'True'}

                            return render(request, 'user/checkout.html', context)
                else:
                    return redirect('/user/gocart/')
            except:
                return redirect('/user/dashboard/')
        else:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = A_User.objects.get(id=user2)
            obj = stateModel.objects.all()
            address_obj = addressModel.objects.filter(user_id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)

            if alldata.exists():
                cart_product = [p for p in add_to_cart.objects.all()
                                if p.user.id == user2]
                total_amount = []
                main_total_quantity = []
                total_quantity = []
                if cart_product:
                    for p in cart_product:
                        temp_quantity = p.quantity
                        mainqunatity = p.product_id.total_quantity
                        total_quantity.append(temp_quantity)
                        main_total_quantity.append(mainqunatity)
                        tempamount = (p.quantity * p.product_id.pro_price)
                        total_amount.append(tempamount)

                    qun = []
                    for i in range(0, len(main_total_quantity)):
                        if (int(main_total_quantity[i]) >= int(total_quantity[i])):
                            ss = 1
                            qun.append(ss)

                    if (int(len(main_total_quantity)) == int(len(qun))):

                        summ = 0
                        total_quan = 0
                        for i in range(0, len(total_amount)):
                            summ = summ + total_amount[i]
                        for i in range(0, len(total_quantity)):
                            total_quan = total_quan + total_quantity[i]
                        shipping_charge = 70
                        total_price = summ + shipping_charge

                        send_data = {'click_on': '1', 'cart_val': count, 'cartt': alldata, 'total_price': total_price,
                                     'state_list': obj, 'address_obj': address_obj, 'total_quantity': total_quan,
                                     'subtotal': summ, 'var_11': 'varr'}
                        return render(request, 'user/checkout.html', send_data)
                    else:
                        return redirect('/user/gocart/')
            else:
                return redirect('/user/category/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


def get_client():
    client = razorpay.Client(
        auth=(
            f"{settings.RAZORPAY_KEY_ID}",
            f"{settings.RAZORPAY_KEY_SECRET}"
        )
    )
    return client


# Paymant Using razorpay
def payment_status(request):
    if request.method == 'POST':
        response = request.POST

        params_dict = {
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        transaction_id = params_dict['razorpay_payment_id']
        i = request.session.get('order_info')[0]
        shipping_charge = 70
        today_date = date.today()
        payment_option = 'RAZORPAY'

        address_id = i['address_id']
        total = i['total']
        quantity = i['quan']

        order_id_idd = i['order_id_id']
        user_idd = i['user_id']
        pro_id = i['p_id']
        pro_quan = i['pro_quan']
        pro_total = i['pro_total']
        cart_id = i['cart_id']

        buy_obj = buyModel()

        address_obj = addressModel.objects.get(id=address_id)
        us_id = A_User.objects.get(id=user_idd)

        buy_obj.address_id = address_obj

        buy_obj.order_idd = order_id_idd
        buy_obj.payment_mode = payment_option
        buy_obj.order_date = today_date
        buy_obj.shipping_charge = shipping_charge
        buy_obj.transaction_id = transaction_id
        buy_obj.total_quantity = quantity
        buy_obj.total_amount = total
        buy_obj.user_id = us_id
        buy_obj.save()
        id11 = buy_obj.id

        for i in range(int(len(pro_id))):
            sub_obj = Sub_bayModel()

            product_obj = productModel.objects.get(id=pro_id[i])
            total_quantityt = product_obj.total_quantity
            update_quantity = int(total_quantityt) - int(pro_quan[i])
            product_obj.total_quantity = update_quantity
            product_obj.save()

            sub_obj.product_id = product_obj
            sub_obj.quantity = pro_quan[i]
            sub_obj.total = pro_total[i]

            buy_obj2 = buyModel.objects.get(id=id11)
            sub_obj.order_id = buy_obj2

            sub_obj.save()

            cart_obj = add_to_cart.objects.get(id=cart_id[i])
            cart_obj.delete()

        del request.session['order_info']

        userr = str(id11)
        return redirect('/user/order/' + userr + '/1')

    else:
        if 'userid' in request.session:
            return redirect('/user/checkout/')
        else:
            return redirect('/user/accounts/login/')


# Cart Item Count
def cart_count(user):
    user_obj2 = A_User.objects.get(id=user)
    alldata = add_to_cart.objects.filter(user=user_obj2)
    soo = alldata.count()
    return soo


# Product Subtotal And Total Amount
def cartdetail(alldata, user2):
    if alldata.exists():
        cart_product = [p for p in add_to_cart.objects.all()
                        if p.user.id == user2]

        total_amount = []
        total_quantity = []
        if cart_product:
            for p in cart_product:
                temp_quantity = p.quantity
                total_quantity.append(temp_quantity)
                tempamount = (p.quantity * p.product_id.pro_price)
                total_amount.append(tempamount)
            summ = 0
            total_quan = 0
            for i in range(0, len(total_amount)):
                summ = summ + total_amount[i]
            for i in range(0, len(total_quantity)):
                total_quan = total_quan + total_quantity[i]
        shipping_charge = 70
        total_price = summ + shipping_charge
        return total_price, summ


from .models import Profile
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail , BadHeaderError,EmailMessage
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import UserModel
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm , PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from Admin.slider.models import GalleryModel
from Admin.category.models import categoryModel
from Admin.subcategory.models import brandModel
from Admin.product.models import productModel
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date
import random

from .serializer import address_Serialize
from rest_framework.decorators import api_view
from rest_framework.response import Response


def page_not_found_view(request, exception):
    # return redirect('/user/')
    return render(request, 'user/404.html', status=404)

#Login Page for User
def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        userobj = User.objects.filter(username = username).first()
        user_obj = User.objects.filter(email = username).first()

        if (user_obj or userobj) is None:
            messages.success(request, 'User not found.')
            return redirect('/user/accounts/login')
            
        profile_obj = Profile.objects.filter(user = user_obj ).first()
        profileobj = Profile.objects.filter(user = userobj ).first()

        if (profile_obj or profileobj) is None:
            messages.success(request, "Admin can't login")
            return redirect('/user/accounts/login')

        if not (profile_obj or profileobj).is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('/user/accounts/login')
        try:
            user = UserModel.objects.get(email=username)
            usee = authenticate( username = user , password = password)
            # login(request , usee)
            request.session['userid'] = usee.id
            request.session['username'] = usee.username
            if 'redirectlurll' in request.session:
                ss = request.session.get('redirectlurll')
                del request.session['redirectlurll']
                return redirect(''+ss+'')
            else:
                return redirect('/user/dashboard/')
            # return redirect(request.META.get('HTTP_REFERER'))
            # return redirect('/user/')
            
        except:
            usee = None;
        
        user1 = authenticate( username = username , password = password)        
        
        if (user1 or usee ) is None:
            messages.success(request, 'Wrong password.')
            return redirect('/user/accounts/login')
        
        # login(request , user1)
        request.session['userid'] = user1.id
        request.session['username'] = user1.username
        if 'redirectlurll' in request.session:
            ss = request.session.get('redirectlurll')
            del request.session['redirectlurll']
            return redirect(''+ss+'')
        else:
            return redirect('/user/dashboard/')

    if 'username' in request.session:
        return redirect('/user/dashboard/')

    else:
        count = 0
        return render(request , 'user/login.html',{'cart_val':count})

#For User Logout
def logout(request):
    del request.session['userid']
    del request.session['username']
    return redirect('/user/accounts/login/')


#Registration Page for User 
def register_attempt(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is taken.')
                return redirect('/user/register')

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is taken.')
                return redirect('/user/register')
            
            user_obj = User(username = username , email = email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , auth_token = auth_token)
            profile_obj.save()
            send_mail_after_registration(email, username, auth_token)
            return redirect('/user/token')

        except Exception as e:
            print(e)
    else:
        if 'userid' in request.session:
            return redirect('/user/dashboard/')
        else:
            count = 0
            return render(request , 'user/register.html',{'cart_val':count})
    

#Account Activation Mail Send
def send_mail_after_registration(email,username , token):
    email_template_name = 'user/verifymail.html'
    parameters = {
        'domain' : 'monarksoni.com/user/verify',
        'token' : f'{token}',
        'protocol' : 'https',
        'username' : f'{username}',

    }
    html_template = render_to_string(email_template_name, parameters )
    subject = 'Registration Complete'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    message = EmailMessage(subject , html_template , email_from , recipient_list )
    message.content_subtype = 'html'
    message.send()


#After Mail Send Page
def token_send(request):
    if 'userid' in request.session:
        return redirect('/user/dashboard')
    else:
        count = 0
        return render(request , 'user/token_send.html',{'cart_val':count,})
        

#check Email verification
def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/user/accounts/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/user/accounts/login')
    except Exception as e:
        print(e)
        return redirect('/user/')


#for User Forgot Passward
def forget_passward(request):
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            data = password_form.cleaned_data['email']
            user_email = User.objects.filter(Q(email=data))
            user_obj = User.objects.filter(email = data).first()
            profile_obj = Profile.objects.filter(user = user_obj ).first()
            if user_email.exists():
                if profile_obj is None:
                    messages.success(request, "Admin can't ")
                    return redirect('/user/password-reset/')
                for user in user_email:
                    subject = 'Password Resquest'
                    email_template_name = 'user/password_message.tex'
                    parameters = {
                        'email' : user.email,
                        'domain' : 'monarksoni.com',
                        # 'site_name' : 'PostScribers',
                        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                        'token' : default_token_generator.make_token(user) ,
                        'protocol' : 'https',
                    }
                    email = render_to_string(email_template_name, parameters)
                    try:
                        send_mail(subject, email, '', [user.email], fail_silently=False)
                    except:
                        return HttpResponse('invalid Header')
                    return redirect('/user/password-reset/done/')
            else:
                messages.success(request, "Enter a valid email address.")
                return redirect('/user/password-reset/')
    else:
        password_form = PasswordResetForm()
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    context = {
        'cartt':alldata,
        'total_price':total_price,
        'cart_val':count,
        'password_form' : password_form,
    }
    return render(request, 'user/password_reset_form.html', context)


#Home Page
def home(request):
    a = int(1)
    b = int(2)
    c = int(3)
    d = int(4)
    e = int(5)
    f = int(6)
    get_cate1 = productModel.objects.filter(catname_id = a)
    get_cate2 = productModel.objects.filter(catname_id = b)
    get_cate3 = productModel.objects.filter(catname_id = c)
    get_cate4 = productModel.objects.filter(catname_id = d)
    get_cate5 = productModel.objects.filter(catname_id = e)
    get_cate6 = productModel.objects.filter(catname_id = f)
    get_banner = GalleryModel.objects.all()
    get_cat = categoryModel.objects.all()
    get_cat1 = productModel.objects.all()
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    # get_cat2 = productModel.objects.get(id = 2)
    # get_cat3 = productModel.objects.get(id = 4)
    get_product = productModel.objects.all()
    alldata = {'cartt':alldata,'total_price':total_price,'cart_val':count,'obj': get_banner,'pro':get_cat,'pro1':get_cat1,'cate1':get_cate1,'cate2':get_cate2,'cate3':get_cate3,'cate4':get_cate4,'cate5':get_cate5,'cate6':get_cate6}
    return render(request , 'user/home.html' , alldata)


#particular Category Display
def category(request, hid):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    try:
        pro_list = productModel.objects.filter(catname_id=hid)
        cat_obj = categoryModel.objects.get(id=hid)
    except:
        return redirect('/user/category/')
    shop_dict = {'cartt':alldata,'total_price':total_price,'cart_val':count,'cat_obj':cat_obj,'pro_list':pro_list,'hid': hid}
    return render(request,'user/category.html',shop_dict)


#All Category Display
def cat_page(request):  
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    cat_obj = categoryModel.objects.all()
    shop_dict = {'cartt':alldata,'total_price':total_price,'cart_val':count,'cat_obj':cat_obj}
    return render(request,'user/category-list.html',shop_dict)

#Edited
#Particular Product Display
def product(request, pid):
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0

    try:
        cdataa = add_to_cart.objects.get(user=user_obj2 ,product_id = pid)
        cdata = cdataa.product_id.id
    except:
        cdata = 0
    try:
        pdata = productModel.objects.get(id = pid)
        cdataa = productModel.objects.filter(catname_id = pdata.catname_id.id)
        ss = pid
    except:
        return redirect('/user/product/')
    x = {'rating':'1''2''3''4''5','reletedskip':ss,'cartt':alldata,'total_price':total_price,'pdata': pdata,'cart_val':count,'cart_vall':cdata,'releteddata':cdataa}
    return render(request, 'user/product.html', x)

#All Product Display
def pro_page(request):  
    try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    except:
        count = 0
        alldata = 0
        total_price = 0
    pro_obj = productModel.objects.all()
    pro_dict = {'cartt':alldata,'total_price':total_price,'cart_val':count,'pro_list':pro_obj}
    return render(request,'user/product-list.html',pro_dict)

#User Dashboard
def dashboard(request):
    if 'userid' in request.session:
        # try:
        user2 = request.session.get('userid')
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
    # except:
    #     count = 0
    #     alldata = 0
    #     total_price = 0
        return render(request, 'user/dashboard.html',{'email':user_obj2,'cartt':alldata,'total_price':total_price,'cart_val':count,'dashboard_active':'dashboard_master'})
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

#Manage Shipping Address
def address(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        obj = stateModel.objects.all()
        address_obj = addressModel.objects.filter(user_id=user2)
        count = cart_count(user2)
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
        send_dat = {'cart_val':count,'state_list': obj,'cartt':alldata,'total_price':total_price,'address_obj': address_obj,'address_active':'address_master'}

        return render(request, 'user/address.html' , send_dat )
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

#Add And Update Address Url 
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
            address_obj = addressModel.objects.get(id = hid)
        except:
            address_obj = addressModel()

        user_id = User.objects.get(id=user2)
        
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


        # if hid == '1':
        return redirect(request.META.get('HTTP_REFERER'))
        # elif hid == '2':
        #     return redirect(request.META.get('HTTP_REFERER'))
    
    else:
        if 'userid' in request.session:
            return redirect('/user/address/')
        else:
            messages.success(request, 'First You Need to Loginn')
            return redirect('/user/accounts/login/')

#Address Update Using Ajax
@api_view(['POST']) 
def updateaddress(request):
    id = request.POST.get('id')
    obj = addressModel.objects.get(id = id)
    serializer = address_Serialize(obj)
    return Response(serializer.data)

#Address Delete Using Ajax
def remove_address(request,hid):
    if 'userid' in request.session:
        try:
            obj = addressModel.objects.get(id = hid)
            aa = buyModel.objects.filter(address_id = hid)
            aa_count = aa.count()
            if(int(aa_count) == 0):
                obj.delete()
                messages.success(request,"Delete successfully ✔")
                return redirect('/user/address/')
            else:
                
                messages.warning(request,"Can't Delete ❌")
                return redirect('/user/address/') 
        except:
            messages.warning(request,"ss")
            return redirect('/user/address/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

#All Order Display
def myorder(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        user_obj2 = User.objects.get( id = user2)
        order = buyModel.objects.filter(user_id=user_obj2)
        check = order.count();
        count = cart_count(user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
        send_dat = {'cartt':alldata,'total_price':total_price,'cart_val':count,'myorder_active':'myorder_master','allorder':order,'emptyorder':check}
        return render(request, 'user/order.html', send_dat)
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

#particular Order Display  #Order Success Page
def myorder1(request,hid,sid):
    if 'userid' in request.session:
        try:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = User.objects.get(id=user2)
            alldata = add_to_cart.objects.filter(user=user_obj2)
            total_price = cartdetail(alldata,user2)
            pro_list = Sub_bayModel.objects.filter(order_id=hid)
            order = buyModel.objects.get(id=hid)
            cart_product = [p for p in buyModel.objects.filter(id=hid)]
    
            ttotal_amount = []
            shipping_charge = 70
            for p in cart_product:
                total_amountt = p.total_amount
                ttotal_amount.append(total_amountt)
            subtotal = ttotal_amount[0] - shipping_charge 
            data = {'cartt':alldata,'total_price':total_price,'cart_val':count,'hid': hid,'sid':sid,'order_list':pro_list,'order':order,'subtotal':subtotal}
            
            return render(request, 'user/order-success.html',data)
        except:
            return redirect('/user/myorder/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


#Add To Cart Page
def gocart(request):
    if 'userid' in request.session:
        user2 = request.session.get('userid')
        user_obj2 = User.objects.get(id=user2)
        alldata = add_to_cart.objects.filter(user=user_obj2)
        total_price = cartdetail(alldata,user2)
        soo = alldata.count();
        if alldata.exists():
            var = request.POST.get('var')
            if var == '3':
                id1 = request.POST.get('id')
                cartquntity = request.POST.get('cartquntity')
                obj = add_to_cart.objects.get(id = id1)
                ss = obj.product_id.id
                assa = productModel.objects.get(id = ss)
                sa = assa.total_quantity
                
                if(int(sa) >= int(cartquntity)):
                    obj.quantity = cartquntity
                    obj.save();
                    cart_productt = [p for p in add_to_cart.objects.all()
                                if p.user.id == user2]
                    total_amount = []
                    if cart_productt:
                        for p in cart_productt:
                            tempamount = (p.quantity * p.product_id.pro_price)
                            total_amount.append(tempamount);
                        amount = 0
                        shipping = 70.00
                        for i in range(0, len(total_amount)):
                            amount = amount + total_amount[i]
                        amountd = amount + shipping    
                        a = {'status':True,'total_amount_update':amount,'total_amount':total_amount,'amountd':amountd}
                        return JsonResponse(a)
                else:
                    a = {'status':False}
                    return JsonResponse(a)

            cart_product = [p for p in add_to_cart.objects.all()
                            if p.user.id == user2]
            
            total_amount = []
            if cart_product:
                for p in cart_product:
                    tempamount = (p.quantity * p.product_id.pro_price)
                    total_amount.append(tempamount);
                summ = 0
                for i in range(0, len(total_amount)):
                    summ = summ + total_amount[i]
            send_data = {'cartt':alldata,'total_price':total_price,'totall_amount':summ,'cart_val':soo}
        else:
            return render(request, 'user/cart.html',{'emptycart':'emtycart','cart_val':soo})
        return render(request, 'user/cart.html',send_data)
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

#Add, Update and Delete Cart Item
@csrf_exempt
def addCart(request):
    if 'username' in request.session:
        var = request.POST.get('var')
        if var == '1':
            update_cart = request.POST.get('update_cart')
            user2 = request.session.get('userid')
            user_obj = User.objects.get(id=user2)
            quantity = request.POST.get('ccartquntity')
            product_id = request.POST.get('id')
            cartprice = request.POST.get('cartprice')
            product = productModel.objects.get(id=product_id)
            compair = product.total_quantity

            if(update_cart=='0'):
                add_obj = add_to_cart()
                quantityy = int(quantity)
                another = int(compair)

            else:
                add_obj = add_to_cart.objects.get(product_id = update_cart ,                            user = user_obj)
                add_objj = add_obj.quantity
                quantityy = int(add_objj) + int(quantity)
                another =  int(compair)-  int(add_objj)

    
            if(int(quantityy) <= int(compair)):

                add_obj.price = cartprice
                add_obj.quantity = quantityy
                add_obj.product_id = product
                
                add_obj.user = user_obj
                add_obj.save()
                a = {'status': True}
                return JsonResponse(a)
            else:
                a = {'status': "error",'another':another}
                return JsonResponse(a)

        if var == '2':
            id1 = request.POST.get('id')
            obj = add_to_cart.objects.get(id = id1)
            obj.delete()
            # return redirect(request.META.get('HTTP_REFERER'))
            return JsonResponse({'status': True})

    if request.method == 'GET':
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')

    else:
        redirectlurll = request.POST.get('redairecturl')
        request.session['redirectlurll'] = redirectlurll
        messages.success(request, 'First You Need to Login')
        return JsonResponse({'status': False})

#CheckOut Page
def checkout(request):
    if 'userid' in request.session:
        if request.method == 'POST':
            pas = str(random.randint(9999999,99999999))      
            username = request.session.get('username')
            user_idd = request.session.get('userid')
            address_iid = request.POST.get('hidden_address')
            address_obj = addressModel.objects.get(id = address_iid)
            address_oobj = addressModel.objects.filter(id = address_iid)
            emaill = User.objects.filter(id = user_idd)
            payment_mode = request.POST.get('payment-group')
            order_date = date.today()
            shipping_charge =  request.POST.get('hidden_shipping')
            total_quantity =  request.POST.get('hidden_total_quantity')
            total_amount =  request.POST.get('hidden_total_ammount')
            payment_option = request.POST.get('payment_group')
            testmodelamount = int(total_amount)*100

            cart_iid =  request.POST.getlist('cart_id')
            product_iid =  request.POST.getlist('hidden_product_id')
            quantity =  request.POST.getlist('hidden_quantity')
            total =  request.POST.getlist('hidden_total')
            order_currency = 'INR'
            order_receipt = 'order_rcptid_11'

            suma = 0
            for i in range(0, len(quantity)):
                product_obj = productModel.objects.get(id = product_iid[i])
                suma = suma + product_obj.total_quantity
            print(suma);
            print(total_quantity);

            if(int(total_quantity) <= int(suma) ):
                if payment_option == 'COD':
                    buy_obj = buyModel()
    
                    user_obj2 = User.objects.get(id=user_idd)
                    buy_obj.user_id = user_obj2
    
                    buy_obj.order_idd  = pas
                    buy_obj.payment_mode = payment_option
                    buy_obj.address_id = address_obj
                    buy_obj.order_date = order_date
                    buy_obj.shipping_charge = shipping_charge
                        
                    buy_obj.total_quantity = total_quantity
                    buy_obj.total_amount = total_amount
                    buy_obj.save()
    
                    id11 = buy_obj.id
                    buy_obj2 = buyModel.objects.get(id = id11 )
    
    
                    for i in range(int(len(quantity))):
                        sub_obj = Sub_bayModel()
    
    
                        product_obj = productModel.objects.get(id = product_iid[i])
                        total_quantityt = product_obj.total_quantity
                        update_quantity = int(total_quantityt) - int(quantity[i])
                        product_obj.total_quantity = update_quantity
                        product_obj.save();
                        sub_obj.product_id = product_obj
                        sub_obj.quantity = quantity[i]
                        sub_obj.total = total[i]
                        sub_obj.order_id = buy_obj2
                        sub_obj.save()
                        
    
                        cart_obj = add_to_cart.objects.get(id = cart_iid[i])
                        cart_obj.delete()
                    userr = str(id11)
                    return redirect('/user/order/'+userr+'/1')
    
                elif payment_option == 'RAZORPAY':
                    x = []
                    pro_dict = { 'user_id':user_idd, 'address_id':address_iid,'p_id':product_iid,'total':total_amount,'quan':total_quantity,'pro_quan':quantity,'cart_id':cart_iid,'pro_total':total,'order_id_id':pas}
                    x.append(pro_dict)
                    request.session['order_info'] = x 
    
                    # Creating Order
                    response = client.order.create(dict(
                        amount=testmodelamount, currency=order_currency, receipt=order_receipt, payment_capture='0'))
    
                    order_id = response['id']
                    order_status = response['status']
                
                    if order_status == 'created':
                        context = {'product_id': product_iid, 'price': total_amount, 'order_id': order_id,
                                   'quantity': total_quantity, 'payment_mode': payment_mode, 'address_id': address_obj, 'address_iid': address_oobj,'emaill':emaill,'check_var':'True'}
            
                        return render(request, 'user/checkout.html', context)
            else:
                return redirect('/user/gocart/')

        else:
            user2 = request.session.get('userid')
            count = cart_count(user2)
            user_obj2 = User.objects.get(id=user2)
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
                        total_quantity.append(temp_quantity);
                        main_total_quantity.append(mainqunatity);
                        tempamount = (p.quantity * p.product_id.pro_price)
                        total_amount.append(tempamount);
                    

                    qun = []
                    for i in range(0, len(main_total_quantity)):
                        if(int(main_total_quantity[i]) >= int(total_quantity[i])):
                            ss = 1
                            qun.append(ss);

                    if(int(len(main_total_quantity)) == int(len(qun))):

                        summ = 0
                        total_quan = 0
                        for i in range(0, len(total_amount)):
                            summ = summ + total_amount[i]
                        for i in range(0, len(total_quantity)):
                            total_quan = total_quan + total_quantity[i]
                        shipping_charge = 70
                        total_price = summ + shipping_charge
                            
                        send_data = {'cart_val':count,'cartt': alldata,'total_price':total_price,'state_list': obj,'address_obj': address_obj,'total_quantity':total_quan,'subtotal':summ,'var_11':'varr'}
                        return render(request, 'user/checkout.html',send_data)
                    else:
                        return redirect('/user/gocart/');
            else:
                # messages.success(request, "Admin can't ")
                return redirect('/user/category/')
    else:
        messages.success(request, 'First You Need to Login')
        return redirect('/user/accounts/login/')


import razorpay
client = razorpay.Client(
    auth=("rzp_test_As5y7xyrTHsCyp", "FrSdit4d7RbYywjpchnaYqiL"))

#Paymant Using razorpay
def payment_status(request):
    if request.method == 'POST':
        response = request.POST

        params_dict = {
            'razorpay_payment_id' : response['razorpay_payment_id'],
            'razorpay_order_id' : response['razorpay_order_id'],
            'razorpay_signature' : response['razorpay_signature']
        }

        transaction_id = params_dict['razorpay_payment_id']
        try:    
            status = client.utility.verify_payment_signature(params_dict)
            get_data = request.session.get('order_info')
            shipping_charge = 70
            today_date = date.today()
            payment_option = 'RAZORPAY'
            for i in get_data:
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

            address_obj = addressModel.objects.get(id = address_id)
            us_id = User.objects.get(id = user_idd)

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

                
                product_obj = productModel.objects.get(id = pro_id[i])
                total_quantityt = product_obj.total_quantity
                update_quantity = int(total_quantityt) - int(pro_quan[i])
                product_obj.total_quantity = update_quantity
                product_obj.save();
                sub_obj.product_id = product_obj
                sub_obj.quantity = pro_quan[i]
                sub_obj.total = pro_total[i]
                buy_obj2 = buyModel.objects.get(id = id11 )
                sub_obj.order_id = buy_obj2
                sub_obj.save()
                cart_obj = add_to_cart.objects.get(id = cart_id[i])
                cart_obj.delete()

            del request.session['order_info'] 

            userr = str(id11)
            return redirect('/user/order/'+userr+'/1')
        except:
            return redirect('/user/')

    else:
        if 'userid' in request.session:
            return redirect('/user/checkout/')
        else:
            return redirect('/user/accounts/login/');


#Cart Item Count
def cart_count(user):
    user_obj2 = User.objects.get(id=user)
    alldata = add_to_cart.objects.filter(user=user_obj2)
    soo = alldata.count();
    return soo


#Product Subtotal And Total Amount
def cartdetail(alldata,user2):
    if alldata.exists():
        cart_product = [p for p in add_to_cart.objects.all()
                        if p.user.id == user2]
        
        total_amount = []
        total_quantity = []
        if cart_product:
            for p in cart_product:
                temp_quantity = p.quantity
                total_quantity.append(temp_quantity);
                tempamount = (p.quantity * p.product_id.pro_price)
                total_amount.append(tempamount);
            summ = 0
            total_quan = 0
            for i in range(0, len(total_amount)):
                summ = summ + total_amount[i]
            for i in range(0, len(total_quantity)):
                total_quan = total_quan + total_quantity[i]
        shipping_charge = 70
        total_price = summ + shipping_charge
        return total_price,summ

#Edited
#Product Rating
def pro_Rating(request):
    print("heelo");
    # if request.method == 'POST':
      
    #     user = request.POST.get('catname_id')
    #     brandname_id = request.POST.get('brandname_id')
    #     productname = request.POST.get('productname')
    #     pro_description = request.POST.get('pro_description')
    #     pro_code = request.POST.get('pro_code')
        
    #     try:
    #         hid = request.POST.get('hid')
    #         pro_obj = productModel.objects.get(id = hid)
    #     except:
    #         pro_obj = productModel()

    #     cat_id = categoryModel.objects.get(id = catname_id)
    #     pro_obj.catname_id = cat_id
    #     brand_id = brandModel.objects.get(id = brandname_id)
    #     pro_obj.brand = brand_id
    #     pro_obj.productname = productname
    #     pro_obj.pro_description = pro_description
    #     pro_obj.pro_code = pro_code
            
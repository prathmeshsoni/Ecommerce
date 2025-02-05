from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.views import admin_login_required
from Admin.category.models import categoryModel
from Admin.filter.models import colourModel
from Admin.product.models import productModel
from Admin.subcategory.models import brandModel
from User.models import add_to_cart, Sub_bayModel
from .serializer import proSerialize


@admin_login_required
def index(request):
    if request.method == 'POST':

        try:
            catname_id = request.POST.get('catname_id')
            brandname_id = request.POST.get('brandname_id')
            productname = request.POST.get('productname')
            pro_description = request.POST.get('pro_description')
            pro_code = request.POST.get('pro_code')

            try:
                hid = request.POST.get('hid')
                pro_obj = productModel.objects.get(id=hid)
            except:
                pro_obj = productModel()

            cat_id = categoryModel.objects.get(id=catname_id)
            pro_obj.catname_id = cat_id
            brand_id = brandModel.objects.get(id=brandname_id)
            pro_obj.brand = brand_id
            pro_obj.productname = productname
            pro_obj.pro_description = pro_description
            pro_obj.pro_code = pro_code

            try:
                gb = 1
                pro_obj.save()
            except:
                gb = 0

            id = pro_obj.id
        except:
            gb = 0

        a = {'status': False}
        if gb == 1:
            a = {'status': True, 'id': id}

        return JsonResponse(a)

    else:
        pro_data = productModel.objects.all()
        cat_obj = categoryModel.objects.all()
        brand_obj = brandModel.objects.all()
        colour_obj = colourModel.objects.all()

        m = {'cat_master': 'master', 'product_active': 'product_master', 'cat_obj': cat_obj,
             'brand_obj': brand_obj, 'colour_obj': colour_obj, 'pro_data': pro_data}

        return render(request, "admin/product-1.html", m)


@admin_login_required
def getdata(request):
    if request.method == 'POST':
        hid = request.POST.get('hidden_id')
        try:
            pro_image = request.FILES['pro_image']
        except:
            pass
        try:
            pro_back_image = request.FILES['pro_back_image']
        except:
            pass
        try:
            feature_image = request.FILES['feature_image']
        except:
            pass

        pro_quntity = request.POST.get('pro_quntity')
        pro_price = request.POST.get('pro_price')
        strike_price = request.POST.get('strike_price')

        pro_colour = request.POST.get('pro_colour')
        return_product = request.POST.get('return_product')
        return_period_days = request.POST.get('return_period_days')

        pro_height = request.POST.get('pro_height')
        pro_width = request.POST.get('pro_width')
        pro_length = request.POST.get('pro_length')

        obj = productModel.objects.get(id=hid)

        obj.total_quantity = pro_quntity
        obj.pro_price = pro_price
        obj.strike_price = strike_price

        try:
            obj.pro_image = pro_image
        except:
            pass
        try:
            obj.pro_back_image = pro_back_image
        except:
            pass
        try:
            obj.feature_image = feature_image
        except:
            pass

        obj.pro_colour = pro_colour
        obj.return_product = return_product
        obj.return_period_days = return_period_days

        obj.pro_height = pro_height
        obj.pro_width = pro_width
        obj.pro_length = pro_length

        obj.save()

        return redirect('/admin/product/')


@admin_login_required
@api_view(['POST'])
def updatepro(request):
    id = request.POST.get('id')
    obj = productModel.objects.get(id=id)
    serializer = proSerialize(obj)
    return Response(serializer.data)


@admin_login_required
def remove_pro(request, hid):
    if request.user.is_authenticated:
        try:
            add_obj = add_to_cart.objects.get(product_id=hid)
            add_obj_chec = add_obj.id
            add_obj_check = str(add_obj_chec)

        except:
            add_obj_check = int(0)
        sub_obj = Sub_bayModel.objects.filter(product_id=hid)
        sub_count = sub_obj.count()
        obj = productModel.objects.get(id=hid)
        if add_obj_check == 0 and (int(sub_count) == 0):
            obj.delete()
            return redirect('/admin/product/')
        else:
            objs = obj.productname
            messages.success(request, "Can't Delete This (" + objs + ")")
            return redirect('/admin/product/')
    else:
        return redirect('/admin/')

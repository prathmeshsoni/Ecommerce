from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.views import admin_login_required
from Admin.category.serializer import catSerialize
from Admin.product.models import productModel
from .forms import categoryForm
from .models import categoryModel


@admin_login_required
def cat_page(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            jj = categoryModel.objects.get(id=id)
            d = categoryForm(request.POST or None, request.FILES or None, instance=jj)
        except:
            d = categoryForm(request.POST or None, request.FILES or None)
        if d.is_valid():
            d.save()
            return redirect('/admin/category/')
    else:
        d = categoryForm()
        b = categoryModel.objects.all()
        x = {'m': d, 'list': b, 'cat_master': 'master', 'cat_active': 'cat_master'}
        return render(request, "admin/category-1.html", x)


@admin_login_required
@api_view(['POST'])
def updateCat(request):
    id = request.POST.get('id')
    get_data = categoryModel.objects.get(id=id)
    serializer = catSerialize(get_data)
    return Response(serializer.data)


@admin_login_required
def remove_cat(request, hid):
    pro_obj = productModel.objects.filter(catname_id=hid)
    pro_count = pro_obj.count()
    obj = categoryModel.objects.get(id=hid)
    if int(pro_count) == 0:
        obj.delete()
        return redirect('/admin/category/')
    else:
        obj = obj.cat_name
        messages.success(request, "Can't Delete This (" + obj + ")")
        return redirect('/admin/category/')

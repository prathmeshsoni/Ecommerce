from django.shortcuts import render,redirect
from .forms import brandForm
from .models import brandModel
from Admin.product.models import productModel
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import brandSerializer
from django.contrib import messages

# Create your views here.
def brand_page(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            obj = brandModel.objects.get(id = id)
            b = brandForm(request.POST or None, instance = obj)
        except:
            b = brandForm(request.POST or None)
        if b.is_valid():
            b.save()
        return redirect('/admin/brand/')
    
    else:  
        n = brandForm()
        k = brandModel.objects.all()
        m = {'key':n,'key2':k,'cat_master':'master','subcat_active':'subcat_master'}
        return render(request,"admin/brand.html",m)

@api_view(['POST'])
def updatebrand(request):
    id = request.POST.get('id')
    obj = brandModel.objects.get(id = id)
    serializer = brandSerializer(obj)
    return Response(serializer.data)


def remove_brand(request,hid):
    brand_obj = productModel.objects.filter(brand = hid)
    brand_count = brand_obj.count()
    obj = brandModel.objects.get(id = hid)
    if(int(brand_count) == 0):
        obj.delete()
        return redirect('/admin/brand/')
    else:
        obj = obj.brand_name
        messages.success(request, "Can't Delete This ("+obj+")")
        return redirect('/admin/brand/')
    
    
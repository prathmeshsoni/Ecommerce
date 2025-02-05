from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.views import admin_login_required
from Admin.slider.forms import GalleryForm
from Admin.slider.models import GalleryModel
from Admin.slider.serializer import sliderSerialize


@admin_login_required
def slider(request):
    if request.method == "POST":
        try:
            id = request.POST.get('hid')
            jj = GalleryModel.objects.get(id=id)
            get_data = GalleryForm(request.POST or None, request.FILES or None, instance=jj)
        except:
            get_data = GalleryForm(request.POST or None, request.FILES or None)
        if get_data.is_valid():
            get_data.save()
            return redirect('/admin/slider/')
    else:
        form_obj = GalleryForm()
        show_data = GalleryModel.objects.all()
        g_dict = {'form_obj': form_obj, 'show_data': show_data, 'slider_master': 'slider master',
                  'slider_active': 'slider_master'}
        return render(request, 'admin/slider-1.html', g_dict)


@admin_login_required
@api_view(['POST'])
def updateSlider(request):
    id = request.POST.get('id')
    get_data = GalleryModel.objects.get(id=id)
    serializer = sliderSerialize(get_data)
    return Response(serializer.data)


@admin_login_required
def remove_slider(request, hid):
    obj = GalleryModel.objects.get(id=hid)
    obj.delete()
    return redirect('/admin/slider/')

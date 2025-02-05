from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.views import admin_login_required
from Admin.filter.forms import colourForm
from Admin.filter.models import colourModel
from .serializer import colourSerialize


@admin_login_required
def colour(request):
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            obj = colourModel.objects.get(id=id)
            data = colourForm(request.POST or None, request.FILES or None, instance=obj)
        except:
            data = colourForm(request.POST or None, request.FILES or None)
        if data.is_valid():
            data.save()
        return redirect('/admin/filter/colour/')
    else:
        colour_obj = colourForm()
        show_data = colourModel.objects.all()
        colour_dict = {'colour_obj': colour_obj, 'show_data': show_data, 'filter_master': 'filter master',
                       'colour_active': 'colour_master'}
        return render(request, 'admin/colour.html', colour_dict)


@admin_login_required
@api_view(['POST'])
def update_colour(request):
    id = request.POST.get('id')
    obj = colourModel.objects.get(id=id)
    serializer = colourSerialize(obj)
    return Response(serializer.data)


@admin_login_required
def remove_colour(request, hid):
    obj = colourModel.objects.get(id=hid)
    obj.delete()
    return redirect('/admin/filter/colour/')

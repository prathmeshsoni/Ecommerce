from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Admin.views import admin_login_required
from Admin.address_master.forms import stateForm
from Admin.address_master.models import stateModel
from Admin.address_master.serializer import stateSerialize
from User.models import addressModel


@admin_login_required
def state(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            jj = stateModel.objects.get(id=id)
            get_data = stateForm(request.POST or None, request.FILES or None, instance=jj)
        except:
            get_data = stateForm(request.POST or None, request.FILES or None)
        if get_data.is_valid():
            get_data.save()
            return redirect('/admin/address/state/')

    else:
        form_obj = stateForm()
        state_list = stateModel.objects.all()
        x = {'state_list': state_list, 'form_obj': form_obj, 'address_master': 'address master',
             'state_active': 'state_master'}
        return render(request, 'admin/state-1.html', x)


@admin_login_required
@api_view(['POST'])
def updateState(request):
    id = request.POST.get('id')
    get_data = stateModel.objects.get(id=id)
    serializer = stateSerialize(get_data)
    return Response(serializer.data)


@admin_login_required
def remove_state(request, hid):
    state_obj = addressModel.objects.filter(state=hid)
    state_count = state_obj.count()
    obj = stateModel.objects.get(id=hid)
    if int(state_count) == 0:
        obj.delete()
        return redirect('/admin/address/state/')
    else:
        obj = obj.state_name
        messages.success(request, "Can't Delete This (" + obj + ")")
        return redirect('/admin/address/state/')

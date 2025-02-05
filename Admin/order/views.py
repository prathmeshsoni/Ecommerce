from django.shortcuts import render

from Admin.views import admin_login_required
from User.models import buyModel, Sub_bayModel


@admin_login_required
def order(request):
    order_details = buyModel.objects.all()
    order_detailss = Sub_bayModel.objects.all()
    order_dict = {'order_master': 'order', 'order_active': 'order_master', 'order_details': order_details,
                  'order_detailss': order_detailss}
    return render(request, 'admin/order-1.html', order_dict)


@admin_login_required
def order_detail(request, hid):
    pro_list = Sub_bayModel.objects.filter(order_id=hid)
    order = buyModel.objects.get(id=hid)
    data = {'order_master': 'order', 'order_activee': 'order_masterr', 'order_list': pro_list, 'order': order}

    return render(request, 'admin/order_detail-1.html', data)

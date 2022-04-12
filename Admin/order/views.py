from django.shortcuts import render
from User.models import buyModel,Sub_bayModel


def order(request):
    order_details = buyModel.objects.all()
    order_detailss = Sub_bayModel.objects.all()
    order_dict = {'order_master':'order','order_active':'order_master','order_details':order_details,'order_detailss':order_detailss}
    return render(request,'admin/order.html',order_dict)

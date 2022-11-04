from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [

    path('',views.index,name="home"),
    path("showContest/" ,views.showContest , name = "show_contest" ),
    path("yourContest/<int:ids>/" ,views.yourContest , name = "your_contest" ),
    path("profile/" , views.profileSet,name = "profile"),
    path("select_contest/" ,views.select_con , name = "select_contest" ),
    path("ongoing_contest/" ,views.getjoinedContest , name = "ongoing_contest" ),
    path("All_Stocks/" ,views.stocklist , name = "All_Stocks" ),
    path("add_money" , views.trans_add , name = 'addmoney'),
    path("payment_success" , views.success , name = 'success'),
    path("withdraw_money" , views.trans_withdraw , name = 'withdraw'),
    path("your_transactions" , views.show_tranactions , name = 'transactions'),
    path("profile/<int:id>" , views.updateprofile , name = 'updateprofile'),
    path("edit/<int:id>" , views.editportfolio , name = 'editportfolio'),

]

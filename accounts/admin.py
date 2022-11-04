from django.contrib import admin
from .models import extendedUser,Contest_winner,UserProfile,StockProfile,ContestConfirm,ContestProfile,ContestJoinedByUser,checkall,transaction

# Register your models here.
@admin.register(ContestJoinedByUser)
class ContestMatchAdmin(admin.ModelAdmin):
    model = ContestJoinedByUser
    list_display = ('id','contest_type','contest_status','date_joined')

@admin.register(Contest_winner)
class Contest_winnerAdmin(admin.ModelAdmin):
    model = Contest_winner
    list_display = ('id','contest','winner')

@admin.register(StockProfile)
class StockAdmin(admin.ModelAdmin):
    model = StockProfile
    list_display = ('id','ticker','name','yesterday_closingPrice','Todayclosing_price')

@admin.register(extendedUser)
class extendedUserAdmin(admin.ModelAdmin):
    model = extendedUser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    # list_display = ('id','name')

@admin.register(ContestProfile)
class ContestProfileAdmin(admin.ModelAdmin):
    model = ContestProfile

    list_display = ('id','Name')

@admin.register(ContestConfirm)
class ContestConfirmAdmin(admin.ModelAdmin):
    model = ContestConfirm
    list_display = ('id','player','Ongoing_contest','date_joined','stockQuantity','stock_selected')

@admin.register(checkall)
class checkall(admin.ModelAdmin):
    model = checkall

@admin.register(transaction)
class transaction(admin.ModelAdmin):
    model = transaction
    list_display = ('id','name','Amount','transaction_type','paid')

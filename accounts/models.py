from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django import forms

from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(User): #depricated
    phone = models.IntegerField(null = True)
    is_phoneVerified = models.BooleanField(default=False)
    amount = models.IntegerField(default=30)
    Bonus = models.IntegerField(default = 70)
    contest_won = models.PositiveSmallIntegerField(default=0)
    conetest_joined = models.PositiveSmallIntegerField(default = 0)
    # def __str__(self):
    #     return'%s'%(self.name)

# upi_choice = (
#     ("bhim","Bhim"),("gpay", "Gpay")
#     )

class extendedUser(models.Model):
    usr = models.OneToOneField(User,on_delete = models.CASCADE )
    upi_gatewayOfPhone = models.CharField(max_length=50, null = True)
    phone = models.IntegerField(null = True, unique = True)
    is_phoneVerified = models.BooleanField(default=False)
    amount = models.IntegerField(default=30)
    Bonus = models.IntegerField(default = 70)
    contest_won = models.PositiveSmallIntegerField(default=0)
    conetest_joined = models.PositiveSmallIntegerField(default = 0)
    
    referal_id = models.CharField(max_length=10, null = True)
    refereal_used = models.CharField(max_length=10, null = True)
    total_referals = models.PositiveSmallIntegerField(default = 0)
    def __str__(self):
        return'%s'%str(self.usr.username)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        extendedUser.objects.create(usr=instance)



class StockProfile(models.Model):
    id = models.AutoField(primary_key=True)
    ticker = models.CharField(max_length=15,unique= True,null= False)
    name = models.CharField(max_length=50)
    yesterday_closingPrice = models.FloatField(default = 100)
    Todayclosing_price = models.FloatField(default =150)
    # is_updated = models.BooleanField(default=False)
    def __str__(self):
        return'%s'%(self.name)
class checkall(models.Model):
    id = models.AutoField(primary_key=True)
    is_contestStarted = models.BooleanField(default=False)
    is_StockPriceUpdated = models.BooleanField(default=False)
    Is_contestFinished = models.BooleanField(default=False)
    Is_winnerfound = models.BooleanField(default=False)
    Is_winnerset = models.BooleanField(default=False)
    is_allChecked = models.BooleanField(default=False)

   
#contest profile has information about all the contest and are predefined

class ContestProfile(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    NoOfPlayer = models.IntegerField()
    fees =  models.IntegerField()
    winnerPrize =  models.IntegerField()
    def __str__(self):
        return'%s'%str(self.id)

#ContestJoinedByUser has information about intance of contest created from contest profile 
# and the user that  wants to join it 

class ContestJoinedByUser (models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ManyToManyField(extendedUser,through= u'ContestConfirm' )
    contest_type = models.ForeignKey(ContestProfile , on_delete = models.CASCADE)
    # winner = models.ForeignKey(UserProfile, on_delete= models.CASCADE,null = True, related_name="winner")
    contest_status = models.CharField(max_length=20 , default="NotStarted")
    date_joined = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return'%s'%(self.id)

class Contest_winner(models.Model):
    id = models.AutoField(primary_key=True)
    contest = models.ForeignKey(ContestJoinedByUser , on_delete = models.CASCADE)
    winner = models.ForeignKey(extendedUser, on_delete= models.CASCADE,null = True, related_name="winner")


class ContestConfirm (models.Model):
    id = models.AutoField(primary_key=True)
    player  = models.ForeignKey(extendedUser, on_delete= models.CASCADE)
    Ongoing_contest  = models.ForeignKey(ContestJoinedByUser,on_delete= models.CASCADE)
    stockQuantity = models.IntegerField()
    stock_selected = models.ForeignKey(StockProfile , on_delete = models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

class transaction(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100,unique= True,null= False)
    name = models.ForeignKey(extendedUser, on_delete= models.CASCADE,null = False)
    Amount = models.FloatField(default = 0)
    paid = models.BooleanField(default =False)
    transaction_type = models.CharField(max_length = 15,null = False)
    date_joined = models.DateTimeField(auto_now_add=True, null = True)

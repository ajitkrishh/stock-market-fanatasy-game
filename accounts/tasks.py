from huey.contrib.djhuey import task,periodic_task
from huey import RedisHuey,SqliteHuey,crontab
from datetime import datetime,time
from .models import extendedUser,Contest_winner,UserProfile,StockProfile,ContestConfirm,ContestProfile,ContestJoinedByUser,checkall
import requests,json
import pandas as pd
from django.db import connection as cn, reset_queries as rs
from django.db.models import F

import time
huey = SqliteHuey('demo')



def set_winners(idlist,winnerlist): #updates db for winners :triggered from startfindingwiners function a last
	if checkall.objects.get(pk = 1).Is_winnerset == False:
		for matchid,winer in zip(idlist,winnerlist):
			# print(winer)
			# print(winer[0])
			price = int(winer[1]/len(winer[0]))
			for usrid in winer[0]:
														# ContestJoinedByUser.objects.filter(pk = matchid).update(winner=)
														#winer[0][0] is usrid and winer[1] is contest price
				Contest_winner.objects.create(
					contest = ContestJoinedByUser.objects.get(pk = matchid),
					winner = extendedUser.objects.get(user = usrid))
				extendedUser.objects.filter(user = usrid).update(contest_won = F("contest_won") + 1,amount = F("amount") + price)
			
			ContestJoinedByUser.objects.filter(pk = matchid).update(contest_status="finished")
			# print("updated for ",matchid)
	
	checkall.objects.filter(pk = 1).update(Is_winnerset = True , Is_contestFinished = True, is_allChecked = True)


def StartfindingWiners():
	print(datetime.now().hour)
	if datetime.now().hour >= 16 and checkall.objects.get(pk = 1).Is_winnerfound == False: 
	# if datetime.now().hour >= 0: 
		started_contest = ContestConfirm.objects.filter(Ongoing_contest__contest_status='started').values_list('player__usr',
																'Ongoing_contest','stock_selected__Todayclosing_price',
																'stockQuantity','Ongoing_contest__contest_type__winnerPrize')
		df = pd.DataFrame.from_records(started_contest,columns = ['player','Ongoing_contest',
													'stock_selected__Todayclosing_price',
													'stockQuantity','winningPrice'])
		id_list = df.Ongoing_contest.unique() #get id of all ongoing contest
		winner_list = []
		for id in id_list:

			datafrm = ''
			datafrm = df[(df.Ongoing_contest == id)]

			player_list = datafrm.player.unique()
			dictnw = {}
			for plr in player_list:
				y = ''                              # remove previous results from loop
				y = datafrm[(datafrm.player == plr)]            #check for same player
				total = 0    # initialize total price
				contestlst = []                       
				for index,row in y.iterrows():     #running loop through dataframe
					total += row['stock_selected__Todayclosing_price']*row['stockQuantity']
				dictnw.__setitem__(plr,total)
			maximum_profit  = max(dictnw.values())
			winner=[]
			# print("profit" , maximum_profit)
			# print("dictnw" , dictnw)
			for key in dictnw:
				print(key,dictnw.get(key))
				if dictnw.get(key) == maximum_profit:
					winner.append(key)
					# print(key)
			price = datafrm['winningPrice'].iloc[0]
			t=(winner,price)
			# here ""winner"" is list of all the user whose maximum are equal  
			winner_list.append(t)
		# print("winner",winner_list)

		checkall.objects.filter(pk = 1).update(Is_winnerfound = True)
		# print("winner_list")
		set_winners(id_list,winner_list)

	else:
		print("wrong timing")





def update_price():
	if  checkall.objects.get(pk = 1).is_StockPriceUpdated == False:


		stklst = StockProfile.objects.filter(pk__gte= 5)
		# for stock_price in stklst:

		# time.sleep(5)
		for stock in stklst:
			print(stock.id)
			urll = "https://query1.finance.yahoo.com/v8/finance/chart/"+stock.ticker+".bo"
			price_chart = json.loads(requests.get(urll).text)
			price = price_chart['chart']['result'][0]['meta']['regularMarketPrice']
			StockProfile.objects.filter(id = stock.id).update(yesterday_closingPrice = F('Todayclosing_price'),Todayclosing_price = 100)

			# StockProfile.objects.filter(id = stock.id).update(Todayclosing_price = price)

		checkall.objects.filter(pk = 1).update(is_StockPriceUpdated = True) 
		print(" is_StockPriceUpdated updated")
		StartfindingWiners()   #///////////////////
	else:
		StartfindingWiners()

# @task()
# def hello_task():
#     print ("hello via pero wold")

# @periodic_task(crontab(minute = '56',hour='22'))

def reset_checkall():
	checkall.objects.filter(pk =1).update(
		is_contestStarted = False , 
		is_StockPriceUpdated = False,
		Is_winnerfound = False,
		Is_winnerset = False,
		Is_contestFinished = False,
		is_allChecked = False )



@periodic_task(crontab(minute='2-7' , hour = '16',day_of_week = '1,2,3,4,5'),name = "close_contest" ,
						 retries=2, retry_delay=10)

# @periodic_task(crontab(minute='10-12' , hour = '1'),name = "close_contest" , retries=2, retry_delay=10)
@huey.lock_task('updatestocks-lock')
def maain():
	checks = checkall.objects.get(pk = 1)
	if datetime.now().hour >= 16 and checks.is_allChecked == False:
		if checks.is_StockPriceUpdated == False:
			update_price()
		else:
			StartfindingWiners()
		print("main called")
	else:
		print("else main failed")
	print("something is wrong")


@periodic_task(crontab(minute='1-5' , hour = '0'),name = "Reset_all")
def rst():
	if datetime.now().hour == 0:
		reset_checkall()

@periodic_task(crontab(minute='0-2' , hour = '9',),name = "start_contest",day_of_week = '1,2,3,4,5')
def contest_start():
	ContestJoinedByUser.objects.filter(contest_status = 'NotStarted').update(contest_status = 'Started')
	checkall.objects.filter(pk = 1).update(is_contestStarted = True)
	print("started")


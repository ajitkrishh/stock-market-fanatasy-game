from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import extendedUser,Contest_winner,UserProfile,StockProfile,ContestConfirm,ContestProfile,ContestJoinedByUser,transaction,checkall
import razorpay,random
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages as msg
from .forms import Sign_upform,Registerform,phoneUpdateform
# from .stklist import xx

from django.db.models import F
from django.db import connection as cn, reset_queries as rs

import datetime
import time
import pandas as pd
import math
# Create your views here.

from django.http import HttpResponse
from .tasks import StartfindingWiners

from .tasks import update_price
def index(request):
	return render(request,'accounts/index.html')
	
# def sign_up(request):
# 	print(1111111111)
# 	if request.method == "POST":
# 		rgistr = Registerform(request.POST , prefix = "register")
# 		extensn = extensionform(request.POST , prefix = "extension")
# 		if rgistr.is_valid() and extensn.is_valid():
# 			user = rgistr.save()
# 			# print(user,extensn)
# 			usrprof = extensn.save(commit = False)
# 			usrprof.user = user
# 			usrprof.save()
# 			login(request,user,backend="django.contrib.auth.backends.ModelBackend")
# 			msg.add_message(request,msg.SUCCESS,'TOUR ACCOUNT HAS BEEN SUCCESSFULL CREATED')
# 			return render(request,'accounts/index.html')
# 		else:
# 			msg.add_message(req,msg.WARNING,'SOMETHING WENT WRONG')
# 		return render(request,'account/signup.html')

# 	else:
# 		form = Registerform(prefix = "register")
# 		ef = extensionform(prefix = "extension")
# 		context = {"fm": form, "ef" : ef}
# 		return render(request,'account/signup.html',context)

# ////////////////////////////////////////////////////////////

#helper function to create a object of contest confirm for joining contst
def contest_entry(stockQ_list,stockid_List,latestContestId,usr_id,fees,edition_type):
	# print(stockQ_list,stockid_List,latestContestId,usr_id,fees)
	for stkid,StkQ in zip(stockid_List,stockQ_list):
		# print("ï am indi lop")
		add_plyr = ContestConfirm.objects.create(
			stockQuantity = StkQ,
			stock_selected = StockProfile.objects.get(pk = stkid),  
			Ongoing_contest = ContestJoinedByUser.objects.get(pk = latestContestId),
			player= extendedUser.objects.get(usr = usr_id),

		)
	if edition_type == "create":  #edition type can be  create(when joing a contest) 
								   # or update (if updating a joined contest)

		
		feesfrombonus = math.ceil(fees*0.2) #20% fees that will be deducted if bomus is available
		bonusAmt = extendedUser.objects.get(usr = usr_id).Bonus 	

		if bonusAmt >= feesfrombonus:
			remaining_fees = fees-feesfrombonus
			extendedUser.objects.filter(usr = usr_id).update(
						conetest_joined = F("conetest_joined") + 1 ,
						amount = F("amount") - remaining_fees,Bonus = F("Bonus") - feesfrombonus )
		elif bonusAmt < feesfrombonus and bonusAmt> 0:
			feesfrombonus= bonusAmt
			remaining_fees = fees-feesfrombonus
			extendedUser.objects.filter(usr = usr_id).update(
						conetest_joined = F("conetest_joined") + 1 ,
						amount = F("amount") - remaining_fees,Bonus = F("Bonus") - feesfrombonus )
		else:
			extendedUser.objects.filter(usr = usr_id).update(
							conetest_joined = F("conetest_joined") + 1 ,
							amount = f("amount") - fees )

# ***************************************************************************

@login_required #from here we can join contest : actual db entries for selected stocks
def join_con(req,cntst_id):
	# print(req.method+"  of join con")
	if req.method == 'POST':
		if req.POST.get('xxid'):
			StkIdStr = req.POST.get('xxid')
			StkIdList = list(StkIdStr.split(","))
			value_x = req.POST.get('contestType')
		else:
			msg.add_message(req,msg.WARNING,'Something Went Wrong')
			# print("we didnt got id list") 

		if req.POST.get('xxQ'):
			StkQStr = req.POST.get('xxQ')
			StkQList = list(StkQStr.split(","))
			print("we got quantity list")
			# print(StkQList)
			# print(req.user.id)


			# contestfees = ContestJoinedByUser.objects.get(pk = value_x).contest_type.fees
			contestfees = ContestProfile.objects.get(pk = value_x).fees

			print(contestfees)

			contestStart_jointime = datetime.time(8,59,59,0000)
			contestEnd_jointime = datetime.time(17,30,00,0000)
			day_for_contest = [0,1,2,3,4] #o for mon

			tym = datetime.datetime.now().time()
			# if len(StkIdList) > 2 and len(StkQList) > 2 :
			if (len(StkIdList) == len(StkQList)) and len(StkIdList) > 2 :

				if ContestJoinedByUser.objects.filter(contest_type = value_x).count() > 0:
					contestCheck = ContestJoinedByUser.objects.filter(contest_type = value_x).latest("id")
					
					joindppl = ContestConfirm.objects.filter(Ongoing_contest= contestCheck).values_list('player' , flat=True).distinct().count()
					reqNoppl = ContestProfile.objects.get(pk = value_x).NoOfPlayer
					
					if joindppl < reqNoppl :
						if ContestConfirm.objects.filter(player__usr = req.user.id ,
													 Ongoing_contest = contestCheck.id ).count() > 0:
							msg.add_message(req,msg.SUCCESS,'ÿou re already joined')
							# print("ÿou have already joined the contest ")
						elif tym > contestStart_jointime and tym < contestEnd_jointime or checkall.objects.get(pk = 1).is_contestStarted == True:
							msg.add_message(req,msg.SUCCESS,'You cannot join between 9 am to 5:30 pm')
							# print("tried to join match in between")
						   
							# print("ÿou have late joined the contest ")
						elif datetime.datetime.today().weekday() not in day_for_contest:
							msg.add_message(req,msg.SUCCESS,'You cannot join at saturay or sunday')
						else:
							usrid = req.user.id
							contestId = contestCheck.id
							edition_type = "create"
							
							contest_entry(StkQList,StkIdList,contestId,usrid, contestfees,edition_type)
							
						#         )
					# # /////////////// dont touch works perfectly //////////////////

					else : # if selected contest is alrdy filled
						new_contest = ContestJoinedByUser.objects.create(contest_type= ContestProfile.objects.get(pk = value_x))# value_x defines contesttype or contest ids from contest profile type )
						contestCheck = new_contest.id
						edition_type = "create"  # below creating a new contest of selected ypes
						contest_entry(StkQList,StkIdList,contestCheck,req.user.id,contestfees,edition_type)
						

				else : # if thta type of contest is never created then creating new contest
					new_contest = ContestJoinedByUser.objects.create(contest_type= ContestProfile.objects.get(pk = value_x))# value_x defines contesttype or contest ids from contest profile type )
					contestCheck = new_contest.id
					edition_type = "create"
					contest_entry(StkQList,StkIdList,contestCheck,req.user.id, contestfees,edition_type)
					print(StkQList,StkIdList,contestCheck,req.user.id,contestfees)
					print("ÿou created new  contest due to absence of contest ")

			else:
				msg.add_message(req,msg.WARNING,'select at least 3 stock')

		else:
			msg.add_message(req,msg.WARNING,'Something went wrong try again !!')

	   
		# else:
		#         print("already full")
		print("here i am going to select_con")
		req.method= 'GET'
		return select_con(req)
	else:

		value_x = cntst_id
		stklist = StockProfile.objects.all()
		cxt = {'cntstype': value_x , 'form' : stklist}
		return render(req,'enroll/contest_joining.html' , cxt) 
		




@login_required# from here we can see list of availabe contest
def select_con(req):
	if req.method == 'POST':
		# print(req.user.id)
		value_x = req.POST.get('contestname')
		print(value_x)
		if value_x == None:
			req.method = 'POST'
			# print("from making it")
		else:
			if value_x != None and extendedUser.objects.get(usr__id = req.user.id).amount < ContestProfile.objects.get(pk = value_x).fees:
				# print("insuuficient")
				msg.add_message(req,msg.WARNING,'INSUFFICIENT BALANCE !!')
				stklist = StockProfile.objects.all()
				contestlist = ContestProfile.objects.all()
				cxt = {'contestlist' : contestlist,'stocklist':stklist}
				return render(req,'enroll/contest_selection.html', cxt)

			req.method = 'GET'

		print(req.method,value_x,"req,value_x from select con")
		return join_con(req , value_x)
		
	else: 
		if checkall.objects.get(pk = 1).is_contestStarted == True:
			msg.add_message(req,msg.WARNING,'NOW YOU CANNOT JOIN MATCH !!')

		stklist = StockProfile.objects.all()
		
		contestlist = ContestProfile.objects.all()

		# //////////////// code for joined but not started contest ////////////////
		# mm = []
		notStartedcnst = ContestConfirm.objects.filter(player__usr = req.user.id,Ongoing_contest__contest_status = "NotStarted").values_list('player__usr__username','Ongoing_contest',
									'Ongoing_contest__contest_type__Name','stock_selected__name',
									'stock_selected__yesterday_closingPrice',
									'stockQuantity')
		# for x in notStartedcnst:
			# mm.append()
		df = pd.DataFrame.from_records(notStartedcnst,
									columns = ['player_username','Ongoing_contest',
									'Ongoing_contest_Name','stock_selected_name',
									'stock_selected_yesterday_closingPrice',
									'stockQuantity'])
		# uniqueMatches = df.
		contest_ids = df.Ongoing_contest.unique()
		contest_name = df.Ongoing_contest_Name.unique()
		cnstNameNid = df[df.Ongoing_contest_Name.isin(contest_name)]
		cnstNameNid = cnstNameNid[['Ongoing_contest','Ongoing_contest_Name']].drop_duplicates(['Ongoing_contest'])
		# CREATING A DICT FOR CONTEST ID AND THEIR NAME
		# print(cnstNameNid)
		cnstvals = cnstNameNid.values.tolist()
		if len(cnstNameNid) > 0:
			# print("if",len(cnstNameNid))

			finaldict = cnstNameNid.set_index('Ongoing_contest').T.to_dict('records')[0]
			Mainlst = []
			cnstdict = {}
			for constId in contest_ids:
				f = df[(df.Ongoing_contest == constId)]
				f = f[['stockQuantity','stock_selected_name','stock_selected_yesterday_closingPrice']]
				flist = f.values.astype(str).tolist()
				# cnstdict.__setitem__(finaldict[constId],flist)
				for cnstval in cnstvals:
					if constId in cnstval:
						# print (cnstval)
						cnstdict.__setitem__(tuple(cnstval),flist)
				# print(cnstdict)
			# print(len(cnstNameNid))

			cxt = {'contestlist' : contestlist,'joinedcontestlist':cnstdict}
		else:
			# print("else")
			cxt = {'contestlist' : contestlist}



		
		return render(req,'enroll/contest_selection.html', cxt)




@login_required #shows ongoing contest with contest status "started"
def getjoinedContest(req):
	started_contest = ContestConfirm.objects.filter(Ongoing_contest__contest_status='Started',player__usr = req.user.id).values_list('Ongoing_contest',flat=True).distinct()
	# print(started_contest)
	if len(started_contest) > 0:
		cnst = ContestConfirm.objects.filter(Ongoing_contest__in = started_contest).values_list('player__usr__username',
									'Ongoing_contest','Ongoing_contest__contest_type__Name',
									'stock_selected__name',
									'stock_selected__yesterday_closingPrice',
									'stockQuantity')
		# cnst id for getting everytthing from db in one go
		df = pd.DataFrame.from_records(cnst,
									columns = ['player__usr__username','Ongoing_contest',
									'Ongoing_contest__contest_type__Name','stock_selected__name',
									'stock_selected__yesterday_closingPrice',
									'stockQuantity'])
		# print(df,started_contest)
		# making a df from fetched queryset 
		contest_ids = df.Ongoing_contest.unique()
		contest_name = df.Ongoing_contest__contest_type__Name.unique()
		cnstNameNid = df[df.Ongoing_contest__contest_type__Name.isin(contest_name)]
		cnstNameNid = cnstNameNid[['Ongoing_contest','Ongoing_contest__contest_type__Name']].drop_duplicates(['Ongoing_contest'])
		if len(cnstNameNid) > 0:
			finaldict = cnstNameNid.set_index('Ongoing_contest').T.to_dict('records')[0]
		else:
			msg.add_message(req,msg.WARNING,"you didnt join any match today/ Match is not started yet ")
		# del
		# print(finaldict)
		# print(len(started_contest))
		if len(cnstNameNid) > 0:
			Mainlst = []
			for id in contest_ids:
				lst = []
				mdict = {}
				f = df[(df.Ongoing_contest == id)]
				player_ids = f.player__usr__username.unique()
				for pid in player_ids:
					dicnw = {}
					nf = f[(f.player__usr__username == pid)]
					nf = nf[['stockQuantity','stock_selected__name','stock_selected__yesterday_closingPrice']]
					nflist = nf.values.astype(str).tolist()
					dicnw.__setitem__(pid,nflist)
					lst.append(dicnw)
				mdict.__setitem__(str(finaldict[id]),lst)
				Mainlst.append(mdict)

			cxt = {"details": Mainlst}
			return render(req,'accounts/details.html',cxt)
		else:
			msg.add_message(req,msg.WARNING,"you didnt join any match today/Match is not started yet ")
			cxt = None
			return render(req,'accounts/details.html',cxt)

	else:
		msg.add_message(req,msg.WARNING,"you didnt join any match today/Match is not started yet ")
		cxt = None
		return render(req,'accounts/details.html',cxt)
   
# def frnt(req):
# 		return render(req,'enroll/A3.html')
		
@login_required   #shows all finished  contest  by user till date 
def showContest(req):
	print(req.user.id)
	if ContestConfirm.objects.filter(player__usr = req.user.id).count() > 0:
  
		matchesId = ContestConfirm.objects.filter(player__usr = req.user.id,Ongoing_contest__contest_status = "finished").values_list('Ongoing_contest' , flat=True).distinct()
		if len(matchesId) >0 :
			mathnm = ContestJoinedByUser.objects.all()
			matchdetail = {}
			for m in matchesId:
				# matchesname =  ContestJoinedByUser.objects.get(id = m).contest_type.Name
				matchesname = mathnm.get(id = m).contest_type.Name
				matchdetail.__setitem__(m,matchesname)
			cxt = {"contest" :  matchdetail}
			print(cxt)
			return render(req,'enroll/show_cntst.html', cxt)
			# x = ContestProfile.objects.get(pk = value_x).id
		else:
			msg.add_message(req,msg.WARNING,'YOU HAVE NEVER JOINED ANY CONTEST ')
			print("you didnt join any contest")
			return render(req,'enroll/show_cntst.html')
	else:
		msg.add_message(req,msg.WARNING,'YOU HAVE NEVER JOINED ANY CONTEST ')
		print("you didnt join any contest")
		return render(req,'enroll/show_cntst.html')

		# /////////////////////////////////////////////////////////////////////////////////////

@login_required #shows details of finished contest with player and stocks details
def yourContest(req,ids):
	if ContestConfirm.objects.filter(Ongoing_contest = ids , player__usr=req.user.id,Ongoing_contest__contest_status = "finished").exists():
		contest = ContestConfirm.objects.filter(Ongoing_contest = ids,Ongoing_contest__contest_status = "finished").select_related("stock_selected")
		matchdetail = []
		winnerlist = []
		for mm in contest:
			matchdetail.append({'id':mm.id,'player':mm.player.usr.first_name,'stockselected':mm.stock_selected.name,'stockquantity':mm.stockQuantity,"MStockprice" : mm.stock_selected.yesterday_closingPrice,"UStockprice": mm.stock_selected.Todayclosing_price})
		
		winner_user = Contest_winner.objects.filter(contest = ids)
		for winners in winner_user:
			winnerlist.append(winners.winner.username)
		print(winnerlist)
		cxt = {"contest" :  matchdetail,'winners':winnerlist}
		# print(cxt)
		return render(req,'enroll/your_cntst.html',cxt)# x = ContestProfile.objects.get(pk = value_x).id
	else:
		print("invalid")
		return render(req,'enroll/show_cntst.html')# x = ContestProfile.objects.get(pk = value_x).id
# ///////////////////////////////////////////////////////////
@login_required
def profileSet(req):#shows profile of user


	usrextension = extendedUser.objects.filter(usr = req.user.id)
	# if extendedUser.objects.filter(usr = req.user.id).count() > 0:
	# 	# print(req.user.id, "if 1")
	# 	usrextension = extendedUser.objects.filter(usr = req.user.id)
	cxt = {"contest" :  usrextension}
	return render(req,'accounts/profile.html',cxt)# x = ContestProfile.objects.get(pk = value_x).id


@login_required #shows list of all stocks 
def stocklist(req):
	stklst = []
	stk = StockProfile.objects.all()
	for item in stk:
		stklst.append({'id':item.id,'name' : item.name,"ticker":item.ticker ,'pclose':item.yesterday_closingPrice})
		# print(item.id)
	return render(req,'enroll/stockslist.html' ,{'stklst':stklst})


	
	
# //////////////////////////////transactions below///////////////////////////////// 

@login_required
def trans_add(req): #adding money in account
	if req.method == 'POST':
		name = req.POST.get("name")
		val = int(req.POST.get("value"))*100 # rzorpay requires 100 time of real value// it works wth paisa rather than rupees
		client = razorpay.Client(auth = ("auth id ",'auth key'))
		payment = client.order.create({'amount':val,'currency':'INR','payment_capture': '1'})
		print(payment)
		transaction.objects.create(
			order_id = payment['id'],
			name = extendedUser.objects.get(usr = req.user.id),
			Amount = val,
			transaction_type="AddMoney"
		)
		payment.__setitem__(name,req.user.username)
			  
		print(name,val,payment)
		return render(req, "transaction/proceed.html",{'payment':payment})
	cxt = {"add" : "add"}
	return render(req, "transaction/transaction_add.html", cxt)

@csrf_exempt
def success(req): #sttus after ransaction
	if req.user.is_authenticated:
		if req.method == 'POST':
			print(req.POST)
			trans_query = transaction.objects.filter(order_id = req.POST['razorpay_order_id'])
			set_paid = trans_query.update(paid = True)
			amt = trans_query[0].Amount
			print(amt)
			extendedUser.objects.filter(usr = req.user.id).update(amount =F('amount') + (amt/100))
			x = {'rslt' : "success"}
			return render(req, "transaction/success.html" , x)
	return redirect("profile")

@login_required
def trans_withdraw(req): #function for handling withdraw request
	if req.method == 'POST':
		user_amt = extendedUser.objects.get(usr = req.user.id).amount
		name = req.POST.get(req.user)
		# payment_method = 
		val = int(req.POST.get("value"))

		if val < 1: 
			msg.add_message(req,msg.WARNING,"ENTER POSITIVE VALUE TO WITHDRAW")
			return render(req, "transaction/transaction_withdraw.html")

		elif user_amt < val:                
			msg.add_message(req,msg.WARNING,"INSUFFICIENT BALANCE")  
			return render(req, "transaction/transaction_withdraw.html")

		elif user_amt - val <= 50:   
			msg.add_message(req,msg.WARNING,"YOU SHOULD HAVE AS LOW AS 50 INR IN YOUR WALLET")
			return render(req, "transaction/transaction_withdraw.html")

		else : 
			n = random.randint(0,999999)
			transaction.objects.create(
				order_id = str(str(req.user.username)+str(n)),
				name = extendedUser.objects.get(usr = req.user.id),
				Amount = val*100,# saving like razorpay to avoid confusion
				transaction_type="Withdraw"
			)
			extendedUser.objects.filter(usr = req.user.id).update(amount = user_amt - val)
			msg.add_message(req,msg.SUCCESS,'YOUR REQUEST TO WITHDRAW '+str( val) +' INR HAS BEEN SUCCESSFULL ACCEPTED')
		print(name,val)
		return render(req, "transaction/success.html")

	else:
		if extendedUser.objects.get(usr = req.user.id).phone == None :

			msg.add_message(req,msg.WARNING,'YOU HAVE NOT UPDATED YOUR PHONE NUMBER TO PROCEED TRANSACTION')
			return redirect("profile")
	
	cxt = {"remove" : "remove"}
	return render(req, "transaction/transaction_add.html", cxt)
	# return render(req, "transaction/transaction_withdraw.html")

# ///////////////////////////////////////////////
@login_required
def updateprofile(req,id):
	if req.method == 'POST':
		
		payment_method = req.POST.get("payment_method")
		Phonnenum = req.POST.get("phone")
		if extendedUser.objects.filter(phone = Phonnenum).count() > 0:
			msg.add_message(req,msg.WARNING,'phone number already taken')
			return render(req,"enroll/update.html")

		print(payment_method)
		# if ef.is_valid() and payment_method != None and Phonnenum != None :
		if payment_method != "options" and Phonnenum != None :
			# ef.save()
			extendedUser.objects.filter(usr = req.user.id).update(upi_gatewayOfPhone =payment_method , phone = Phonnenum)
			msg.add_message(req,msg.SUCCESS,'YOUR ACCOUNT Phone HAS BEEN SUCCESSFULL UPDATED')
			return redirect("profile")
		else:
			print("hello")
	else:
		if extendedUser.objects.get(usr = req.user.id).phone != None:
			msg.add_message(req,msg.WARNING,'You have setup your phone number')
			return redirect("profile")

	return render(req,"enroll/update.html")

	# make new form for updating profile that doesnt include username and password 

@login_required
def editportfolio(req,id):
	# print("called")
	if req.method == 'POST':
		if req.POST.get('xxid'):
			StkIdStr = req.POST.get('xxid')
			StkIdList = list(StkIdStr.split(","))
			conteseId_x = req.POST.get('contestType')
			print("we got id list")
			print( 'contest type is'+str(conteseId_x))
		else:
			print("we didnt got id list") 

		if req.POST.get('xxQ'):
			StkQStr = req.POST.get('xxQ')
			StkQList = list(StkQStr.split(","))
			
			contestStart_jointime = datetime.time(8,59,59,0000)
			contestEnd_jointime = datetime.time(17,30,00,0000)


			# day_for_contest = [0,1,2,3,4,5,6] # 0 for monday 4 for friday 

			tym = datetime.datetime.now().time()
			if len(StkIdList) > 2 and len(StkQList) > 2 :
				if ContestJoinedByUser.objects.filter(pk = conteseId_x).exists():
					contestCheck = ContestJoinedByUser.objects.filter(pk = conteseId_x)
					print(contestCheck)						
					if tym > contestStart_jointime and tym < contestEnd_jointime:
						msg.add_message(req,msg.SUCCESS,'You cannot edit between 9 am to 5:30 pm')
						print("tried to edit match in between")
					# if datetime.datetime.now().day not in day_for_contest:
					# 	msg.add_message(req,msg.SUCCESS,'You cannot edit at saturay or sunday')
					else:
						ContestConfirm.objects.filter(player__usr = req.user.id , Ongoing_contest = conteseId_x).delete()
						usrid = req.user.id
						edition_type = "update"
						contestfees = None
						# print(StkQList,StkIdList,conteseId_x,usrid,edition_type)
						contest_entry(StkQList,StkIdList,conteseId_x,usrid, contestfees,edition_type)
						print("updated the contest ")

				else :
					msg.add_message(req,msg.WARNING,'ÿou cannot edit this contest')
					print("ÿou cannot edit this contest ")

			else:
				msg.add_message(req,msg.WARNING,'select at least 3 stock')

		else:
			msg.add_message(req,msg.WARNING,'Something went wrong try again !!')

		return redirect("select_contest")


	else:


		value_x = id
		stklist = StockProfile.objects.all()
		cxt = {'cntstype': value_x , 'form' : stklist}
		return render(req,'enroll/contest_joining.html' , cxt) 

	

@login_required
def show_tranactions(req):
	trans = transaction.objects.filter(name__usr = req.user.id )
	if len(trans) >0:
		# trans_dict = {}
		lst = []
		for x in trans:
			lst.append([(x.Amount)/100,x.transaction_type,x.date_joined])
		# print(lst)
		cxt = {"trans_list" : lst}
	return render(req,"transaction/transactions.html", cxt)
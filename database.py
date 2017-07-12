from flask import Flask, session, render_template, url_for, request, redirect
from sqlalchemy import schema, types
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import update
from sqlalchemy import delete,join
from passlib.hash import pbkdf2_sha256
from sqlalchemy import *
from sqlalchemy.sql import exists
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import exc

app = Flask(__name__)

app.config['SQLAlCHEMY_DATABASE_URI']='sqlite:///my.db'
app.config['SECRET_KEY']="random string"
db=SQLAlchemy(app)



engine = create_engine('sqlite:///my.db', echo=True)
Session = sessionmaker(autocommit=False, autoflush=False,bind=engine)
Base = declarative_base()


session1 = Session()
session2=Session()



class Users(Base):
	__tablename__ = 'Users'
	UserID = Column(Integer, primary_key=True,autoincrement=True)
	Username = Column(String(80))
	Password = Column(String(80))
	Email = Column(String(120),)
	Prop = Column(String(50))
	Sellers = relationship('Seller', backref = 'Users')
	Clients = relationship('Client', backref = 'Users')
	Admins = relationship('Admin', backref = 'Users')

	def __init__(self,UserID=None, Username=None, Email=None, Password=None, Prop=None):
		self.UserID = UserID
		self.Username = Username
		self.Email= Email	
		self.Password = Password	
		self.Prop = Prop
		
		
class Program(Base):
	__tablename__ = 'Program'
	ProgramID=Column(Integer, primary_key=True,autoincrement=True)
	Descr=Column(String(250))
	Price=Column(Integer) 
	Admins2 = relationship('Admin', backref = 'Program')

	def __init__(self,ProgramID=None,Descr=None,Price=None):
		self.ProgramID=ProgramID
		self.Descr=Descr
		self.Price=Price 


class Client(Base):
	__tablename__ = 'Client'
	ClientID=Column(Integer, primary_key=True, autoincrement=True)
	Name=Column(String(80))
	Surname=Column(String(80))
	Address=Column(String(80))
	AFM=Column(String(80))
	UserID=Column(Integer, ForeignKey(Users.UserID))
	PhoneNumber=Column(String(80))
	CallsR = relationship('Calls', backref = 'Client')
	
	def __init__(self,ClientID=None,Name=None,Surname=None,Address=None,AFM=None,UserID=None,PhoneNumber=None):
		self.ClientID=ClientID
		self.Name=Name
		self.Surname=Surname
		self.Address=Address
		self.AFM=AFM
		self.UserID=UserID
		self.PhoneNumber=PhoneNumber

class Admin(Base):
	__tablename__ = 'Admin'
	AdminID=Column(Integer, primary_key=True, autoincrement=True) #ayksanontai automata
	Name=Column(String(80))
	Surname=Column(String(80))
	Address=Column(String(80))
	ProgramID=Column(Integer, ForeignKey(Program.ProgramID))
	UserID=Column(Integer, ForeignKey(Users.UserID))

	def __init__(self,AdminID=None,Name=None,Surname=None,Address=None,ProgramID=None,UserID=None): #mporoun na mhn symplirwthoun merika pedia
		self.AdminID=AdminID
		self.Name=Name
		self.Surname=Surname
		self.Address=Address
		self.ProgramID=ProgramID
		self.UserID=UserID

class Seller(Base):
	__tablename__ = 'Seller'
	SellerID=Column(Integer, primary_key=True, autoincrement=True)
	CompanyName=Column(String(80))
	Address=Column(String(80))
	UserID=Column(Integer, ForeignKey(Users.UserID))

	def __init__(self,SellerID=None,CompanyName=None,Address=None,UserID=None):
		self.SellerID=SellerID
		self.CompanyName=CompanyName
		self.Address=Address
		self.UserID=UserID		


class Calls(Base):
	__tablename__ = 'Calls'
	CallID=Column(Integer, primary_key=True, autoincrement=True)
	ClientID=Column(Integer, ForeignKey(Client.ClientID))    
	Date=Column(String(80))
	Time=Column(Integer)  
	FriendPhone=Column(Integer)
	ProgramID=Column(Integer, ForeignKey(Program.ProgramID)) 


	def __init__(self,CallID=None,ClientID=None,Date=None, Time=None,FriendPhone=None,ProgramID=None):
		self.CallID=CallID
		self.ClientID=ClientID
		self.Date=Date
		self.Time=Time
		self.FriendPhone=FriendPhone
		self.ProgramID=ProgramID


def encryption(p):
	pwd = pbkdf2_sha256.encrypt(p, rounds=20000, salt_size= 16)
	return pwd 

def verification(p1,pw):
	return pbkdf2_sha256.verify(p1,pw)	 


	
@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/login/')
def log():
	return render_template('form.html')

@app.route('/logout/')
def logout():
	session.clear()
	msg="You have been logout!"
	return render_template('index.html', msg=msg)
	
@app.route('/form/', methods = ['GET', 'POST'])	
def form():
	if request.method == 'POST':
		session['tag'] = False
		email = request.form['email']
		password = request.form['password']
		registered_user = session2.query(exists().where(Users.Email == email)).scalar()
		if registered_user is True:
			person = session2.query(Users).filter_by(Email=email).first()
			if verification(password,person.Password):
				session['userid']= person.UserID
				session['logged_in'] = True
				if person.Prop == 'Admin':
					session['Prop']= 'Admin'
					return render_template('admin.html')
				elif person.Prop == 'Seller':
					session['Prop']= 'Seller'
					return render_template('seller.html')
				else:
					session['Prop']= 'Client'
					return render_template('client.html')
			else:
				return render_template('form.html') # la8os kwdikos 
		else:
			return render_template('form.html') # la8os onoma xrhsth
	else:
		return render_template('form.html') #elegxei gia to method post, an einai to vgazoume sto telos
		
@app.route('/client/')
def cl():
	session['tag']=False
	return render_template('client.html')

@app.route('/seller/')
def sel():
	return render_template('seller.html')
	
@app.route('/ser/')
def ser():
	return render_template('ser.html')

@app.route('/admin/')
def ad():
	return render_template('admin.html')
	
@app.route('/addsel/')
def adds():
	return render_template('addsel.html')
	
@app.route('/addcl/')
def add():
	return render_template('addcl.html')
	
@app.route('/addpr/')
def addp():
	return render_template('addpr.html')
	
@app.route('/ad/', methods = ['GET', 'POST'])	
def adder():
	msg=None
	if request.method == "POST":
		Email = request.form['Email']
		Username = request.form['Username']
		Password = request.form['Password']
		Name = request.form['Name']
		Surname= request.form['Surname']
		Address= request.form['Address']
		AFM= request.form['AFM']
		PhoneNumber=request.form['PhoneNumber']

		obj = Users(Username = Username, Email = Email, Password = encryption(Password), Prop=u'Client' )
		session2.add(obj)
		session2.commit()

		obj1= Client(Name=Name, Surname=Surname, Address=Address, AFM=AFM,UserID=obj.UserID, PhoneNumber=PhoneNumber)		
		session2.add(obj1)
		msg='Your inputs have been added!'
		session2.commit()

		if session['Prop'] == 'Admin':
			return render_template('admin.html', msg=msg)
		else:
			return render_template('seller.html', msg=msg)
	else:
		msg='Error.Something gone wrong!'
		if session['Prop'] == 'Admin':
			return render_template('admin.html', msg=msg)
		else:
			return render_template('seller.html', msg=msg)
		
@app.route('/ads/', methods = ['GET', 'POST'])	
def adder1():
	msg=None
	if request.method == "POST":
		Email = request.form['Email']
		Username = request.form['Username']
		Password = request.form['Password']
		CompanyName = request.form['CompanyName']
		Address= request.form['Address']
		
		obj = Users(Username = Username, Email = Email, Password = encryption(Password), Prop=u'Seller')
		session2.add(obj)
		session2.commit()

		obj1= Seller(CompanyName=CompanyName,Address=Address,UserID=obj.UserID)		
		session2.add(obj1)
		session2.commit()

		msg='Your inputs have been added!'
		
		return render_template('admin.html', msg=msg)
	else:
		msg='Error.Something gone wrong!'
		return render_template('admin.html', msg=msg)
		
@app.route('/adpr/', methods = ['GET', 'POST'])	
def adder2():
	msg=None
	if request.method == "POST":
		Description = request.form['Description']
		Price = request.form['Price']
		obj= Program(Descr=Description,Price=Price)
		session2.add(obj)
		msg='Your inputs have been added!'
		session2.commit()
		return render_template('admin.html', msg=msg)
	else:
		msg='Error.Something gone wrong!'
		return render_template('admin.html', msg=msg)
		
@app.route('/account/')
def account():	
	msg = None 
	client = session.get('userid', None)	
	client = session2.query(Client).filter_by(UserID=client).first()
	client1 = client.ClientID
	Name = client.Name
	Surname = client.Surname
	Address=client.Address
	program = session2.query(Calls).filter_by(ClientID = client1).first()
	Program_client = program.ProgramID
	price = session2.query(Program).filter_by(ProgramID = Program_client).first()
	Price = price.Price	
	session['tag'] = True
	return render_template('client.html',name=Name, surname=Surname,address=Address, price=Price)




@app.route('/pay/')
def pay():
	client=session.get('userid',None)
	client1=session2.query(Client).filter_by(UserID=client).first()
	clientid = client1.ClientID
	program = session2.query(Calls).filter_by(ClientID = clientid).first()
	Program_client = program.ProgramID
	price = session2.query(Program).filter_by(ProgramID = Program_client).first()
	Price = price.Price
	return render_template('pay.html', Price=Price)

@app.route('/payb/', methods = ['GET', 'POST'])	
def payb():
	if request.method == "POST":
		Amount = request.form['Amount']
		client=session.get('userid',None)
		client1=session2.query(Client).filter_by(UserID=client).first()
		clientid = client1.ClientID
		program = session2.query(Calls).filter_by(ClientID = clientid).first()
		Program_client = program.ProgramID
		price = session2.query(Program).filter_by(ProgramID = Program_client).first()
		Price = price.Price
		if Amount == str(Price):
			msg='Your bills have been paid'
			session['paid']=True
			return render_template('pay.html', msg=msg)
		else:
			msg='Please insert the right amount '
			return render_template('result.html', msg=msg)
	else:
		msg='Error.Something gone wrong!'
		return render_template('admin.html', msg=msg)
	
@app.route('/serach/', methods = ['GET', 'POST'])	
def search():
	if request.method == "POST":
		afm = request.form['afm']
		registered_user = session2.query(exists().where(Client.AFM == afm)).scalar()
		if registered_user is True:			
			client = session2.query(Client).filter_by(AFM = afm).first()
	  		Person = client.ClientID
	  		Name = client.Name
	  		Surname = client.Surname
			Address=client.Address
			PhoneNumber=client.PhoneNumber
	  		program = session2.query(Calls).filter_by(ClientID = Person).first()
	  		Program_client = program.ProgramID
	  		price = session2.query(Program).filter_by(ProgramID = Program_client).first()
	  		Price = price.Price
	  		Program_descr =price.Descr
			return render_template('search.html', Name = Name, Surname = Surname, Address = Address, AFM = afm, PhoneNumber = PhoneNumber,Program = Program_descr, Price = Price)
	  	else:
			msg='This AFM doent exist!'
	  		return render_template('ser.html', msg=msg)
	else:	
		msg='Error.Something went wrong!'
		return render_template('admin.html', msg=msg)
	
	
		
@app.route('/Change/')			# auto apla emfanizei enan pinaka me ta paketa wste na ta vlepei o xrhsths
def change():				
	query = select([Program])
	rows = session2.execute(query)  
	return render_template('chpro.html',rows= rows)
	

@app.route('/chprog/' , methods = ['GET', 'POST'])
def	chprog():
	msg=None
	msg1=None
	if request.method == "POST": #thelw na kanw update sto program id enos client...to path einai apo client.name->client.id->calls.programid (to client id uparxei ston Calls)
		AFM = request.form['AFM']	# pernw to onoma tou client pou theloume na ginei h allagh
		Programid = request.form['Programid']	# kai to neo program id pou 8a tou valoume
		
		registered_user = session2.query(exists().where(Program.ProgramID == Programid)).scalar()
		if registered_user == True:
			client = session2.query(Client).filter_by(AFM = AFM).first()
			clientid =  client.ClientID		

			stmnt = update(Calls, Calls.ClientID==clientid)
			engine.execute(stmnt, ProgramID=Programid)
			msg = "Successful Update"
			return render_template('seller.html', msg=msg)
		else:
			msg1='Something went wrong!'
			return render_template('seller.html', msg1=msg1)						
	else:
		msg='Something went wrong!'
		return render_template('seller.html', msg1=msg1)
		
@app.route('/prov/')
def prov():	
	msg = None 
	client=session.get('userid',None) #pairneis to userid
	client1=session2.query(Client).filter_by(UserID=client).first() #ston pinaka client psaxneiw to userid poy einai monadiko kai tha antistoixei se monadiko clientid
	clientid=client1.ClientID #apothukeyeis to clientid 
	
	all_programs = session2.query(Calls).filter_by(ClientID = clientid).all() #filtrareis me vash to clientid ton pinaka Calls gia na emfanistoun telika oles oi klhseis autounou me to sygkekrimeno client id
	
	return render_template('callh.html',programs= all_programs)
	
#---------------------------------------------------------------------------------------------------#




Base.metadata.create_all(engine,checkfirst=True)


allah = Users(Username = u'allah', Email = u'allah@gmail.com', Password = encryption("hey"),Prop = u'Admin')
ash = Users(Username = u'AshKet',Email = u'catchemall@gmail.com', Password= encryption('pikatchu'), Prop = u'Admin') 
oak = Users(Username = u'ProfOak', Email = u'profoak@gmail.com', Password = encryption('pokemon'), Prop = u'Seller')
gary = Users(Username = u'GaryO', Email = u'garyoak@gmail.com', Password = encryption('squirtle'),  Prop = u'Seller')
misty = Users(Username = u'MistyW', Email = u'mistyw@gmail.com', Password = encryption('starmie'), Prop = u'Client')
broke = Users(Username = u'BrokeR', Email = u'broker@gmail.com', Password = encryption('onix'), Prop = u'Client')


session1.add(allah)
session1.add(ash)
session1.add(oak)
session1.add(gary)
session1.add(misty)
session1.add(broke)

allah1=Admin(Name=u'mrallah',Surname=u'tourmeq',Address=u'adoudabi',ProgramID=1,UserID=allah.UserID) 
ash1=Admin(Name=u'Ash',Surname=u'Catchemall',Address=u'Pallet Town',ProgramID=2,UserID=ash.UserID)
session1.add(allah1)
session1.add(ash1)

oak1=Seller(CompanyName="PokemonBazaar",Address="Everywhere",UserID=oak.UserID)
gary1=Seller(CompanyName="VillainStore",Address="PokemonHell",UserID=gary.UserID)
session1.add(oak1)
session1.add(gary1)

misty1=Client(ClientID=1,Name=u'Misty',Surname=u'Water',Address=u'Cerulean Gym',AFM=5446548754,UserID=misty.UserID,PhoneNumber=6956724563)
broke1=Client(ClientID=2,Name=u'Brock',Surname=u'Rock',Address=u'Pewter City',AFM=5745476476,UserID=broke.UserID,PhoneNumber=6987467423)
session1.add(misty1)
session1.add(broke1)

pr=Program(ProgramID=1,Descr="Foithtiko",Price=15)
pr1=Program(ProgramID=2,Descr="Oikogeneiako",Price=20)
session1.add(pr)
session1.add(pr1)
cal=Calls(ClientID=misty1.ClientID,Date='21/2/2016',Time=10,FriendPhone=6987512345,ProgramID=1)  		
cal2=Calls(ClientID=misty1.ClientID,Date='12/4/2016',Time=7,FriendPhone=6930987645,ProgramID=1)
cal3=Calls(ClientID=misty1.ClientID,Date='7/6/2016',Time=20,FriendPhone=6998904345,ProgramID=1)
cal4=Calls(ClientID=broke1.ClientID,Date='17/1/2016',Time=4,FriendPhone=6965512345,ProgramID=2)
cal5=Calls(ClientID=broke1.ClientID,Date='7/3/2016',Time=15,FriendPhone=6987574639,ProgramID=2)
cal6=Calls(ClientID=broke1.ClientID,Date='30/5/2016',Time=2,FriendPhone=6983412345,ProgramID=2)
session1.add(cal)
session1.add(cal2)
session1.add(cal3)
session1.add(cal4)
session1.add(cal5)
session1.add(cal6)


try:
	session1.commit()
except exc.SQLAlchemyError:
	pass
	



if __name__ == '__main__':
  app.run(debug=True, use_reloader=False)
  


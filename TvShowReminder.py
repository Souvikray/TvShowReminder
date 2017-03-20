from bs4 import BeautifulSoup
import urllib.request
from html.parser import HTMLParser
import sqlite3
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import TwilioRestClient

try:
    #first we create four different files each storing information about Tv show name,season and episode,show time and Tv channel respectively
    fo1 = open("/home/souvik/PycharmProjects/web", "w")
    fo2 = open("/home/souvik/PycharmProjects/web2", "w")
    fo3 = open("/home/souvik/PycharmProjects/web3", "w")
    fo4 = open("/home/souvik/PycharmProjects/web4", "w")
    #we also create a file to store error info in case if any error occurs
    eo = open("/home/souvik/PycharmProjects/err", "w")

    d,m,y = input("Please select a date to get a list of Tv Shows being aired for that day(DD.MM.YYYY) ").split(".")
    print("Please wait while we get you the list of TV Shows...\n")
    url = "http://www.tvmuse.com/schedule.html?date="+str(m)+"/"+str(d)+"/"+str(y)
    #we create a request header to send browser information to the website
    headers = {}
    #we add browser information to the header dictionary
    headers["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    #we sent the a request to the website
    req = urllib.request.Request(url,headers=headers)
    #we receive the response from the website
    res = urllib.request.urlopen(req)
    #we read the information and store in 'content' variable
    content = res.read()
    #create a soup object to parse the site
    soup = BeautifulSoup(content,"lxml")
    try:
        #we extract information from the website making use of suitable tags
        result1 = soup.find_all("span" ,{"class":"c1 brd_r_dot"})
        for i in result1:
            fo1.write("{}\n".format(i.text))
        result2 = soup.find_all("span" ,{"class":"c2 brd_r_dot"})
        for j in result2:
            fo2.write("{}\n".format(j.text))
        result3 = soup.find_all("span" ,{"class":"c4 brd_r_dot"})
        for k in result3:
            fo3.write("{}\n".format(k.text))
        result4 = soup.find_all("span" ,{"class":"c5"})
        for l in result4:
            fo4.write("{}\n".format(l.text))

    except HTMLParser as he:
        print(he)

except (IOError,ValueError):
    print("IOError or ValueError has occured")
except Exception as e:
    print(e)

finally:
    fo1.close()
    fo2.close()
    fo3.close()
    fo4.close()

#we create an empty list to transfer the data from the file to the list
webList = []
with open("/home/souvik/PycharmProjects/web","r") as cont:
    for line in cont:
        line = line.strip()
        webList.append(line)

web2List = []
with open("/home/souvik/PycharmProjects/web2","r") as cont:
    for line in cont:
        line = line.strip()
        web2List.append(line)

web3List = []
with open("/home/souvik/PycharmProjects/web3","r") as cont:
    for line in cont:
        line = line.strip()
        web3List.append(line)

web4List = []
with open("/home/souvik/PycharmProjects/web4","r") as cont:
    for line in cont:
        line = line.strip()
        web4List.append(line)

#we remove the first element from the 'web4List' as it is a useless information
web4List.pop(0)
webListJoined = list(zip(webList,web2List,web3List,web4List))
print(webListJoined)

#we create a method to print the content of the database table
def printTvInfo():
    resultSet = cursor.execute(sql3)
    for row in resultSet:
        print(row)

#table for Tv Show information
#connect to the TvShow database
db = sqlite3.connect("TvShow")
#create a cursor object
cursor = db.cursor()
sql = "DROP TABLE IF EXISTS Show"
sql1 = "CREATE TABLE Show(id integer primary key autoincrement not null,showName text,se text,time varchar(10),channel varchar(10))"
sql2 = "INSERT INTO Show(showName,se,time,channel) VALUES(?,?,?,?)"
sql3 = "SELECT * FROM Show"

try:
    cursor.execute(sql)
    cursor.execute(sql1)
    #we loop through the list and insert the data into the database table
    for i in webListJoined:
       cursor.execute(sql2, [i[0], i[1], i[2], i[3]])
    printTvInfo()
    db.commit()

except sqlite3.OperationalError as oe:
    print("Unsuccessful operation")
    print(oe)
    db.rollback()

finally:
    db.close()
#we create a 'userShow' list to store the user's choice of Tv shows
userShow = []
#we create a 'showPref' list to store the entire information about the selected Tv shows
showPref = []
while True:
    userShow.append(input("Please select the Tv Show you would like to be reminded of "))
    choice = input("Do you want to select another Tv Show(Y/N)")
    if choice=="Y":
        continue
    else:
        break

email = input("Please enter your email id to receive confirmation email ")
phoneNumber = input("Please enter your mobile number to receive reminder sms ")
#we add '+91' to the phoneNumber to indicate its an Indian number
phoneNumber = "+91"+phoneNumber
print("Thank You!\nYou will receive a confirmation email and an SMS about the show details")

try:
    db = sqlite3.connect("TvShow")
    cursor = db.cursor()
    sql4 = "DROP TABLE IF EXISTS Preference"
    sql5 = "CREATE TABLE Preference(id integer primary key autoincrement not null,showName text,se text,time varchar(10),channel varchar(10))"
    sql6 = "SELECT showName,se,time,channel FROM Show WHERE showName=(?)"
    sql7 = "INSERT INTO Preference(showName,se,time,channel) VALUES(?,?,?,?)"
    sql8 = "SELECT * FROM Preference"
    cursor.execute(sql4)
    cursor.execute(sql5)
    for i in userShow:
        resultSet = cursor.execute(sql6,[i])
        for row in resultSet:
            showPref.append(row)

    for i in showPref:
        cursor.execute(sql7,[i[0],i[1],i[2],i[3]])
    resultSet = cursor.execute(sql8)
    db.commit()

except sqlite3.OperationalError as oe:
    print("Unsuccessful operation")
    print(oe)
    db.rollback()
except IndexError:
    print('Error on line {}').format(sys.exc_info()[-1].tb_lineno)
finally:
    db.close()

#Create an email to send a confirmation message
fromaddr = "souvikray999@gmail.com"
#we pass the user's email id
toaddr = str(email)
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
#subject of the email
msg['Subject'] = "Confirmation email"
#content of the email
body = "This is a confirmation email.You will receive an SMS prior to the start of the show\nThanks for using our service!"
msg.attach(MIMEText(body, 'plain'))
#we use SSL encryption
server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
server.ehlo()
#pass your email id and password
server.login("souvikray999@gmail.com", "***********")
#the message must be sent as a string
text = msg.as_string()
#send the mail
server.sendmail(fromaddr, toaddr, text)
#disconnect from the server
server.quit()

#send sms to the user's phone number
#we create a 'showPref2' list to store the information about the user's selected Tv shows
showPref2 = []
try:
    db = sqlite3.connect("TvShow")
    cursor = db.cursor()
    sql8 = "SELECT * FROM Preference"
    resultSet = cursor.execute(sql8)
    for row in resultSet:
        showPref2.append(row)
    db.commit()

    # put your own credentials here
    ACCOUNT_SID = "AC598fdd1a56846658f66065**********"
    AUTH_TOKEN = "ce2337ed21d390367e0188**********"
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        #pass user's phone number
        to=str(phoneNumber),
        #your twilio phone number
        from_="+1 856-469-4604 ",
        #pass the list in the form of a string
        body=str(showPref2),
        media_url="https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg",
    )
except sqlite3.OperationalError as oe:
    print("Unsuccessful operation")
    print(oe)
    db.rollback()

finally:
    db.close()


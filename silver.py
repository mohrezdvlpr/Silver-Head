import time
import requests
import telepot
import random
import datetime
import instaloader
from peewee import *
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup as mkp
from telepot.namedtuple import InlineKeyboardButton as btn

L = instaloader.Instaloader()
#L.login('mohrezdvlpr2','123456Aa')
L.load_session_from_file("mohrezdvlpr2")

bot = telepot.Bot('5384433217:AAHLAS7To72hHUFm0QmiAyUfPWkAaZUF9UU')

admin = 220520720

step = 0
Link = ""
Followers = ""
msg_id = 0 

database = SqliteDatabase('Silver-DB.db')

# Database Init .....
class USERS(Model):
    id = PrimaryKeyField()
    chat_id = CharField()
    name = CharField()
    is_first = IntegerField()
    class Meta:
         database = database

class PAYMENT(Model):
    id = PrimaryKeyField()
    name = CharField()
    chat_id = CharField()
    order_id = CharField()
    order_id2 = CharField()
    token = CharField()
    amount = IntegerField()
    product = CharField()
    link = CharField()
    followers = CharField()
    status = IntegerField()
    time = DateField()
    class Meta:
        database = database
database.connect()

def payment(order_id, name, amount,chat_id,product):
    global Link
    global Followers

    url = "https://api.idpay.ir/v1.1/payment" 
    data = {
      "order_id": order_id,
      "amount":   amount*10,
      "name":     name,
      "callback": "https://grety.pythonanywhere.com/",
        }
    headers = {"Content-Type": "application/json",
      "X-API-KEY": "b1b49797-1cc1-4493-bed1-005ff4a07363"}
    res = requests.post(url,json=data,headers=headers)

    PAYMENT.create(chat_id=chat_id,name=name,order_id=order_id,token=res.json()["id"],amount=amount,status=0,time=datetime.date.today(),link=Link,followers=Followers).save()

    return res.json()["id"],res.json()["link"] 


def download_post(text):
    global Link
    data = text
    changing_url = text.split("/")
    url_code = changing_url[4]
    url = f"https://www.instadownloader.org/a.php?i=https://www.instagram.com/p/{url_code}/"    
    visit = requests.get(url).json()
    if visit['status'] == '1':
        return visit

def download_profile(text):
    global Link
    global Followers
    Link = text
    profile = instaloader.Profile.from_username(L.context, text.replace("@",''))
    if profile.is_private:
        return False
    img = profile.profile_pic_url
    Followers = str(profile.followers)
    following = profile.followees
    fullname = profile.full_name
    text = """نام : {}
    آی دی : {}
    فالوور : {}
    فالووینگ :‌ {}
    """.format(fullname,text,Followers,following)
    return text,img

back_keyboard = mkp(inline_keyboard=[
                       [btn(text='خانه' ,callback_data='home')]])
main_keyboard = mkp(inline_keyboard=[
                       [btn(text='فالوور ارزان' ,callback_data='cheap_follower')],[btn(text='خرید لایک' ,callback_data='like')],[btn(text='فالوور ایرانی' ,callback_data='irani_follower')],[btn(text='بازدید استوری' ,callback_data='story_view')],[btn(text='تماس با ما' ,callback_data='contact')]])

follower_keyboard = mkp(inline_keyboard=[
                       [btn(text='1 K' ,callback_data='h1')],[btn(text='2 K' ,callback_data='h2')],[btn(text='3 K' ,callback_data='h3')],[btn(text='5 K' ,callback_data='h4')],[btn(text='10 K' ,callback_data='h5')],[btn(text='20 K' ,callback_data='h6')],[btn(text='منو اصلی 🏠' ,callback_data='home')]])
like_keyboard = mkp(inline_keyboard=[
                       [btn(text='1 K' ,callback_data='l1')],[btn(text='2 K' ,callback_data='l2')],[btn(text='3 K' ,callback_data='l3')],[btn(text='5 K' ,callback_data='l4')],[btn(text='10 K' ,callback_data='l5')],[btn(text='20 K' ,callback_data='l6')],[btn(text='منو اصلی 🏠' ,callback_data='home')]])
follower_irani_keyboard = mkp(inline_keyboard=[
                       [btn(text='1 K' ,callback_data='i1')],[btn(text='2 K' ,callback_data='i2')],[btn(text='3 K' ,callback_data='i3')],[btn(text='5 K' ,callback_data='i4')],[btn(text='10 K' ,callback_data='i5')],[btn(text='20 K' ,callback_data='i6')],[btn(text='منو اصلی 🏠' ,callback_data='home')]])

confirm_keyboard = mkp(inline_keyboard=[
                       [btn(text='رد' ,callback_data='deny')],[btn(text='تایید' ,callback_data='accept')]])
def main(msg):
        global step
        global msg_id

    #try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        name = msg["chat"]["first_name"]
        text = msg["text"]

        if text == "/start":
            bot.sendMessage(chat_id,"خوش آمدید",reply_markup=main_keyboard)
        
        elif "@" in text and step == 1:
            progress = bot.sendMessage(chat_id,"درحال بررسی پیج ...")["message_id"]
            result = download_profile(text)
            if result:
                text,img = result
                bot.deleteMessage((chat_id,progress))
                bot.sendPhoto(chat_id,caption=text,photo=img,reply_markup=confirm_keyboard)
            else : 
                bot.editMessageText((chat_id,progress),text="لطفا پیج را از حالت شخصی به عمومی تغییر دهید.",reply_markup=back_keyboard)


        elif "instagram.com" in text and step == 2:
            bot.sendMessage(chat_id=chat_id, text="1")
            visit = download_post(text)
            if "d.php" in visit['output']:
                bot.sendVideo(chat_id=chat_id, video=visit['output'],caption="آیا پست مورد نظر را تایید میکنید؟",reply_markup=confirm_keyboard)
            else:
                bot.sendPhoto(chat_id=chat_id, photo=visit['output'],caption="آیا پست مورد نظر را تایید میکنید؟",reply_markup=confirm_keyboard)
            step = 0

  #  except:
   #     pass


def callback(msg):
    global step
    query_id, from_id, query = telepot.glance(msg, flavor='callback_query')
    chat_id = int(msg["from"]["id"])
    name = msg["from"]["first_name"]
    message_id = int(msg["message"]["message_id"])
    if query == "cheap_follower":
        bot.editMessageText((chat_id,message_id), text="لطفا آی دی پروفایل خود را همراه با @ وارد کنید.")
        step = 1
    elif query == "like":
        bot.editMessageText((chat_id,message_id), text="لطفا لینک پست را وارد کنید.")
        step = 2
    elif query == "irani_follower":
        bot.editMessageText((chat_id,message_id), text="لطفا آی دی پروفایل خود را همراه با @ وارد کنید.")
        step = 3
    elif query == "story_view":
        bot.editMessageText((chat_id,message_id), text="این بخش در حال حاظر در دسترس نمی باشد.",reply_markup=back_keyboard)
        step = 0
    elif query == "contact":
        bot.editMessageText((chat_id,message_id), text="Dawsham MohRezDvlpr :)",reply_markup=back_keyboard)
    elif query == "home":
        bot.editMessageText((chat_id,message_id), text="اینجا به زودی یه چیزی راه اندازی میشود :)",reply_markup=main_keyboard)
    elif query == "accept":
        bot.deleteMessage((chat_id,message_id))
        if step == 1 :
            bot.sendMessage(chat_id,"تعداد فالوور را انتخاب کنید.",reply_markup=follower_keyboard)
            
        elif step == 2 :
            pass
        elif step == 3 :
            pass

    elif query == "deny":
        bot.editMessageText((chat_id,message_id),text="درخواست لغو شد.",reply_markup=back_keyboard)

    elif query in ["h1","h2","h3","h4","h5"]:
        bot.answerCallbackQuery(query_id, text="درحال ایجاد درگاه پرداخت ...") 
        order_id = random.randrange(10000000,99999999)
        if query =="h1":
            amount = 13000
        elif query =="h2":
            amount = 25000
        elif query =="h3":
            amount = 37000
        elif query =="h4":
            amount = 60000
        elif query =="h5":
            amount = 110000
        elif query =="h6":
            amount = 200000
        token , url = payment(order_id, name, amount,chat_id,query)
        bot.editMessageText((chat_id,message_id),"قیمت : {} لینک :‌{} توکن : {} ".format(amount,url,token))

    elif query in ["l1","l2","l3","l4","l5"]:
        pass

MessageLoop(bot, {'chat': main,
                 'callback_query': callback}).run_as_thread()
while 1 : 
    pass
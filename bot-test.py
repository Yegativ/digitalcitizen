import config
import requests
import telebot
import json
from telebot import apihelper
from telebot import types
import sqlite3
import logging

#ip = '185.228.233.248'
#port = '1080'

#apihelper.proxy = {
  #'https': 'socks5://{}:{}'.format(ip,port)
#}


#oper_with_db("UPDATE text_for_user SET text='Это измененный текст' WHERE id=12")    -
#    допилить апдейт для админки обязательно исползовать условие WHERE иначе на данный текст будет заменен весь столбец

# buttons = types.InlineKeyBoardMarkup - Создание Inline кнопку
# buttons.add(*[types.InlineKeyBoardButton(name,callback_data = name) for name in ["Да","Нет"]])                 'Доп. инф.  в группе

#button.add(types)           -



bot = telebot.TeleBot(config.token)

_db_Number_of_User = 0

_db_User_Status = 0

myArray =[_db_Number_of_User,_db_User_Status]
print(myArray)

WaitMode = 0
UserMode = 1
AdminMode = 2
@bot.message_handler(commands = ['start'])
def start(message):
    #try:
    res = cursorConnectionAndRead("SELECT Status FROM First_4_answers WHERE UserTelegrammID =%s" %message.from_user.id)
    res =int(res[0][0])

    if res == 1:
        userRights(message)
    elif res == 0:
        considiration(message)
    elif res ==2:
        adminRights(message)
            
#    except:
 #       main(message)


@bot.message_handler(commands =['info'])
def info(message):
    try:
        res = cursorConnectionAndRead(
            "SELECT Status FROM First_4_answers WHERE UserTelegrammID =%s" % message.from_user.id)
        res = int(res[0][0])
        print(res)
        if res == 0:
            bot.send_message(message.chat.id,
                             'Ваша заявка ещё на рассмотрении администратора,Ожидайте ')
        elif res == 1:
            bot.send_message(message.chat.id,
                             'Вы Числитесь как User напишите /start что бы начать работу')
        elif res == 2:
            bot.send_message(message.chat.id,
                             'Вы числитесь как Admin напишите /start что бы начать работу')
    except:
        bot.send_message(message.chat.id,'Пока вы не зарегисрированы, отправьте  команду /start для регистрации')








@bot.message_handler(commands = ['admin'])
def adminModeActivation(message):
    bot.send_message(message.chat.id,"Вы ввели команду для получения прав Админа ")
    bot.send_message(message.chat.id,"Введите пароль:")
    bot.register_next_step_handler(message,adminPasswordCheck)



def main(message):
    global results
    global myArray

    myArray = list(myArray)
    myArray = [_db_Number_of_User, _db_User_Status]
    results = cursorConnectionAndRead("SELECT text FROM greetings")

    bot.send_message(message.chat.id, results)
    results = cursorConnectionAndRead("SELECT questionTEXT FROM First_4_questions")
    questioning(message)






def questioning(message):
    global results
    global myArray
    
    print(results)
    if results !=[]:
        for i in results:
            bot.send_message(message.chat.id,i)
            bot.register_next_step_handler(message,questoningStep2)
            del results[0]
            break
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True) #one_time_keyboard=True - спрятать кнопку после нажатия
        keyboard.add(*[types.KeyboardButton(name) for name in["Отправить"]])
        bot.send_message(message.chat.id, "Если все данные верны нажмите 'Отправить', в противном случае введите данные заново нажав на /start", reply_markup=keyboard)
        
        myArray[_db_Number_of_User]=message.from_user.id
        myArray = tuple(myArray)

        bot.register_next_step_handler(message,finalStepOfRegistration)

        
    
def questoningStep2(message):
    
    myArray.append(message.text)
    print(myArray)
    
    questioning(message)



    

def cursorConnectionAndRead(sql):
    conn = sqlite3.connect('TZ_base.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    info = cursor.fetchall()
    conn.close()
    return info



def cursorConnectionAndWrite(tableName,insertingTurpleWithValues):
    conn = sqlite3.connect('TZ_base.db')
    cursor = conn.cursor()
    cursor.execute("insert into %s values %s"%(tableName,insertingTurpleWithValues))
    conn.commit()
    conn.close()


def cursorConnectionAndUpdate(tableName,columnText,textValue,columnForOrientation,columnForOrientationValue):
    conn = sqlite3.connect('TZ_base.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE %s SET %s = '%s'  WHERE %s = %s" %(tableName,columnText,textValue,columnForOrientation,columnForOrientationValue))
    conn.commit()
    conn.close()

def finalStepOfRegistration(message):
    global myArray

    if message.text == "Отправить":
        bot.send_message(message.chat.id,
                         'Поздравляю вы прошли регистрацию, ваша заявка находится на рассмотрении администрации')
        bot.send_message(message.chat.id,
                         'Используйте команду /start для того чтобы узнать ваш статус')

        cursorConnectionAndWrite("First_4_answers", myArray)
    else:
        start(message)

        #cursorConnectionAndUpdate("First_4_answers","Status",1,'UserTelegrammId',message.from_user.id)




def considiration(message):
    bot.send_message(message.chat.id, cursorConnectionAndRead(
        "SELECT text_after_registration FROM RegistrationComplete WHERE tag = 'review_of_user'"))

def userRights(message):
    global results
    results = cursorConnectionAndRead("SELECT text FROM buttons WHERE id=1 OR id = 2 OR id = 3 OR id = 4")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name[0]) for name in results])
    bot.send_message(message.chat.id,
                     "Для выбора функции нажмите на кнопку",
                     reply_markup=keyboard)
    bot.register_next_step_handler(message,ButtonChoose)
    

def adminPasswordCheck(message):
    #из таблицы плучаем информацию в виде кортежа в списке, поэтому надо преобразовать в str через  [0][0]
    if  str(cursorConnectionAndRead("SELECT password FROM adminPassword")[0][0]) == message.text :
        cursorConnectionAndUpdate("First_4_answers","Status",AdminMode,"UserTelegrammID",message.from_user.id)
        bot.send_message(message.chat.id,"Теперь вы зарегистрированы как Админ и можете пользоваться привилегиями этого статуса")
    else:
        bot.send_message(message,"Введенный пароль не подходит")


def adminRights(message):
    global results
    results = cursorConnectionAndRead("SELECT text FROM buttons WHERE id=5 OR id = 6 OR id = 7 OR id = 8 OR id = 9 OR id = 10")
    print(results)
    bot.send_message(message.chat.id,  cursorConnectionAndRead(
        "SELECT text_after_registration FROM RegistrationComplete WHERE tag = 'admin'"))

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)  # one_time_keyboard=True - спрятать кнопку после нажатия
    keyboard.add(*[types.KeyboardButton(name[0]) for name in results])
    bot.send_message(message.chat.id,
                     "Для выбора функции нажмите на кнопку",
                     reply_markup=keyboard)

    bot.register_next_step_handler(message,ButtonChoose)


def ButtonChoose(message):
    global results
    results = cursorConnectionAndRead("SELECT text FROM buttons")
    print(cursorConnectionAndRead("SELECT text FROM buttons WHERE id=5"))
    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=1")[0][0]:
       InfoProect(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=2")[0][0]:
        requests(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=3")[0][0]:
        ChangeText(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=4")[0][0]:
        Developments(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=5")[0][0]:
        ChangeKeyWords(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=6")[0][0]:
        ChangeQuestions(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=7")[0][0]:
        ChangeText(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=8")[0][0]:
        Developments(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=9")[0][0]:
        GroupMembers(message)

    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE id=10")[0][0]:
        Vacancies(message)
    if message.text == cursorConnectionAndRead("SELECT text FROM buttons WHERE if=15")[0][0]
def requests(message):
    global results
    results = cursorConnectionAndRead("SELECT text FROM buttons WHERE id=11 OR id=12 OR id=13 OR id=14 OR id=15")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)  # one_time_keyboard=True - спрятать кнопку после нажатия
    keyboard.add(*[types.KeyboardButton(name[0]) for name in results])
    bot.send_message(message.chat.id, cursorConnectionAndRead("SELECT text FROM greetings WHERE id=2")[0][0],reply_markup=keyboard)
    bot.send_message(message.chat.id, str(1)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=1")[0][0])
    bot.send_message(message.chat.id, str(2)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=2")[0][0])
    bot.send_message(message.chat.id, str(3)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=3")[0][0])
    bot.send_message(message.chat.id, str(4)+"."+cursorConnectionAndRead("SELECT text FROM buttons WHERE id=14")[0][0])
    bot.send_message(message.chat.id, str(5)+"."+cursorConnectionAndRead("SELECT text FROM buttons WHERE id=15")[0][0])
    bot.register_next_step_handler(message, ButtonChoose)
        
def Fullproblems(message):
    bot.send_message(message.chat.id, str(1)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=1")[0][0])
    bot.send_message(message.chat.id, str(2)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=2")[0][0])
    bot.send_message(message.chat.id, str(3)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=3")[0][0])
    bot.send_message(message.chat.id, str(4)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=4")[0][0])
    bot.send_message(message.chat.id, str(5)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=5")[0][0])
    bot.send_message(message.chat.id, str(6)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=6")[0][0])
    bot.send_message(message.chat.id, str(7)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=7")[0][0])
    bot.send_message(message.chat.id, str(8)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=8")[0][0])
    bot.send_message(message.chat.id, str(9)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=9")[0][0])
    bot.send_message(message.chat.id, str(10)+"."+cursorConnectionAndRead("SELECT text FROM problems WHERE id=10")[0][0])
    
        
        
    
    
def InfoProect(message):
    global results
    results = cursorConnectionAndRead("SELECT url FROM url WHERE id = 1")
    keyboard = types.InlineKeyboardMarkup()  # one_time_keyboard=True - спрятать кнопку после нажатия
    keyboard.add(types.InlineKeyboardButton("Читать далее", url=results[0][0]))
    bot.send_message(message.chat.id, "Клуб Активистам города, которым не все равно, где жить", reply_markup=keyboard)
    bot.register_next_step_handler(message,ButtonChoose)
def ChangeKeyWords(message):
    global results
    global myArray

    bot.send_message(message.chat.id,"Вы выбрали функцию 'Ключевые слова' теперь вы можете изменить текст на кнопках"
                     "вам по очереди будет выведен текст каждой кнопки, если вы захотите изменить его то просто отправьте тект с новым вопросом")
    results = cursorConnectionAndRead("SELECT id FROM buttons")

    ChangeKeyWordsStep2(message)
def ChangeKeyWordsStep2(message):
    global i
    global results

    for i in results:
        bot.send_message(message.chat.id,"Редактирумая кнопка" + "<"+str(cursorConnectionAndRead("SELECT text FROM buttons WHERE id='%s'" %i)[0][0])+">")
        bot.register_next_step_handler(message,ChangeKeyWordsStep3)
        del results[0]
        break
def ChangeKeyWordsStep3(message):
    global i
    try:
        i = i[0]
    except:
        print("'i' is already int")

    cursorConnectionAndUpdate("buttons","text", message.text, "id", i)
    if results == []:
        bot.send_message(message.chat.id,"Вы поменяли текст в кнопках")
        adminRights(message)
    ChangeKeyWordsStep2(message)


def ChangeQuestionsStep2(message):
    global i   #попытаться убрать этот костыль и разобраться с bot.register_next_ste_handler(может ли быть три аргумента)
    global results


    for i in results:
        print(cursorConnectionAndRead("SELECT questionTEXT FROM First_4_questions WHERE questionID=%s" % i))
        bot.send_message(message.chat.id,"Редактируемый вопрос" + "<"+str(cursorConnectionAndRead("SELECT questionTEXT FROM First_4_questions WHERE questionID=%s" %i)[0][0])+">")
        bot.register_next_step_handler(message,ChangeQuestionStep3)
        del results[0]
        print (results)
        break







def ChangeQuestionStep3(message):
    global i
    try:
        i = i[0]
    except:
        print("'i' is already int")

    cursorConnectionAndUpdate("First_4_questions", "questionTEXT", message.text, "questionID", i)
    if results == []:
        bot.send_message(message.chat.id,"Вы поменяли текст вопросов при регистрациии")
        adminRights(message)
    ChangeQuestionStep2(message)



def ChangeQuestions(message):
    global results
    global myArray

    bot.send_message(message.chat.id,'Вы выбрали функцию"изменить "вопросы"" тперь вы можете изменить вопросы при регистрации пользователя.'
                                     'Вам по очереди будет выведен текст каждого вопроса, если вы захотите изменить его то просто отпрвьте текст с новым вопросом')

    results = cursorConnectionAndRead("SELECT questionID FROM First_4_questions")

    ChangeQuestionStep2(message)

def ChangeText(message):
    global results
    bot.send_message(message.chat.id,"Редактируемый текст" + "<"+str(cursorConnectionAndRead("SELECT text FROM greetings")[0][0]+">"))
    bot.register_next_step_handler(message, ChangeTextStep2)
def ChangeTextStep2(message):
    cursorConnectionAndUpdate("greetings", "text", message.text, "id", 1)
    bot.send_message(message.chat.id, "Вы поменяли текст при регистрации")
    adminRights(message)
def Developments(message):
    print("4")

def GroupMembers(message):
    print("5")

def Vacancies(message):
    print("6")




















if __name__=='__main__':
    bot.polling(none_stop = True)


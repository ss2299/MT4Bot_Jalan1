# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import EncryptedInfo
from MT4Hook import MT4Hook
from EncryptedInfo import EcryptedInfo
import datetime
import os, time
import telegram
import pyautogui


def checkWords(data, target):
    with open(data, 'r', encoding='UTF8') as file:
        text = file.read()

        if target in text:
            flag = True
        else:
            flag = False

    return flag


def writeWords(data, target):
    with open(data, 'a+', encoding='UTF8') as file:
        file.write(target)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'{name}')  # Press Ctrl+F8 to toggle the breakpoint.

    MT4 = MT4Hook()
    MT4.ConnectApp("FxPro")

    eni = EncryptedInfo.EcryptedInfo()

    tempTime = ''
    tempMsg = ''
    listTexts = []
    tempList = []
    filename = 'MT4log'
    ext = 'txt'

    bot = telegram.Bot(token=eni.getToken())

    while True:
        try:

            # Loop Timer
            time.sleep(2)

            # Check listview contents is updated
            if MT4.getListTexts("SysListView32") != listTexts:
                listTexts = MT4.getListTexts("SysListView32")

                # 임시 리스트를 이용해서 파일 저장 내용 만들기
                templist = listTexts.copy()
                templist.remove('List1')

                # Current date for filename
                filename = 'MT4log'
                ext = 'txt'
                today = datetime.date.today().strftime('%y%m%d')

                # Current date for make directory
                output_save_folder_path = './log/'
                output_path = os.path.join(output_save_folder_path, time.strftime('%Y%m', time.localtime(time.time())))

                if not os.path.exists(output_save_folder_path):
                    os.mkdir(output_save_folder_path)
                if not os.path.exists(output_path):
                    os.mkdir(output_path)

                filename = f"./{output_path}/{filename}-{today}.{ext}"

                # If there is no file then make blank new file
                if not os.path.isfile(filename):

                    with open(filename, 'w') as file:
                        pass

                # Handling list view contents
                for i in range(len(templist)):
                    # Time info
                    if i % 2 == 0:
                        tempTime = templist[i]

                    # Message Contents
                    if i % 2 == 1:
                        tempMsg = templist[i]
                        mergeMsg = f"{tempTime} , {tempMsg} \n"


                        # If there is no message in the log file
                        if not checkWords(filename, mergeMsg):
                            writeWords(filename, mergeMsg)

                            print(f"[Logging Success] {mergeMsg}")
                            bot.sendMessage(chat_id=eni.getChannelid('20K'), text=mergeMsg)
                            # bot.sendMessage(chat_id=eni.getChannelid('GoldenLine_Jalan1'), text=mergeMsg)

                            # Send Message with interval
                            time.sleep(1)



        except Exception:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{now}] It is watching MT4')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Hi MT4, im telegram bot.')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

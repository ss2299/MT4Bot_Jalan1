# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import EncryptedInfo
from MT4Hook import MT4Hook
from EncryptedInfo import EcryptedInfo
import time
import os
import telegram




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
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    MT4 = MT4Hook()
    MT4.ConnectApp("FxPro")

    eni = EncryptedInfo.EcryptedInfo()

    tempTime = ''
    tempMsg = ''
    listTexts = []
    tempList = []
    filename = 'MT4log.txt'

    bot = telegram.Bot(token=eni.getToken())

    while True:
        try:

            # 리스트 뷰의 내용이 변경되었는지 확인
            if MT4.getListTexts("SysListView32") != listTexts:
                listTexts = MT4.getListTexts("SysListView32")

                # 임시 리스트를 이용해서 파일 저장 내용 만들기
                templist = listTexts.copy()
                templist.remove('List1')

                if not os.path.isfile((filename)):
                    with open(filename, 'w') as file:
                        pass


                for i in range(len(templist)):
                    if i % 2 == 0:
                        tempTime = templist[i]

                    if i % 2 == 1:
                        tempMsg = templist[i]
                        mergeMsg = f"{tempTime} , {tempMsg} \n"

                        if not checkWords(filename, mergeMsg):
                            writeWords(filename, mergeMsg)
                            print(f"[Logging Success] {mergeMsg}")
                            bot.sendMessage(chat_id=eni.getChannelid(), text=mergeMsg)


        except Exception:
            now = time.localtime()
            print(f'[{now.tm_year}/{now.tm_mon}/{now.tm_mday} {now.tm_hour}:{now.tm_min}:{now.tm_sec}] It is watching MT4')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Hi MT4, im telegram bot.')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

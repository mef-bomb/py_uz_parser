from parser1 import find_tickets
import winsound
import time

def get_trains():
    trains = find_tickets('24.06.2016')
    for train in trains:
        if not (train['num'] == '732К' or train['num'] == '736К'):
            winsound.MessageBeep()
        print(train['num'])
    # if len(trains) > 1:
    #     winsound.MessageBeep()
    #     print('uspeh')

i = 0
while True:
    i += 1
    print("cycle #{}".format(i))
    try:
        get_trains()
    except:
        print("one more attempt")
    time.sleep(10)

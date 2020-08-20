from lcuapi import LCU, Event, EventProcessor
import ctypes, sys
import time
from multiprocessing.pool import ThreadPool
import json




def run_as_admin(argv=None, debug=False):
    shell32 = ctypes.windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True

    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = map(str, argv[1:])
    else:
        arguments = map(str, argv)
    argument_line = u' '.join(arguments)
    executable = str(sys.executable)
    if debug:
        print('Command line: ', executable, argument_line)
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None

# EventProcessors are classes that handle/process different events.
# Create an EventProcessor by inherenting from the EventProcessor class.
# You then have to define two methods, "can_handle" and "handle".
class PrintSomeEventInfo(EventProcessor):

    # The "can_handle" method must return True and False.
    # Return True if this event handler can handle the event. Return False if not.
    def can_handle(self, event: Event):        
        if issubclass(event.__class__, Event):
            return True
        else:
            return False

    # The "handle" method defines the functionality of the handler.
    # This is where you write code to do something with the event.
    # In this example, I simply print out the URI of the event and the time at which it was created.
    # The only other attribute of an Event is: "event.data".
    def handle(self, event: Event):
        print(f"Event<uri={event.uri} created={event.created}>")
        print("DATA")
        print(f"{event.data}")
        print("=================================================")
'''
class champion:
    def __init__(self, name, key):
        self.name = name
        self.key = key
'''

def queue(lcu):
    lcu.post('/lol-lobby/v2/lobby/matchmaking/search')

def awaitAccept(lcu):
    global _Auto_Accept_On
    while True:
        if not _Auto_Accept_On:
            break
        #print('Queueing...')
        try:
            if lcu.get('/lol-gameflow/v1/gameflow-phase') == 'ReadyCheck':
                queued = lcu.get('/lol-matchmaking/v1/ready-check')
                if queued['state'] == 'InProgress' and queued['playerResponse'] == 'None':
                    lcu.post('/lol-matchmaking/v1/ready-check/accept')
        except Exception as e:
            print(e, type(e))
        time.sleep(1)

def create_lobby(lcu):
    _data = {"queueId" : 430}
    print(type(_data))
    try:
        response = lcu.post('/lol-lobby/v2/lobby', data=json.dumps(_data))
        print('Response', response)
    except Exception as e:
        print(e, type(e))

def change_region(lcu):
    data = {'locale': 'en_US', 'region': 'TW'}
    try:
        response = lcu.post('/riotclient/set_region_locale', data)
        print('Response', response)
    except Exception as e:
        print(e, type(e))

def report(lcu, friends):
    try:
        got = lcu.get('/lol-end-of-game/v1/eog-stats-block')
        gameID = got['gameId']
        teams = got['teams']
        for team in teams:
            for player in team['players']:
                if player['summonerId'] not in friends:
                    _report = {
                        "comment": "Useless AF",
                        "gameId": gameID,
                        "offenses": "Negative Attitude",
                        "reportedSummonerId": player['summonerId']
                    }
                    response = lcu.post('/lol-end-of-game/v2/player-complaints', json.dumps(_report))
                    print(player['summonerId'], player['summonerName'], 'is reported')
                    print(response)
    except Exception as e:
        print(e, type(e))

def search(users, name):
    for user in users:
        if users[user] == name:
            return user
    return -1

def championIdof(champs, championname):
    for champ in champs:
        if champs[champ] == championname:
            return champ
    return -1

def mastery_Id(lcu, Id, champs, championId = 0):
    try:
        mastery = lcu.get('/lol-collections/v1/inventories/' + str(Id) + '/champion-mastery')
        detail = lcu.get('/lol-summoner/v2/summoners?ids=%5B' + str(Id) + '%5D')
        print(detail[0]['displayName'])
        if championId == 0:
            for c in mastery:
                print('Name:%15s Mastery:%d Points:%7d' % (champs[c['championId']], c['championLevel'], c['championPoints']))
        else:
            for c in mastery:
                if c['championId'] == championId:
                    print('Name:%s Mastery:%d Points:%7d' % (champs[c['championId']], c['championLevel'], c['championPoints']))  
    except Exception as e:
        print(e, type(e))            

def check(lcu, champs, num, myTeam, championname = 'all'):
    try:
        if championname == 'all':
            championId = 0
        else:
            championId = championIdof(champs, championname)
        if num > 0 and num < 6:
            player = myTeam[num - 1]
            mastery_Id(lcu, player, champs, championId)
        else:
            for player in myTeam:
                mastery_Id(lcu, player, champs)
            
    except Exception as e:
        print(e, type(e))

def main():
    global _Auto_Accept_On
    # Create the LCU object.
    lcu = LCU()

    # Multiprocessing pool
    pool = ThreadPool(num_of_process)
    
    # Attach any event processors that we want to use to handle events.
    # You can also pass the event processors into the LCU object when you create it on the previous line.
    #lcu.attach_event_processor(PrintSomeEventInfo())
    
    lcu.wait_for_client_to_open()
    lcu.wait_for_login()

    # Open a background thread and listen for + process events using the EventProcessors that were attached to the LCU.
    #lcu.process_event_stream()

    # Here is an example request to get data from the LCU.
    # finished = lcu.get('/lol-platform-config/v1/initial-configuration-complete')
    # print("Has the client finished it's starting up?", finished)
    # if finished:
    #     lcu.post('/process-control/v1/process/quit')
    #     ctypes.windll.user32.MessageBoxW(0, "You should not play this game", "Riot Garbage", 1)
    
    #preprocessing 
    users = {}
    tmp = lcu.get('/lol-chat/v1/friends')
    friends = []
    for friend in tmp:
        friends.append(friend['summonerId'])
        users[friend['summonerId']] = friend['name']  
    me = lcu.get('/lol-chat/v1/me')
    friends.append(me['summonerId'])
    users[me['summonerId']] = me['name']

    #preprocessing champions
    with open('champion.json', encoding='utf-8') as cjs:
        champions = json.load(cjs)
    #champs will be a list containing champions name and their key in lexicological order
    champs = {}
    for c in champions['data']:
        champs[int(champions['data'][c]['key'])] = champions['data'][c]['name']

    

    #main
    task = input('What should we do now?')
    while(task != ' '):
        if task == 'queue':
            queue(lcu)
        elif task == 'accept':
            print('Accept Mode until Queued')
            while True:
                queued = lcu.get('/lol-matchmaking/v1/ready-check')
               # print(queued)
                if queued['state'] == 'InProgress':
                    lcu.post('/lol-matchmaking/v1/ready-check/accept')
                time.sleep(1)
        elif task == 'toggle':
            if _Auto_Accept_On:
                print('Auto accept is now off')
                _Auto_Accept_On = False
                pool.terminate()
                pool.join()
            else:
                print('Auto accept is now on')
                _Auto_Accept_On = True
                pool = ThreadPool(num_of_process)
                pool.apply_async(awaitAccept, (lcu,))
        elif task == 'create':
            create_lobby(lcu)
        elif task == 'change':
            change_region(lcu)
        elif task == 'report':
            report(lcu, friends)
        elif task == 'list':
            for f in friends:
                print(f)
        elif task == 'spam':
            play_msg = {
                'summonerName' : 'ù還是不愛認錯',
                'message' : 'hello'
            }
            for i in range(300):
                play_msg['message'] = '彥棻'
                lcu.post('/lol-game-client-chat/v1/instant-messages', play_msg)
                time.sleep(1)
            print('sended')
        elif task[0:5] == 'check':
            _check = task.split(' ')
            if len(_check) == 1:
                num = 0
                champname = 'all'
            elif len(_check) == 2:
                champname = 'all'
            else:
                num = int(_check[1])
                champname = _check[2]
            if num < 0 or num > 6:
                print('Error, the num should be within 0 to 5, 0 for all players')
            try:
                session = lcu.get('/lol-champ-select/v1/session')
                myTeam = []
                for p in session['myTeam']:
                    myTeam.append(p['summonerId'])
            except Exception as e:
                print(e, type(e))
            #print(myTeam)
            check(lcu, champs, num, myTeam, champname)
        elif task[0:7] == 'mastery':
            _mastery = task.split(' ')
            id = search(users, _mastery[1])
            mastery_Id(lcu, id, champs)
        elif task[0:8] == 'champion':
            _champion = task.split(' ')
            print(championIdof(champs, _champion[1]))
        elif task == 'AR':
            session = lcu.get('/lol-champ-select/v1/session')
            myTeam = []
            for p in session['myTeam']:
                #print(p['summonerId'], p['championId'])
                mastery_Id(lcu, p['summonerId'], champs, championId=int(p["championId"]))
        elif task == 'quit' or task == 'exit':
            break
        elif task[0:3] == 'GET':
            _get = task[4:]
            print(lcu.get(_get))
        elif task[0:4] == 'POST':
            _post = task.split(' ')
            respose = lcu.post(_post[1], _post[2])
            print(respose)
        elif task[0:6] == 'DELETE':
            _delete = task[4:]
            print(lcu.delete(_delete))
        task = input('What should we do now?')

    # Prevent this program from exiting so that the event stream continues to be read.
    # Press Ctrl+C (and wait for another event to get triggered by the LCU) to gracefully terminate the program.
    #lcu.wait()


if __name__ == '__main__':
    ret = run_as_admin()
    if ret is True:
        main()
        

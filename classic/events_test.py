import re
from enum import IntEnum
import requests


R1 = re.compile(r'TAG_CHANGE Entity=\[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) player=(\d*)] '
                r'tag=(.*) value=(.*)')
R2 = re.compile(r'FULL_ENTITY - Updating \[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) '
                r'player=(\d*)] CardID=(.*)')
R3 = re.compile(r'FULL_ENTITY - Creating ID=(\d*) CardID=(.*)')
R4 = re.compile(r'tag=(.*) value=(.*)')
R5 = re.compile(r'SUB_SPELL_START - SpellPrefabGUID=(.*) Source=(\d*) TargetCount=(\d*)')
R6 = re.compile(r'Targets\[0] = \[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) player=(\d*)]')
R7 = re.compile(r'Source = \[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) player=(\d*)]')
R8 = re.compile(r'Player EntityID=(\d*) PlayerID=(\d*) GameAccountId=\[hi=(\d*) lo=(\d*)]')
R9 = re.compile(r'TAG_CHANGE Entity=(.*) tag=(.*) value=(.*)')
R10 = re.compile(r'PlayerID=(.*), PlayerName=(.*)')
R11 = re.compile(r'id=(.*) Player=(.*) TaskList=(.*) ChoiceType=(.*) CountMin=(.*) CountMax=(.*)')
R12 = re.compile(r'HIDE_ENTITY - Entity=\[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) player=(\d*)] '
                 r'tag=(.*) value=(.*)')
R13 = re.compile(r'SHOW_ENTITY - Updating Entity=\[entityName=(.*) id=(\d*) zone=(.*) zonePos=(\d*) cardId=(.*) '
                 r'player=(\d*)] CardID=(.*)')
R14 = re.compile(r'SHOW_ENTITY - Updating Entity=(\d*) CardID=(.*)')
R15 = re.compile(r'HIDE_ENTITY - Entity=(\d*) tag=(.*) value=(.*)')
R16 = re.compile(r'BLOCK_START BlockType=(\w+) Entity=(\S+)')

class T(IntEnum):
    NONE = 0
    GAME = 1
    GAME_ = 2
    PLAYER = 3
    PLAYER_ = 4
    CREATE = 5
    CREATE_ = 6
    UPDATE = 7
    UPDATE_ = 8
    CHANGE = 9
    CHANGE_ = 10
    HIDE = 11
    HIDE_ = 12




def lines_handler(lines):
    info = []
    players = {}
    name2eid = {}
    last_item = None
    complete = False
    for line in lines:
        # s_head = line[0]
        s_time = line[2:10]
        line0 = line[19:].strip()
        if '() - ' in line0:
            source, info0 = line0.split('() - ', 1)
            info1 = info0.strip()
            if source == 'GameState.DebugPrintPower' or source == 'PowerTaskList.DebugPrintPower':
                if last_item is not None:
                    if info1.startswith('tag='):
                        _tag, value = info1.split(' value=', 1)
                        last_item[5].append((_tag[4:], value))
                        continue
                    info.append(last_item)
                    last_item = None
                if info1.startswith('GameEntity'):
                    last_item = (1, '', source, T.GAME if source[0] == 'G' else T.GAME_, s_time, [])
                elif info1.startswith('Player'):
                    result = R8.match(info1)
                    last_item = (int(result.group(1)), '', source,
                                 T.PLAYER if source[0] == 'G' else T.PLAYER_, s_time,
                                 [('PlayerID', result.group(2)),
                                  ('hi', result.group(3)),
                                  ('lo', result.group(4))])
                elif info1.startswith('FULL_ENTITY - Creating'):
                    result = R3.match(info1)
                    last_item = (int(result.group(1)), result.group(2), source,
                                 T.CREATE if source[0] == 'G' else T.CREATE_, s_time, [])
                elif info1.startswith('FULL_ENTITY - Updating'):
                    result = R2.match(info1)
                    name2eid[result.group(1)] = result.group(2)
                    last_item = (int(result.group(2)), result.group(7), source,
                                 T.UPDATE if source[0] == 'G' else T.UPDATE_, s_time, [])
                elif info1.startswith('SHOW_ENTITY - Updating'):
                    result = R13.match(info1)
                    if result:
                        name2eid[result.group(1)] = result.group(2)
                        last_item = (int(result.group(2)), result.group(7), source,
                                     T.UPDATE if source[0] == 'G' else T.UPDATE_, s_time, [])
                    else:
                        result = R14.match(info1)
                        last_item = (int(result.group(1)), result.group(2), source,
                                     T.UPDATE if source[0] == 'G' else T.UPDATE_, s_time, [])
                elif info1.startswith('TAG_CHANGE'):
                    result = R1.match(info1)
                    if result:
                        last_item = (int(result.group(2)), result.group(5), source,
                                     T.CHANGE if source[0] == 'G' else T.CHANGE_,
                                     s_time, [(result.group(7), result.group(8))])
                    else:
                        result = R9.match(info1)
                        _gameentity = result.group(1)
                        if _gameentity == 'GameEntity':
                            eid = 1
                            if result.group(2) == 'STATE' and result.group(3) == 'COMPLETE':
                                complete = True
                        elif _gameentity.isdigit():
                            eid = int(_gameentity)
                        elif _gameentity in name2eid:
                            eid = int(name2eid[_gameentity])
                        elif _gameentity in players:
                            eid = int(players[_gameentity]) + 1  
                        else:
                            eid = 0
                        last_item = (eid, '' if eid > 0 else _gameentity, source,
                                     T.CHANGE if source[0] == 'G' else T.CHANGE_,
                                     s_time, [(result.group(2), result.group(3))])
                elif info1.startswith('HIDE_ENTITY'):
                    result = R12.match(info1)
                    if result:
                        last_item = (int(result.group(2)), result.group(5), source,
                                     T.CHANGE if source[0] == 'G' else T.CHANGE_,
                                     s_time, [(result.group(7), result.group(8))])
                    else:
                        result = R15.match(info1)
                        last_item = (int(result.group(1)), '', source,
                                     T.CHANGE if source[0] == 'G' else T.CHANGE_,
                                     s_time, [(result.group(2), result.group(3))])
                elif info1.startswith('BLOCK_START'):
                    info.append("BLOCK_START")
                elif info1.startswith('BLOCK_END'):
                    info.append("BLOCK_END")
                elif info1.startswith('CREATE_GAME'):
                    info.append("CREATE_GAME")
                    if complete:
                        info.append("CREATE_GAME_COMPLETE")
                        complete = False
                else:
                    ...
            elif source == 'GameState.DebugPrintGame':
                if info1.startswith('PlayerID='):
                    result = R10.match(info1)
                    players[result.group(2)] = result.group(1)
            elif source == 'GameState.DebugPrintEntityChoices':
                if info1.startswith('id='):
                    result = R11.match(info1)
                    players[result.group(2)] = result.group(1)
            elif source == 'PowerTaskList.DebugPrintPower':
                ...
            else:
                ...
    return info
def lines_parser(lines,cards):
    logs = lines_handler(l)
    with open(f'out.txt','w') as f:
        for log in logs:
            f.write(str(log)+"\n")
            if log[1] == '':
                continue
            else:
                for card in cards:
                    if card['id'] == log[1]:
                        f.write(str(card['name'])+"\n")
                        print(card['name'])
                        break
link = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.json'
cards = requests.get(link).json()
#print(cards[0:10])  
l = []
with open("Power.log") as f:
    for line in f:
        #print(line)
        l.append(line)
    with open(f'orginal.txt','w') as org:
        for line in l:
            org.write(str(line)+"\n")
    lines_parser(l,cards)

        


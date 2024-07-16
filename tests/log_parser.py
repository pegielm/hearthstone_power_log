import re
import json
import requests

def get_card_names(url="https://api.hearthstonejson.com/v1/latest/enUS/cards.json"):
    cards_dict = requests.get(url)
    cards_dict.raise_for_status()
    return cards_dict.json()

def card_code_to_name(cardnames,card_id):
    for card in cardnames:
        if card["id"]==card_id:
            return card["name"]
    return "-"

def print_players(entity_list):
    players_keys = []
    for entity in entity_list:
        try:
            _ = entity_list[entity]["tags"]["HERO_ENTITY"]
            players_keys.append(entity_list[entity]["ID"])
        except KeyError:
            ...
    print("------------------------------------")
    for p in players_keys:
        try:
            v = entity_list[p]["tags"]["NUM_TURNS_IN_PLAY"]
            print(f"{p} {v}")
        except KeyError:
            ...

def get_hero(entity_id,entity_list):
    try:
        card_type = entity_list[entity_id]["tags"]["CARDTYPE"]
        if card_type == "HERO":
            return entity_list[entity_id]["CardID"]
    except Exception:
        return None
    return None
    



def parse_lines(logs):
    cardnames = get_card_names()
    i = 0
    current_block = ""
    entity_list = {}
    entity_id = 0
    games = []
    block_started = False
    block_type = ""
    leaderboard = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #so long for duo
    players_heroes = {}
    for log in logs:
        try:
            meta,data = log.split("() - ")
            d,timestamp,source = meta.split(" ")
            debug = source.split(".")[1]
            if debug != "DebugPrintPower":
                continue
            data_stripped = data.lstrip()
            indent = len(data)-len(data_stripped)
            if True:
                log_type = data_stripped.split(" ")[0]

                if log_type.startswith("tag="):
                    if current_block=="FULL_ENTITY - Creating":
                        pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                        match = re.search(pattern, data_stripped)
                        if match:
                            tag = match.group(1)
                            value = match.group(2)
                            #print(f"Tag: {tag}, Value: {value}")
                        else:
                            raise Exception("bad tag")
                        entity_list[entity_id]["tags"][tag] = value
                    elif current_block=="FULL_ENTITY - Updating":
                        pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                        match = re.search(pattern, data_stripped)
                        if match:
                            tag = match.group(1)
                            value = match.group(2)
                            #print(f"Tag: {tag}, Value: {value}")
                        else:
                            raise Exception("bad tag")
                        entity_list[entity_id]["tags"][tag]=value
                    elif current_block=="SHOW_ENTITY":
                        pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                        match = re.search(pattern, data_stripped)
                        if match:
                            tag = match.group(1)
                            value = match.group(2)
                            #print(f"Tag: {tag}, Value: {value}")
                        else:
                            raise Exception("bad tag")
                        entity_list[entity_id]["tags"][tag]=value
                        
                elif log_type.startswith("Targets"):
                    current_block="Source"
                elif log_type.startswith("Source"):
                    current_block="Targets"
                elif log_type.startswith("Info"):
                    current_block="Info"
                elif log_type == "GameEntity":
                    current_block = "GameEntity"
                elif log_type == "Player":
                    current_block = "Player"
                elif log_type == "CREATE_GAME\n":
                    current_block = "CREATE_GAME"
                    try:
                        if entity_list["GameEntity"]["tags"]["STATE"]=="COMPLETE":
                            games.append(entity_list)
                            with open(f"{len(games)}.json", 'w') as jf:
                                json.dump(entity_list,jf, indent=4)
                            current_block = ""
                            entity_list = {}
                            entity_id = 0
                            games = []
                    except KeyError:
                        ...
                elif log_type == "BLOCK_START":
                    current_block = "BLOCK_START"
                    block_started = True
                    match = re.search(r'BlockType=(\w+).*?id=(\d+)', data_stripped)
                    if match:
                        block_type = match.group(1)
                        entity_id = match.group(2)
                    else:
                        continue

                    if block_type == "ATTACK":
                        hero = get_hero(entity_id,entity_list)
                        if hero != None:
                            print("ATK",hero)
                elif log_type == "BLOCK_END\n":
                    current_block = "BLOCK_END"
                    if block_started:
                        ...
                elif log_type == "FULL_ENTITY":
                    if data_stripped.split(" ")[2] == "Updating":
                        current_block = "FULL_ENTITY - Updating"
                        match = re.search(r'id=(\d+)', data_stripped)
                        if match:
                            entity_id=match.group(1)
                        else:
                            raise Exception("bad updating")
                        
                    elif data_stripped.split(" ")[2] == "Creating":
                        current_block = "FULL_ENTITY - Creating"
                        pattern = r"FULL_ENTITY - Creating ID=(\d+)(?:\s+CardID=([\w_]+))?"
                        match = re.search(pattern,data_stripped)
                        if match:
                            entity_id = match.group(1)
                            card_id = match.group(2)
                            #print(f"ID: {entity_id}, CardID: {card_id}")
                        else:
                            raise Exception("bad creating")
                        entity_list[entity_id] = {"ID": entity_id, "CardID": card_id, "tags": {}}
                elif log_type == "SHOW_ENTITY":
                    current_block = "SHOW_ENTITY"
                    if data_stripped.split(" ")[2] == "Updating":
                        match = re.search(r'id=(\d+)', data_stripped)
                        if match:
                            entity_id=match.group(1)
                        else:
                            match = re.search(r'Entity=(\d+)', data_stripped)
                            if match:
                                entity_id=match.group(1)
                            else:
                                raise Exception("bad show updating")
                    else:
                        raise Exception("no updating in show entity")

                elif log_type == "HIDE_ENTITY":
                    current_block = "HIDE_ENTITY"
# TAG CHANGE ----------------------------------------------
                elif log_type == "TAG_CHANGE":
                    current_block = "TAG_CHANGE"
                    match = re.search(r'id=(\d+)', data_stripped)
                    if match:
                        entity_id=match.group(1)
                    else:
                        match = re.search(r'Entity=([^ ]+)', data_stripped)
                        if match:
                            entity_id=match.group(1)
                        else:
                            raise Exception("bad tag change")
                    pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                    match = re.search(pattern, data_stripped)
                    if match:
                        tag = match.group(1)
                        value = match.group(2)
                        #print(f"Tag: {tag}, Value: {value}")
                    else:
                        raise Exception("bad tag")
                    if entity_id not in entity_list:
                        entity_list[entity_id] = {"ID": entity_id, "tags":{}}
                    entity_list[entity_id]["tags"][tag]=value

                    if tag == "PLAYER_LEADERBOARD_PLACE" and value!="0":
                        hero = entity_list[entity_id]["CardID"]
                        
                        #print("L",entity_id,value,hero)
                        try:
                            leaderboard[int(value)] = hero
                        except Exception:
                            pass
                        #print(leaderboard)
                    if tag == "HERO_ENTITY":
                        print("HERO",entity_id,value)
                        if value != "62":
                            players_heroes[entity_id] = entity_list[value]["CardID"]
                    if tag == "PLAYSTATE":
                        try:
                            print("PLAY",entity_id,value,entity_list[entity_id]["tags"]["HERO_ENTITY"])
                        except KeyError:
                            print("! P ERROR",entity_id,value)
                    if tag == "NUM_TURNS_IN_PLAY":
                        try:
                            hero = entity_list[entity_id]["tags"]["HERO_ENTITY"]
                            print("TURN",entity_id,value)
                        except Exception:
                            pass
                    if tag=="DAMAGE":
                        try:
                            check = entity_list[entity_id]["tags"]["PLAYER_LEADERBOARD_PLACE"]
                            hero = entity_list[entity_id]["CardID"]
                            print("DMG",hero,entity_id,value)
                        except Exception:
                            pass
                    if tag=="STATE" and entity_id=="GameEntity":
                        print("GAME STATE:",value)
                    
# TAG CHECK END ---------------------------------------
                elif log_type == "META_DATA":
                    current_block = "META_DATA"
                elif log_type == "SUB_SPELL_START":
                    current_block = "SUB_SPELL_END"
                elif log_type == "SUB_SPELL_END\n":
                    current_block = "SUB_SPELL_END"
                elif log_type == "SHUFFLE_DECK":   #normalny hs
                    current_block = "SHUFFLE_DECK"
                elif log_type == "CHANGE_ENTITY":
                    current_block = "CHANGE_ENTITY"
                else:
                    raise Exception("not implemented ",log_type)
                #print(indent,current_block)
                
            i+=1
            if i % 1000 == 0:
                #print_players(entity_list)
                pass
        except ValueError as e:
            if "values to unpack" in str(e):
                pass
            else:
                raise e
        except Exception as e:
            raise e
    print_players(entity_list)
    leaderboard_with_names = [card_code_to_name(cardnames,i) for i in leaderboard]
    print(leaderboard_with_names)
    players_heroes_with_names = {key: card_code_to_name(cardnames,value) for key, value in players_heroes.items()}
    print(players_heroes_with_names)
    print("FINAL LEADERBOARD")
    for i in leaderboard_with_names:
        if i != "-":
            hero = i
            for key,value in players_heroes_with_names.items():
                if value == hero:
                    player = key
                    break
            print(leaderboard_with_names.index(i),hero,player)
    with open("entity_list.json", 'w') as jf:
        json.dump(entity_list,jf, indent=4)
    games.append(entity_list)

    
    return games
    

if __name__ == "__main__":
    print("PROGRAM START ----------------------------")
    print("****************************************")
    logs = []
    power_log_path = "Power_bg.log"
    #power_log_path = "test.log" #path to power.log
    with open(power_log_path, 'r') as f:
        for line in f:
            #print(line)
            logs.append(line)
    g = parse_lines(logs)
    with open("final.json", 'w') as final:
        json.dump(g,final, indent=4)
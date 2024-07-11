import re
import json
def parse_lines(logs):
    i = 0
    current_block = ""
    entity_list = {}
    entity_id = 0
    games = []
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
                elif log_type == "BLOCK_END\n":
                    current_block = "BLOCK_END"
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
            if i == 202:
                #break
                pass
        except ValueError as e:
            if "values to unpack" in str(e):
                pass
            else:
                raise e
        except Exception as e:
            raise e
    
    with open("entity_list.json", 'w') as jf:
        json.dump(entity_list,jf, indent=4)
    games.append(entity_list)
    return games
    

if __name__ == "__main__":
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
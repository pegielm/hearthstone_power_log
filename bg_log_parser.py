import re
import json
import requests


class parser:
    def __init__(self, log_path="Power.log"):
        self.log_path = log_path
        self.cardnames = self.get_card_names()
        self.games = []

        self.player = ""
        self.entity_list = {}
        self.leaderboard = [0] * 17
        self.players_heroes = {}

        self.current_block = ""
        self.entity_id = 0
        self.block_started = False
        self.block_type = ""
        
    @staticmethod
    def get_card_names(url="https://api.hearthstonejson.com/v1/latest/enUS/cards.json"):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def card_code_to_name(self, card_id):
        for card in self.cardnames:
            if card["id"] == card_id:
                return card["name"]
        return None
    
    def print_players(self):
        players_keys = [entity["ID"] for entity in self.entity_list.values() if "HERO_ENTITY" in entity.get("tags", {})]
        
        print("------------------------------------")
        for p in players_keys:
            try:
                v = self.entity_list[p]["tags"]["NUM_TURNS_IN_PLAY"]
                print(f"{p} {v}")
            except KeyError:
                pass
    
    def get_hero(self):
        try:
            if self.entity_list[self.entity_id]["tags"]["CARDTYPE"] == "HERO":
                return self.entity_list[self.entity_id]["CardID"]
        except KeyError:
            return None
        return None
    
    def reset_game(self):
        self.entity_list = {}
        self.leaderboard = [0] * 17
        self.players_heroes = {}

        self.current_block = ""
        self.entity_id = 0
        self.block_started = False
        self.block_type = ""
        
    def parse_line(self,log):
        try:
            meta, data = log.split("() - ")
            d, timestamp, source = meta.split(" ")
            debug = source.split(".")[1]
            if debug != "DebugPrintPower":
                return
            data_stripped = data.lstrip()
            indent = len(data) - len(data_stripped)
            log_type = data_stripped.split(" ")[0]
            
            if log_type.startswith("tag="):
                pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                match = re.search(pattern, data_stripped)
                if match:
                    tag = match.group(1)
                    value = match.group(2)
                else:
                    raise Exception("bad tag")
                
                if self.current_block in ["FULL_ENTITY - Creating", "FULL_ENTITY - Updating", "SHOW_ENTITY"]:
                    try:
                        self.entity_list[self.entity_id]["tags"][tag] = value
                    except KeyError:
                        pass
            elif log_type.startswith("Targets"):
                self.current_block = "Source"
            elif log_type.startswith("Source"):
                self.current_block = "Targets"
            elif log_type.startswith("Info"):
                self.current_block = "Info"
            elif log_type == "GameEntity":
                self.current_block = "GameEntity"
            elif log_type == "Player":
                self.current_block = "Player"
            elif log_type == "CREATE_GAME\n":
                self.current_block = "CREATE_GAME"
            elif log_type == "BLOCK_START":
                self.current_block = "BLOCK_START"
                self.block_started = True
                match = re.search(r'BlockType=(\w+).*?id=(\d+)', data_stripped)
                if match:
                    self.block_type = match.group(1)
                    self.entity_id = match.group(2)
                else:
                    return
                
                if self.block_type == "ATTACK":
                    hero = self.get_hero()
                    if hero is not None:
                        print("ATK", hero)
            elif log_type == "BLOCK_END\n":
                self.current_block = "BLOCK_END"
            elif log_type == "FULL_ENTITY":
                if data_stripped.split(" ")[2] == "Updating":
                    self.current_block = "FULL_ENTITY - Updating"
                    match = re.search(r'id=(\d+)', data_stripped)
                    if match:
                        self.entity_id = match.group(1)
                    else:
                        raise Exception("bad updating")
                elif data_stripped.split(" ")[2] == "Creating":
                    self.current_block = "FULL_ENTITY - Creating"
                    pattern = r"FULL_ENTITY - Creating ID=(\d+)(?:\s+CardID=([\w_]+))?"
                    match = re.search(pattern, data_stripped)
                    if match:
                        self.entity_id = match.group(1)
                        card_id = match.group(2)
                    else:
                        raise Exception("bad creating")
                    self.entity_list[self.entity_id] = {"ID": self.entity_id, "CardID": card_id, "tags": {}}
            elif log_type == "SHOW_ENTITY":
                self.current_block = "SHOW_ENTITY"
                if data_stripped.split(" ")[2] == "Updating":
                    match = re.search(r'id=(\d+)', data_stripped)
                    if match:
                        self.entity_id = match.group(1)
                    else:
                        match = re.search(r'Entity=(\d+)', data_stripped)
                        if match:
                            self.entity_id = match.group(1)
                        else:
                            raise Exception("bad show updating")
            elif log_type == "HIDE_ENTITY":
                self.current_block = "HIDE_ENTITY"
            elif log_type == "TAG_CHANGE":
                self.current_block = "TAG_CHANGE"
                match = re.search(r'id=(\d+)', data_stripped)
                if match:
                    self.entity_id = match.group(1)
                else:
                    match = re.search(r'Entity=([^ ]+)', data_stripped)
                    if match:
                        self.entity_id = match.group(1)
                    else:
                        raise Exception("bad tag change")
                pattern = r"tag=([^\s]+)\s+value=([^\s]+)"
                match = re.search(pattern, data_stripped)
                if match:
                    tag = match.group(1)
                    value = match.group(2)
                else:
                    raise Exception("bad tag")
                if self.entity_id not in self.entity_list:
                    self.entity_list[self.entity_id] = {"ID": self.entity_id, "tags": {}}
                self.entity_list[self.entity_id]["tags"][tag] = value

                if tag == "PLAYER_LEADERBOARD_PLACE":
                    
                    try:
                        hero = self.entity_list[self.entity_id]["CardID"]
                        self.leaderboard[int(value)] = self.card_code_to_name(hero)
                        with open("leaderboard.txt", 'a') as lf:
                            lf.write(f"{self.leaderboard}\n")
                    except Exception:
                        pass
                if tag == "HERO_ENTITY":
                    print("HERO", self.entity_id, value)
                    if value != "62":
                        try:
                            hero = self.entity_list[value]["CardID"]
                            hero = self.card_code_to_name(hero)
                            if hero != "Bartender Bob":
                                self.players_heroes[self.entity_id] = hero
                        except KeyError:
                            pass
                if tag == "PLAYSTATE":
                    try:
                        print("PLAY", self.entity_id, value, self.entity_list[self.entity_id]["tags"]["HERO_ENTITY"])
                    except KeyError:
                        pass
                        #print("! P ERROR", self.entity_id, value)
                if tag == "NUM_TURNS_IN_PLAY":
                    try:
                        hero = self.entity_list[self.entity_id]["tags"]["HERO_ENTITY"]
                        print(f"TURN, id={self.entity_id}, value={value}")
                    except Exception:
                        pass
                if tag == "DAMAGE":
                    try:
                        check = self.entity_list[self.entity_id]["tags"]["PLAYER_LEADERBOARD_PLACE"]
                        hero = self.entity_list[self.entity_id]["CardID"]
                        print(f"DMG, hero={hero}, id={self.entity_id}, value={value}")
                    except Exception:
                        pass
                if tag == "STATE" and self.entity_id == "GameEntity":
                    print("GAME STATE:", value)
                    if value == "COMPLETE":
                        self.print_results()
                        self.reset_game()
                if tag == "ATTACKING" and value != "0":
                    try:
                        if self.card_code_to_name(self.entity_list[self.entity_id]["CardID"]) != None:
                            print("ATTACKING", self.card_code_to_name(self.entity_list[self.entity_id]["CardID"]),f"{self.entity_list[self.entity_id]["tags"]["ATK"]}/{self.entity_list[self.entity_id]["tags"]["HEALTH"]} dmg={self.entity_list[self.entity_id]["tags"]["DAMAGE"]}")
                    except KeyError:
                        pass
                if tag == "DEFENDING" and value != "0":
                    try:
                        if self.card_code_to_name(self.entity_list[self.entity_id]["CardID"]) != None:
                            print("DEFENDING", self.card_code_to_name(self.entity_list[self.entity_id]["CardID"]),f"{self.entity_list[self.entity_id]["tags"]["ATK"]}/{self.entity_list[self.entity_id]["tags"]["HEALTH"]} dmg={self.entity_list[self.entity_id]["tags"]["DAMAGE"]}")
                    except KeyError:
                        pass
                if tag == "MULLIGAN_STATE":
                    self.player = self.entity_id

            elif log_type == "META_DATA":
                self.current_block = "META_DATA"
            elif log_type == "SUB_SPELL_START":
                self.current_block = "SUB_SPELL_END"
            elif log_type == "SUB_SPELL_END\n":
                self.current_block = "SUB_SPELL_END"
            elif log_type == "SHUFFLE_DECK":
                self.current_block = "SHUFFLE_DECK"
            elif log_type == "CHANGE_ENTITY":
                self.current_block = "CHANGE_ENTITY"
            else:
                raise Exception("not implemented", log_type)
            
        except ValueError as e:
            if "values to unpack" in str(e):
                pass
            else:
                raise e
        except Exception as e:
            raise e
    
    def parse_lines(self, logs):
        for log in logs:
            self.parse_line(log)
        self.games.append(self.entity_list)
        return self.games
    
    def print_results(self):
        if len(self.players_heroes) == 0:
            return
        self.print_players()
        print(self.players_heroes)
        print(self.leaderboard)
        print("FINAL LEADERBOARD")
        print("-------------------------------------------------")
        print(self.player)
        print(self.entity_list[self.player]["tags"]["PLAYSTATE"])
        print("-------------------------------------------------")
        to_print = []
        heroes_players = {value: key for key, value in self.players_heroes.items()}
        place = 1
        for i in self.leaderboard:
            if i == 0:
                continue

            try:
                to_print.append(f"{place}, {heroes_players[i]}, {i}")
            except Exception:
                to_print.append(f"{place}, {i}")
            place += 1
        to_print.sort()
        for i in to_print:
            print(i)
        print("-------------------------------------------------")
        with open("entity_list.json", 'w') as jf:
            json.dump(self.entity_list, jf, indent=4)
        
    
    def test_run(self):
        logs = []
        with open("leaderboard.txt", 'w') as lf:
            pass
        with open(self.log_path, 'r',encoding='utf-8') as f:
            for line in f:
                logs.append(line)
        games = self.parse_lines(logs)
        self.print_results()
        with open("final.json", 'w') as final:
            json.dump(games, final, indent=4)

if __name__ == "__main__":
    parser = parser()
    parser.test_run()

# Hearthstone Power.log documentation and parser.

### Hearthstone Log Structure (Power.log)

Example logs:

```python
D 15:44:29.2000003 GameState.DebugPrintPower() -         TAG_CHANGE Entity=357 tag=1596 value=1 
D 15:44:29.2000003 GameState.DebugPrintPower() -         TAG_CHANGE Entity=357 tag=HAS_ACTIVATE_POWER value=1 
D 15:44:29.2000003 GameState.DebugPrintPower() -         FULL_ENTITY - Creating ID=363 CardID=BG_GVG_085
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=CONTROLLER value=14
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=CARDTYPE value=MINION
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=1196 value=1
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=479 value=1
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=ATK value=1
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=HEALTH value=2
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=EXHAUSTED value=1
D 15:44:29.2000003 GameState.DebugPrintPower() -             tag=ZONE value=PLAY
```

1. **Timestamp**:

   Each log entry starts with a timestamp (e.g., `D 15:43:52.3262200`).

2. **Debug Type**:

   Following the timestamp, the debug type is specified (e.g., `GameState.DebugPrintPowerList()`).

3. **Event Details**:

   Each event type has associated details, often organized in a nested (block) format. For example:
   ```python
      BLOCK_START BlockType=TRIGGER Entity=[entityName=Misfit Dragonling id=4900 zone=PLAY zonePos=5 
          SUB_SPELL_START - SpellPrefabGUID=ReuseFX_Dragon_BuffImpact_Small_Gold_Super_SourceAuto 
                            Source = [entityName=Misfit Dragonling id=4900 zone=PLAY zonePos=5 cardId=BG29_814_G 
                            Targets[0] = [entityName=Misfit Dragonling id=4900 zone=PLAY zonePos=5 cardId=BG29_814_G 
              FULL_ENTITY - Creating ID=4999 CardID=
                  tag=ZONE value=SETASIDE
                  tag=CONTROLLER value=14
                  tag=ENTITY_ID value=4999
              SHOW_ENTITY - Updating Entity=4999 CardID=BG29_814e
                  tag=CONTROLLER value=14
                  tag=CARDTYPE value=ENCHANTMENT
                  tag=TAG_SCRIPT_DATA_NUM_1 value=8
                  tag=PREMIUM value=1
   ```
4. **Log Types**

   The logs contain different types of events, such as:
   - `BLOCK_START` - Start of a block of events
   - `BLOCK_END` - End of a block of events
   - `FULL_ENTITY` - Creation of a new entity
   - `SHOW_ENTITY` - Update of an entity
   - `CHANGE_ENTITY` - Change of an entity's attributes
   - `HIDE_ENTITY` - Removal of an entity (e.g., when it is destroyed)
   - `TAG_CHANGE` - Change of an entity's tag
   - `META_DATA` - More information about event 
   - `CREATE_GAME` - Start of a new game
   - `SUB_SPELL_START` - More complicated game actions
   - `SUB_SPELL_END` - End of it
   

   Also block have own types:
   - `TRIGGER` 
   - `POWER`
   - `PLAY`
   - `ATTACK`
   - `DEATHS`
   - `MOVE_MINION`

   Additionally, there are separate types for Player and Game Entity.
   - Player Entity 
   - Game Entity

5. **Entity Creation**:

   Entities are created with specific IDs and attributes. They are updated throughout the game. Using the 'FULL_ENTITY' block or 'SHOW_ENTITY' or 'TAG_CHANGE' events, the log captures the creation and modification of entities.
      ```python
      FULL_ENTITY - Creating ID=35 CardID=TB_BaconShop_HERO_PH
          tag=CONTROLLER value=6
          tag=CARDTYPE value=HERO
          tag=HEALTH value=30
          tag=ZONE value=PLAY
          tag=ENTITY_ID value=35
      ```
      ```python
      TAG_CHANGE Entity=16 tag=STATE value=RUNNING 
      TAG_CHANGE Entity=17 tag=PLAYSTATE value=PLAYING 
      ```

### Interpreting the Logs

In the code enties are tracked in the form of a dictionary. When some event occurs, the dictionary is updated with the new information. For example, when a new entity is created, the dictionary is updated and new objects are added. When an entity is updated, the dictionary is updated with the new information.

During the game, we can track entities and their attributes and extract useful information.

At the end of the game, the dictionary is converted to json format and saved. This is how example entity looks like:

```json
"262": {
        "ID": "262",
        "CardID": "BG29_611",
        "tags": {
            "CONTROLLER": "6",
            "CARDTYPE": "MINION",
            "TAG_LAST_KNOWN_COST_IN_HAND": "1",
            "479": "1",
            "COST": "1",
            "ATK": "1",
            "HEALTH": "1",
            "ZONE": "REMOVEDFROMGAME",
        }
      }
```







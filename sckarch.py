import re

# Sample line
line = "BLOCK_START BlockType=POWER Entity=[entityName=Corpse Farm id=65 zone=PLAY zonePos=0 cardId=WW_374 player=2] EffectCardId=System.Collections.Generic.List`1[System.String] EffectIndex=0 Target=0 SubOption=-1"
# Regex to extract the required fields
pattern = re.compile(r'BlockType=(\w+) Entity=(\w+)*')

# Search the line with the regex
match = pattern.search(line)

if match:
    # Extract the required fields
    block_type = match.group(1)
    entity = match.group(2)
    print(block_type, entity)

from hslog.parser import LogParser
from hslog.export import EntityTreeExporter
from hearthstone import *

parser = LogParser()
with open("Power.log") as f:
    parser.read(f)

games = parser.games
n = 0
for game in games:
    packet_tree = game

    with open(f'{n}.txt','w') as f:
        for i in packet_tree.recursive_iter():
            f.write(str(i)+"\n")
    n += 1


exporter = EntityTreeExporter(packet_tree)
export = exporter.export()


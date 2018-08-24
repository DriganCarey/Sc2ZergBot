import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.data import race_townhalls

class ZergBot(sc2.BotAI):
	def __init__(self):
		pass

	async def on_step(self, iteration):
		pass

#running the game:
# first parameter is the map
# second parameter is the list of players/bots
# third is whether the game should be in a realtime, or sped up
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZergBot()), Computer(Race.Zerg, Difficulty.Easy)], realtime = True)
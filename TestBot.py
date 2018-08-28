import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.constants import *
from sc2.data import race_gas, race_worker, race_townhalls, ActionResult, Attribute, Race

class TestBot(sc2.BotAI):

	def __init__(self):
		self.ITERATIONS_PER_MINUTE = 165
		self.ITERATIONS_PER_SECOND = 2.75
		self.hatcherys = []
		self.last_variable_update = None

	# ADDING HATCHERY TO MY LIST
	def add_hatchery(self, input_hatch: Unit, matching_queen: Unit = None):
		# zero value is hatchery itself
		# first value is inject queen
		# second value is inject queue
		self.hatcherys.append([input_hatch, matching_queen, []])


	def get_larva(self, hatchery: Unit) -> Units:
		return self.units(LARVA).closer_than(5, hatchery)

	async def on_step(self, iteration):
		if (iteration == 0):
			for hatch in self.units(HATCHERY):
				self.add_hatchery(hatch)
			self.last_variable_update = 0

		if self.time >= self.last_variable_update + 1:
			for hatch in self.hatcherys:
				# if there is a queued inject
				if len(hatch[2]) > 0:
					if hatch[2][0] != 0:
						hatch[2][0] += -1
					else:
						del hatch[2][0]
			self.last_variable_update = self.time


			print("self.time: " + str(self.time))
			print("Larva no: " + str(self.units(LARVA).closer_than(5, self.hatcherys[0][0]).amount))
			print("Inject queue: " + str(self.hatcherys[0][3]))
			


			


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, TestBot()),Computer(Race.Terran, Difficulty.Easy)], realtime=False)
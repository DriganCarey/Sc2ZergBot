import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.constants import *
from sc2.data import race_gas, race_worker, race_townhalls, ActionResult, Attribute, Race

class hatcheryTracker(object):
	def __init__(self, input_hatch: Unit):
		self.hatchery = input_hatch
		self.queen = None
		self.larva_spawn = True
		self.larva_spawn_timer = 11 # seconds
		self.inject_queue = []
		if self.get_larva().amount >= 3:
			self.larva_spawn = False
			self.larva_spawn_timer = -1

	def add_queen(self, matching_queen: Unit):
		self.queen = matching_queen

	@property
	def get_larva(self) -> Units:
		return self.units(LARVA).closer_than(5, self.hatchery)

	def is_larva_spawn(self):
		return self.larva_spawn

	def is_inject_queued(self):
		if len(self.inject_queue) > 0:
			return True
		else:
			return False

	def update_value(self):
		# if there is a queued inject
		if len(self.inject_queue) > 0:
			if self.inject_queue[0] != 0:
				self.inject_queue[0] += -1
			else:
				del self.inject_queue[0]

		if self.larva_spawn:
			if self.larva_spawn_timer != 0:
				self.larva_spawn_timer += -1
			#otherwise a timer has just finished
			# if the larva is more than 3
			elif self.get_larva().amount >= 3:
				self.larva_spawn = False
				self.larva_spawn_timer = -1
			else:
				self.larva_spawn_timer += -1

	async def inject(self):
		if self.queen != None:
			if self.queen.energy >= 25 and self.queen.is_idle and not self.hatchery.has_buff(QUEENSPAWNLARVATIMER):
				await self.do(queen(EFFECT_INJECTLARVA, hatch))
				self.inject_queue.append(29)


class TestBot(sc2.BotAI):

	def __init__(self):
		self.ITERATIONS_PER_MINUTE = 165
		self.ITERATIONS_PER_SECOND = 2.75
		self.hatcherys = []

	# ADDING HATCHERY TO MY LIST
	def add_hatchery(self, input_hatch: Unit, matching_queen: Unit = None):
		larva_spawn = True
		larva_spawn_timer = 11
		if self.units(LARVA).closer_than(5, input_hatch).amount >= 3:
			larva_spawn = False
			larva_spawn_timer = None
		# zero value is hatchery itself
		# first value is whether larva is spawning
		# second value is next larva spawn
		# third value is inject queen
		# fourth value is inject queue
		self.hatcherys.append([input_hatch, larva_spawn, larva_spawn_timer, matching_queen, []])


	def get_larva(self, hatchery: Unit) -> Units:
		return self.units(LARVA).closer_than(5, hatchery)

	async def on_step(self, iteration):
		if (iteration == 0):
			self.add_hatchery(self.units(HATCHERY).random)

		if (iteration%self.ITERATIONS_PER_SECOND == 0):
			for hatch in self.hatcherys:
				# if there is a queued inject
				if len(hatch[4]) > 0:
					if hatch[4][0] != 0:
						hatch[4][0] += -1
					else:
						del hatch[4][0]

				if hatch[1]:
					if hatch[2] != 0:
						hatch[2] += -1
					#otherwise a timer has just finished
					# if the larva is more than 3
					elif self.units(LARVA).closer_than(5, hatch[0]).amount >= 3:
						hatch[1] = False
						hatch[2] = -1
					else:
						hatch[2] += -1
				else:
					if self.units(LARVA).closer_than(5, hatch[0]).amount < 3:
						hatch[1] = True
						hatch[2] = 11


			print("Time: " + str(iteration/self.ITERATIONS_PER_SECOND))
			print("self.time: " + str(self.time))
			print("Larva no: " + str(self.units(LARVA).closer_than(5, self.hatcherys[0][0]).amount))
			print("Is larva spawning: " + str(self.hatcherys[0][1]))
			print("Time remaining: " + str(self.hatcherys[0][2]))
			print("Inject queue: " + str(self.hatcherys[0][3]))
			


			


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, TestBot()),Computer(Race.Terran, Difficulty.Easy)], realtime=False)
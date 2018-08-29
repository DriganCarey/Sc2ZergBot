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
		self.production = ["DRONE"]

	# ADDING HATCHERY TO MY LIST
	def add_hatchery(self, input_hatch: Unit, matching_queen: Unit = None):
		# zero value is hatchery itself
		# first value is inject queen
		# second value is inject queue
		self.hatcherys.append([input_hatch, matching_queen, []])


	def get_larva(self, hatchery: Unit) -> Units:
		return self.units(LARVA).closer_than(5, hatchery)

	def predict_larva(self, time: int) -> int:
		larva_count = 0
		for hatch in self.hatcherys:
			# current larva
			current_hatch_larva_count = self.get_larva(hatch).amount
			# larva count including naturally spawned larva
			current_hatch_larva_count += time/11
			current_hatch_larva_count = min(current_hatch_larva_count, 3)
			# larva count including popped larva
			if len(hatch[2] > 0):
					number_of_popped_injects = 0
					if time >= hatch[2][0]:
						number_of_popped_injects += 1
						number_of_popped_injects += min((time - hatch[2][0])/29, len(hatch[2]) - 1)
						current_hatch_larva_count += 3*number_of_popped_injects
			current_hatch_larva_count = min(current_hatch_larva_count, 19)
		return current_hatch_larva_count

	def predict_needed_supply(self, time: int) ->int:
		future_larva_count = self.predict_larva(18)
		production_loop = len(self.production)
		needed_supply = 0
		for x in range(0, future_larva_count):
			unit_needed = self.production[x%production_loop]
			if unit_needed == "DRONE":
				needed_supply += 1
		return needed_supply

	def get_to_be_avaliable_supply(self):
		# BUILD TIMES
		overlord_build_time = 18 #seconds
		float_done_hatch = 0.7465 #if hatch progress is this much, it will finish in 18 seconds
		# SUPPLY GIVEN BY
		hatchery_supply = 6 #seconds
		overlord_supply = 8 #seconds

		# calculating supply left in 18 seconds
		already_built_supply = self.already_pending(OVERLORD) * overlord_supply
		avaliable_supply = self.supply_left + (hatchery_supply * self.townhalls.filter(lambda h: 1 > h.build_progress > float_done_hatch).amount) + already_built_supply

		return avaliable_supply

	async def on_step(self, iteration):
		# only at the beginning of the game
		if (iteration == 0):
			for hatch in self.units(HATCHERY):
				self.add_hatchery(hatch)
			self.last_variable_update = 0
			self.hatcherys[0][2].append(29)

		# updating certain variables every 3 iterations
		current_time = self.time

		# updating queued injects every second
		if current_time >= self.last_variable_update + 1:
			for hatch in self.hatcherys:
				# if there is a queued inject
				if len(hatch[2]) > 0:
					if hatch[2][0] != 0:
						hatch[2][0] += -1
					else:
						del hatch[2][0]
			self.last_variable_update = current_time

		if iteration%3 == 0:
			print("self.time: " + str(self.time))
			print("Larva no: " + str(self.units(LARVA).closer_than(5, self.hatcherys[0][0]).amount))
			print("Inject queue: " + str(self.hatcherys[0][2]))
		
		# macro cycle
		if current_time%18 == 0:
			# OVERLORD
			needed_supply = self.predict_needed_supply(18)
			will_be_supply = self.get_to_be_avaliable_supply()
			diff = needed_supply - will_be_supply
			if (diff > 0):
				if self.can_afford(OVERLORD) and self.units(LARVA).exists:
					err = await self.do(self.units(LARVA).random.train(OVERLORD))
			# UNITS
			# INJECT
			# SPREAD CREEP


			


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, TestBot()),Computer(Race.Terran, Difficulty.Easy)], realtime=False)
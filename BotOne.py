from functools import reduce
from operator import or_
import random

import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.data import race_townhalls


class ZergBotV2(sc2.BotAI):
	def __init__(self):
		self.drone_count = 0
		self.unit_production_index = 0
		self.unit_production_list = ["DRONE"]
		self.unit_production = []
		self.drone_saturation = False

	# GET ALL AVALIABLE VESPENE GEYSERS
	# gets a list of vespene geysers that aren't occupied, are next to a finished hatchery and aren't empty
	# DOESNT CHECK IF THERE ARE EMPTY and whether are blocked
	def get_avaliable_gysers(self, hatchery: "Unit"):
		# creates a list of viable gysers near hatchery
		vespeneGeysers = []
		for vg in self.state.vespene_geyser.closer_than(10, hatchery):
			# checking if the vg is already occupied
			if not (self.units(EXTRACTOR).closer_than(1.0, vg).exists or self.units(ASSIMILATOR).closer_than(1.0, vg).exists or self.units(REFINERY).closer_than(1.0, vg).exists):
				vespeneGeysers.append(vg)
		return vespeneGeysers

	#variable definitions:
	@property
	def get_unsaturated_bases(self) -> "Units":
		return self.townhalls.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters)

	@property
	def get_oversaturated_bases(self) -> "Units":
		return self.townhalls.filter(lambda x: x.assigned_harvesters > x.ideal_harvesters)

	@property
	def get_saturated(self) -> "Units":
		return self.townhalls.filter(lambda x: x.assigned_harvesters >= x.ideal_harvesters)

	async def manage_drones(self):
		# MANANGING DRONES:
		# idle drones
		for idle_worker in self.units(DRONE).idle:
			if (self.get_unsaturated_bases.exists):
				target_hatch = self.get_unsaturated_bases.closest_to(idle_worker)
			else:
				target_hatch = self.townhalls.closest_to(idle_worker)
			# checking if there is an unsaturated base and assigning worker to closest one
			await self.do(idle_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
			break
		# oversaturated mineral lines (only manages if there are un-saturated bases)
		if not self.drone_saturation:
			for original_hatch in self.get_oversaturated_bases():
				for random_worker in self.workers.closer_than(17, original_hatch):
					target_hatch = self.get_unsaturated_bases.closest_to(original_hatch)
					await self.do(random_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
					break

	async def build_units(self):
		if self.units(LARVA).exists and all(self.unit_production):
			if self.unit_production_index < len(self.unit_production_list):
				current_unit = self.unit_production_list[self.unit_production_index]
				if current_unit == "DRONE":
					if self.can_afford(DRONE) and self.supply_left >= 1:
						await self.do(self.units(LARVA).random.train(DRONE))
			else:
				self.unit_production_index = 0

	async def build_overlords(self):
		if self.supply_left < 5 and not self.already_pending(OVERLORD):
			if self.units(LARVA).exists and self.can_afford(OVERLORD):
				await self.do(self.units(LARVA).random.train(OVERLORD))

	async def expand(self):
		if self.townhalls.amount < 2 and self.can_afford(HATCHERY):
			await self.expand_now()

	async def gas(self):
		saturated = self.get_saturated()
		for hatch in saturated.filter(lambda h: h.build_progress > 0.71):
			vgs = self.get_avaliable_gysers(hatch)
			if len(vgs) > 0:
				vg = vgs[0]
				if (self.can_afford(EXTRACTOR)):
					worker = self.select_build_worker(vg.position)
					if worker is not None:
						await self.do(worker.build(EXTRACTOR, vg))
				break


	# DRONES NOT BEING PUT INTO GAS
	# MULTIPLE DRONES BEING PULLED
	async def on_step(self, iteration):
		if iteration == 0:
			print("Bot has started iteration 0")
		if iteration % 5 == 0:
			# updating variables
			self.drone_count = self.units(DRONE).amount + self.already_pending(DRONE)
			self.unit_production = [True]
			self.drone_saturation = False
			if (self.get_unsaturated_bases().amount == 0):
				self.drone_saturation = True

			await self.manage_drones()
			await self.build_overlords()
			await self.build_units()
			await self.expand()
			await self.gas()
		
		
	
#running the game:
# first parameter is the map
# second parameter is the list of players/bots
# third is whether the game should be in a realtime, or sped up
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZergBotV2()), Computer(Race.Zerg, Difficulty.Easy)], realtime = True)


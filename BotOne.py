from functools import reduce
from operator import or_
import random

import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.data import race_townhalls
from sc2.unit import Unit
from sc2.units import Units

class ZergBotV2(sc2.BotAI):
	def __init__(self):
		self.drone_count = 0
		self.drone_saturation = False

		self.unit_production_index = 0
		self.unit_production_list = [DRONE ]
		self.unit_production = []

		self.can_attack_air = [QUEEN, HYDRALISK, MUTALISK, CORRUPTOR]
		self.can_attack_ground = [ROACH, DRONE, QUEEN, BANELING, RAVAGER, HYDRALISK, ULTRALISK, MUTALISK, BROODLORD]

		self.attack = False
		self.defend = True
		self.defendRangeToTownhalls = 30 # how close the enemy has to be before defenses are alerted

		self.creepSpreadInterval = 10
		self.injectInterval = 100
		self.workerTransferInterval = 10
		self.buildStuffInverval = 4
		self.microInterval = 3

	#variable definitions:
	def get_unsaturated_bases(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters)

	def get_oversaturated_bases(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters > x.ideal_harvesters)

	def get_saturated(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters >= x.ideal_harvesters)

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

	# BUILDING VARIABLE UNITS
	def larva_controller(self):
		if self.drone_count < 33 or not self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [DRONE]
		elif self.drone_count < 70 and self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [DRONE, ROACH]
		else:
			self.unit_production_list = [ROACH]

	async def build_units(self):
		if self.units(LARVA).exists:
			if self.unit_production_index < len(self.unit_production_list):
				current_unit = self.unit_production_list[self.unit_production_index]
				if current_unit in [DRONE, ZERGLING]:
					if self.can_afford(current_unit) and self.supply_left >= 1:
						await self.do(self.units(LARVA).random.train(current_unit))
						self.unit_production_index += 1
				elif current_unit in [ROACH]:
					if self.can_afford(current_unit) and self.supply_left >= 2:
						await self.do(self.units(LARVA).random.train(current_unit))
						self.unit_production_index += 1
			else:
				self.unit_production_index = 0

	async def build_overlords(self):
		if self.supply_left + (self.already_pending(OVERLORD)*8) < (5 * self.townhalls.ready.amount) and self.supply_cap + self.already_pending(OVERLORD) * 8 < 200:
			if self.units(LARVA).exists and self.can_afford(OVERLORD):
				await self.do(self.units(LARVA).random.train(OVERLORD))

	# BUILDING BUILDINGS
	# GET ALL AVALIABLE VESPENE GEYSERS
	# gets a list of vespene geysers that aren't occupied, are next to a finished hatchery and aren't empty
	# DOESNT CHECK IF THERE ARE EMPTY and whether are blocked
	def get_avaliable_gysers(self, hatchery: Unit):
		# creates a list of viable gysers near hatchery
		vespeneGeysers = []
		for vg in self.state.vespene_geyser.closer_than(10, hatchery):
			# checking if the vg is already occupied
			if not (self.units(EXTRACTOR).closer_than(1.0, vg).exists or self.units(ASSIMILATOR).closer_than(1.0, vg).exists or self.units(REFINERY).closer_than(1.0, vg).exists):
				vespeneGeysers.append(vg)
		return vespeneGeysers

	async def expand(self):
		if self.townhalls.amount < 3 and self.can_afford(HATCHERY):
			await self.expand_now()

	async def gas(self):
		saturated = self.get_saturated()
		for hatch in saturated:
			vgs = self.get_avaliable_gysers(hatch)
			if len(vgs) > 0:
				vg = vgs[0]
				if self.can_afford(EXTRACTOR) and not self.already_pending(EXTRACTOR):
					worker = self.select_build_worker(vg.position)
					if worker is not None:
						await self.do(worker.build(EXTRACTOR, vg))
				break

	async def offensive_force_buildings(self):
		if self.units(SPAWNINGPOOL).ready.exists:
			if self.drone_count > 33:
				if not self.already_pending(ROACHWARREN) and not self.units(ROACHWARREN).exists:
					 self.unit_production.append(False)
					 self.is_expanding.append(False)
					 if self.can_afford(ROACHWARREN):
					 	await self.build(ROACHWARREN, near = self.units(HATCHERY).ready.first)
		elif not self.already_pending(SPAWNINGPOOL) and self.drone_count > 18:
			self.unit_production.append(False)
			self.is_expanding.append(False)
			if self.can_afford(SPAWNINGPOOL):
				await self.build(SPAWNINGPOOL, near = self.units(HATCHERY).ready.first)

	async def attack_decision(self):
		if self.units(ROACH).amount > 30:
			self.attack = True
			self.defend = False
		# only want to defend
		elif self.units(ROACH).amount > 3:
			self.attack = False
			self.defend = True

	async def attacking(self):
		if self.attack and not self.defend:
			myArmy = self.units(ROACH)
			for unit in myArmy:
				target = self.find_target(self.state, unit)
				if not target == None:
					await self.do(unit.attack(target))
		elif self.defend and not self.attack:
			myArmy = self.units(ROACH)
			for unit in myArmy:
				target = self.find_defense_target(self.state, unit)
				if not target == None:
					await self.do(unit.attack(target))
				#else:
				#	await self.do(unit.move(self.townhalls.random))

	def find_defense_target(self, state, attacking_unit: Unit):
		# add threats: all enemy units that are closer than 30 to nearby townhalls (which are completed)
		unit_threats = set()
		structure_threats = set()
		for th in self.townhalls.ready:
			enemiesCloseToTh = self.known_enemy_units.closer_than(self.defendRangeToTownhalls, th.position)
			unit_threats |= {x.tag for x in enemiesCloseToTh}
		if len(unit_threats) > 0:
			return self.state.units.filter(lambda x: x.tag in unit_threats).closest_to(attacking_unit)
		else:
			return None

	def find_target(self, state, attacking_unit: Unit):
		unit_threats = self.known_enemy_units.filter(lambda x: ((x.is_flying and attacking_unit.type_id in self.can_attack_air)
			or (not x.is_flying and attacking_unit.type_id in self.can_attack_ground)) and not x.type_id in [DRONE, OVERLORD, OVERSEER, OVERLORDTRANSPORT, OVERSEERSIEGEMODE])
		structure_threats = self.known_enemy_structures.filter(lambda x: (x.is_flying and attacking_unit.type_id in self.can_attack_air) or (not x.is_flying and attacking_unit.type_id in self.can_attack_ground))
		if len(unit_threats) > 0:
			return unit_threats.closest_to(attacking_unit)
		elif len(structure_threats) > 0:
			return structure_threats.closest_to(attacking_unit)
		else:
			return self.enemy_start_locations[0]


	# DRONES NOT BEING PUT INTO GAS
	# DELAY IN BUILDING EXTRACTOR AFTER FINISHING ONE?
	# Building location - NOT in mineral line, in first base
	# built more drones that 70 (76), but did stop in the end
	# prioritise gas gysers in main b4 2nd or 3rd
	async def on_step(self, iteration):
		if iteration == 0:
			print("Bot has started iteration: " + str(iteration))
		# updating variables
		self.drone_count = self.units(DRONE).amount + self.already_pending(DRONE)
		self.unit_production = [True]
		self.is_expanding = [True]
		self.drone_saturation = False
		if (self.get_unsaturated_bases().amount == 0):
			self.drone_saturation = True

		# defaulting to inbuilt function for now, await self.manage_drones()
		self.larva_controller()
		if iteration % self.workerTransferInterval == 0:
			await self.distribute_workers()
		if iteration % self.buildStuffInverval == 0:
			await self.build_overlords()
			await self.offensive_force_buildings()
			if all(self.unit_production):
				await self.build_units()
			if all(self.is_expanding):
				await self.expand()
			await self.gas()
		if iteration % self.microInterval == 0:
			await self.attack_decision()
			await self.attacking()
		
		
		
	
#running the game:
# first parameter is the map
# second parameter is the list of players/bots
# third is whether the game should be in a realtime, or sped up
for i in range(1):
	print (i)
	run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZergBotV2()), Computer(Race.Random, Difficulty.Medium)], realtime = False)

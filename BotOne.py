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
		self.unit_production_list = []
		self.unit_production = []
		self.overlord_production = False

		self.unit_strategy = None
		self.can_attack_air = [QUEEN, HYDRALISK, MUTALISK, CORRUPTOR]
		self.can_attack_ground = [ROACH, DRONE, QUEEN, BANELING, RAVAGER, HYDRALISK, ULTRALISK, MUTALISK, BROODLORD]
		self.my_attack_group = set()
		self.my_defence_group = set()
		self.defendRangeToTownhalls = 30 # how close the enemy has to be before defenses are alerted
		self.first_hatchery = None

		self.opponentInfo = {
			"spawnLocation": None, # for 4player maps
			"expansions": [], # stores a list of Point2 objects of expansions
			"expansionsTags": set(), # stores the expansions above as tags so we dont count them double
			"furthestAwayExpansion": None, # stores the expansion furthest away - important for spine crawler and pool placement
			"race": None,
			"armyTagsScouted": [], # list of dicts with entries: {"tag": 123, "scoutTime": 15.6, "supply": 2}
			"armySupplyScouted": 0,
			"armySupplyScoutedClose": 0,
			"armySupplyVisible": 0,
			"scoutingUnitsNeeded": 0,
        }

		self.creepSpreadInterval = 10
		self.injectInterval = 100
		self.workerTransferInterval = 10
		self.buildStuffInverval = 4
		self.unitTargetting = 10
		self.microInterval = 3



	#######################
	''' UNIT PRODUCTION '''
	#######################
	# checks whether overlords are required
	def do_overlord_production(self):
		if not self.overlord_production:
			pending_supply = self.already_pending(OVERLORD) * 8 + self.supply_left
			if self.supply_used + pending_supply < 200:
				if pending_supply < 5 * self.townhalls.ready.amount:
					self.unit_production.append(False)
					self.overlord_production = True

	# controlls the production list, which is the ratio of units produced from larva
	def larva_controller(self):
		if self.drone_count <= 33:
			self.unit_production_list = [DRONE]
		elif self.drone_count <= 70 and self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [DRONE, ROACH]
		elif self.drone_count > 70 and self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [ROACH]
		else:
			self.unit_production_list = [DRONE]

	# builds the units according to the production list and overlord_production
	async def build_units(self):
		if self.units(LARVA).exists:
			if not self.overlord_production and all(self.unit_production):
				# resets index if it exceeds boundary
				if self.unit_production_index >= len(self.unit_production_list):
					self.unit_production_index = 0
				current_unit = self.unit_production_list[self.unit_production_index]
				if current_unit in [DRONE, ZERGLING]:
					if self.can_afford(current_unit) and self.supply_left >= 1:
						await self.do(self.units(LARVA).random.train(current_unit))
						self.unit_production_index += 1
				elif current_unit in [ROACH]:
					if self.can_afford(current_unit) and self.supply_left >= 2:
						await self.do(self.units(LARVA).random.train(current_unit))
						self.unit_production_index += 1
			elif self.overlord_production and self.can_afford(OVERLORD):
				await self.do(self.units(LARVA).random.train(OVERLORD))
				self.overlord_production = False

	###########################
	#self.units.not_structure.filter(lambda x:x.type_id not in [DRONE, LARVA, OVERLORD, ZERGLING]).amount
	''' BUILDING PRODUCTION '''
	###########################
	# returns a list of avaliable, non-empty vespene gysers that aren't occupied that are next to the specified hatchery
	# DOESNT CHECK FOR WHETHER UNIT IS BLOCKING PLACEMENT OF EXTRACTOR
	def get_avaliable_gysers(self, hatchery: Unit) -> Units:
		return self.state.vespene_geyser.closer_than(10, hatchery).filter(lambda x:
			x.vespene_contents > 0 and not (self.units(EXTRACTOR)|self.known_enemy_units.structure|self.units(ASSIMILATOR)|self.units(REFINERY)).closer_than(1.0, x).exists)

	async def expand(self):
		if all(self.is_expanding) and self.townhalls.amount < 3 and self.can_afford(HATCHERY):
			await self.expand_now()

	async def gas(self):
		saturated = self.get_saturated()
		for hatch in saturated:
			vgs = self.get_avaliable_gysers(hatch)
			for vg in vgs:
				if self.can_afford(EXTRACTOR) and not self.already_pending(EXTRACTOR):
					worker = self.select_build_worker(vg.position)
					if worker is not None:
						await self.do(worker.build(EXTRACTOR, vg))
						return

	async def offensive_force_buildings(self):
		if not self.units(SPAWNINGPOOL).ready.exists and not self.already_pending(SPAWNINGPOOL):
			if self.time > 70:
				self.unit_production.append(False)
				self.is_expanding.append(False)
				if self.can_afford(SPAWNINGPOOL):
					await self.build(SPAWNINGPOOL, near = self.units(HATCHERY).ready.first)
		elif self.units(SPAWNINGPOOL).ready.exists:
			if self.drone_count > 33:
				if not self.already_pending(ROACHWARREN) and not self.units(ROACHWARREN).exists:
					self.unit_production.append(False)
					self.is_expanding.append(False)
					if self.can_afford(ROACHWARREN):
						await self.build(ROACHWARREN, near = self.units(HATCHERY).ready.first)



	############################################
	''' ATTACKING UNIT DECISION MAKING '''
	############################################
	# makes decision whether to be attacking and or defending
	def attack_decision(self):
		if self.units(ROACH).amount > 30:
			self.unit_strategy = "all_in_attack"
		# only want to defend
		elif self.units(ROACH).amount > 3:
			self.unit_strategy = "pure_defense"

	#x.orders[0].ability.id in [AbilityId.MOVE, AbilityId.SCAN_MOVE, AbilityId.ATTACK]
	# acting upon decision above
	async def updating_unit_targetting(self):
		if self.unit_strategy == "all_in_attack":
			myArmy = self.units(ROACH)
			target = self.find_targets().closest_to(self.first_hatchery)
			if target == None:
				target = self.opponentInfo["spawnLocation"]
			for unit in myArmy:
				await self.do(unit.attack(target))
		elif self.unit_strategy == "pure_defense":
			myArmy = self.units(ROACH)
			target = self.find_targets(defence = True).closest_to(self.first_hatchery)
			if not target == None:
				for unit in myArmy:
					await self.do(unit.attack(target))

	# returns all "known enemy units and structures" with an option defence which will limit the enemy units to ones within range of a townhall
	def find_targets(self, defence = False, air = False, ground = True, include_invisible = False):
		threats = set()
		_known_enemy_units = self.known_enemy_units
		_known_enemy_structures = self.known_enemy_structures

		if not include_invisible:
			_known_enemy_units = _known_enemy_units.filter(lambda x: x.is_visible)
			_known_enemy_structures = _known_enemy_structures.filter(lambda x: x.is_visible)

		if air and not ground:
			_known_enemy_units = _known_enemy_units.filter(lambda x: x.is_flying)
			_known_enemy_structures = _known_enemy_structures.filter(lambda x: x.is_flying)
		elif ground and not air:
			_known_enemy_units = _known_enemy_units.filter(lambda x: not x.is_flying)
			_known_enemy_structures = _known_enemy_structures.filter(lambda x: not x.is_flying)
		
		if defence:
			for th in self.townhalls.ready:
				threat = _known_enemy_units.closer_than(self.defendRangeToTownhalls, th.position)
				threats |= {x.tag for x in threat}
				threat = _known_enemy_structures.closer_than(self.defendRangeToTownhalls, th.position)
				threats |= {x.tag for x in threat}
			return self.state.units.filter(x.tag in threats)
		else:
			return (_known_enemy_units + _known_enemy_structures)



	#######################
	''' BASIC FUNCTIONS '''
	#######################
	def get_unsaturated_bases(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters)

	def get_oversaturated_bases(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters > x.ideal_harvesters)

	def get_saturated(self) -> Units:
		return self.townhalls.ready.filter(lambda x: x.assigned_harvesters >= x.ideal_harvesters)

	#UNFINISHED
	############################################################################################################
	#async def manage_drones(self):
	#	# MANANGING DRONES:
	#	# idle drones
	#	for idle_worker in self.units(DRONE).idle:
	#		if (self.get_unsaturated_bases.exists):
	#			target_hatch = self.get_unsaturated_bases.closest_to(idle_worker)
	#		else:
	#			target_hatch = self.townhalls.closest_to(idle_worker)
	#		# checking if there is an unsaturated base and assigning worker to closest one
	#		await self.do(idle_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
	#		break
	#	# oversaturated mineral lines (only manages if there are un-saturated bases)
	#	if not self.drone_saturation:
	#		for original_hatch in self.get_oversaturated_bases():
	#			for random_worker in self.workers.closer_than(17, original_hatch):
	#				target_hatch = self.get_unsaturated_bases.closest_to(original_hatch)
	#				await self.do(random_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
	#				break
	###############################################################################################################

	# Building location - NOT in mineral line, in first base
	# built more drones that 70 (76), but did stop in the end
	# prioritise gas gysers in main b4 2nd or 3rd
	async def on_step(self, iteration):
		if iteration == 0:
			print("Bot has started iteration: " + str(iteration))
			self.opponentInfo["spawnLocation"] = self.enemy_start_locations[0]
			self.first_hatchery = self.townhalls.random
		# updating variables
		self.drone_count = self.units(DRONE).amount + self.already_pending(DRONE)
		self.unit_production = [True]
		self.is_expanding = [True]
		self.drone_saturation = False
		if (self.get_unsaturated_bases().amount == 0):
			self.drone_saturation = True

		# defaulting to inbuilt function for now, await self.manage_drones()
		if iteration % self.workerTransferInterval == 0:
			await self.distribute_workers()
		if iteration % self.buildStuffInverval == 0:
			# units - larva
			self.do_overlord_production()
			self.larva_controller()
			await self.build_units()
			# buildings
			await self.offensive_force_buildings()
			await self.expand()
			await self.gas()
		if iteration % self.microInterval == 0:
			pass
		if iteration % self.unitTargetting == 0:
			self.attack_decision()
			await self.updating_unit_targetting()
		
		
		'''pos = await self.find_placement(SPAWNINGPOOL, townhallLocationFurthestFromOpponent, min_distance=6)
                    # pos = await self.find_placement(SPAWNINGPOOL, self.townhalls.ready.random.position.to2, min_distance=6)
                    if pos is not None:
                        drone = self.workers.closest_to(pos)
                        if self.can_afford(SPAWNINGPOOL):
                            err = await self.do(drone.build(SPAWNINGPOOL, pos))

        # townhall furthest away from enemy base - that is where i will make all the tech buildings
            townhallLocationFurthestFromOpponent = None
            if self.townhalls.ready.exists and self.known_enemy_structures.exists:
                townhallLocationFurthestFromOpponent = max([x.position.to2 for x in self.townhalls.ready], key=lambda x: x.closest(self.known_enemy_structures).distance_to(x))
            if townhallLocationFurthestFromOpponent is None and self.townhalls.ready.exists:
                townhallLocationFurthestFromOpponent = self.townhalls.ready.random.position.to2'''
	
#running the game:
# first parameter is the map
# second parameter is the list of players/bots
# third is whether the game should be in a realtime, or sped up
for i in range(1):
	print (i)
	run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZergBotV2()), Computer(Race.Random, Difficulty.Medium)], realtime = False)

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
		self.unit_strategy = None

		self.can_attack_air = [QUEEN, HYDRALISK, MUTALISK, CORRUPTOR]
		self.can_attack_ground = [ROACH, DRONE, QUEEN, BANELING, RAVAGER, HYDRALISK, ULTRALISK, MUTALISK, BROODLORD]
		
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
	def overlord_production(self):
		pending_supply = self.already_pending(OVERLORD) * 8 + self.supply_left
		if self.supply_used + pending_supply < 200:
			if self.drone_count < 14 and pending_supply <= 1 :
				return True
			elif pending_supply < 5 * self.townhalls.ready.amount and self.drone_count > 14:
				return True
		return False

	# controlls the production list, which is the ratio of units produced from larva
	def larva_controller(self):
		if not hasattr(self, "unit_production_list"):
			self.unit_production_list = []
		# first checks as to whether overlords are needed
		if self.overlord_production:
			self.unit_production_list = [OVERLORD]
		# if overlords are not needed
		elif self.drone_count <= 33:
			self.unit_production_list = [DRONE]
		elif self.drone_count <= 70 and self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [DRONE, ROACH]
		elif self.drone_count > 70 and self.units(ROACHWARREN).ready.exists:
			self.unit_production_list = [ROACH]
		else:
			self.unit_production_list = [DRONE]

	# builds the units according to the production list and overlord_production
	async def build_units(self):
		if not hasattr(self, "unit_production_index"):
			self.unit_production_index = 0
		if self.units(LARVA).exists:
			if all(self.unit_production):
				# resets index if it exceeds boundary
				if self.unit_production_index >= len(self.unit_production_list):
					self.unit_production_index = 0
				current_unit = self.unit_production_list[self.unit_production_index]
				if self.can_afford(unit):
					if (unit in [DRONE, ZERGLING] and self.supply_left >= 1) or (unit in [ROACH] and self.supply_left >= 2) or (unit in [OVERLORD])
						await self.do(self.units(LARVA).random.train(current_unit))


	# INJECT MACRO
	# COPIED AND PASTED FROM CREEPYBOT
	# take into account not using hatcheries with over 19 larva??
	async def inject(self):
		# list of all alive queens and bases, will be used for injecting
		aliveQueenTags = [queen.tag for queen in self.units(QUEEN)] # list of numbers (tags / unit IDs)
		aliveBasesTags = [base.tag for base in self.townhalls]
		
		# make queens inject if they have 25 or more energy
		toRemoveTags = []

		if hasattr(self, "queensAssignedHatcheries"):
			for queenTag, hatchTag in self.queensAssignedHatcheries.items():
				if queenTag not in aliveQueenTags: # queen is no longer alive
					toRemoveTags.append(queenTag)
					continue
				# hatchery / lair / hive is no longer alive
				if hatchTag not in aliveBasesTags:
					toRemoveTags.append(queenTag)
					continue
				# queen and base are alive, try to inject if queen has 25+ energy
				queen = self.units(QUEEN).find_by_tag(queenTag)
				hatch = self.townhalls.find_by_tag(hatchTag)
				if hatch.is_ready:
					if queen.energy >= 25 and queen.is_idle and not hatch.has_buff(QUEENSPAWNLARVATIMER):
						await self.do(queen(EFFECT_INJECTLARVA, hatch))
				else:
					if iteration % self.injectInterval == 0 and queen.is_idle and queen.position.distance_to(hatch.position) > 10:
						await self.do(queen(AbilityId.MOVE, hatch.position.to2))

			# clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
			for tag in toRemoveTags:
				self.queensAssignedHatcheries.pop(tag)

	def pair_inject_queens(self, max_amount_inject_queens = 5):
		if not hasattr(self, "queen_hatchery_pairing"):
			self.queen_hatchery_pairing = {}
		if maxAmountInjectQueens == 0:
			self.queen_hatchery_pairing = {}
			return

		basesNoInjectPartner = self.townhalls.filter(lambda h: h.tag not in self.queen_hatchery_pairing.values() and h.build_progress > 0.8 )
		for queen in self.units(QUEEN).filter(lambda q: q.tag not in self.queen_hatchery_pairing.keys()):
			if basesNoInjectPartner.amount == 0:
				break
			self.queen_hatchery_pairing[queen.tag] = basesNoInjectPartner.closest_to(queen).tag
			break

	async def build_queens(self):
		if self.units(SPAWNINGPOOL).exists:
			pending_queens = 0
			for hatch in townhalls:
				pass


	###########################
	#self.units.not_structure.filter(lambda x:x.type_id not in [DRONE, LARVA, OVERLORD, ZERGLING]).amount
	''' BUILDING PRODUCTION '''
	###########################
	async def expand(self):
		if all(self.is_expanding) and self.townhalls.amount < 3 and self.can_afford(HATCHERY):
			await self.expand_now()

	async def gas_control(self):
		if self.drone_count < 34:
			if self.units(EXTRACTOR).amount < 1 and self.townhalls.amount + self.already_pending(HATCHERY) >= 2:
				await self.gas()
		else:
			await self.gas()

	async def gas(self):
		saturated = self.townhalls.ready.filter(lambda x: x.assigned_harvesters >= x.ideal_harvesters)
		for hatch in saturated:
			vgs = self.state.vespene_geyser.closer_than(10, hatch).filter(lambda x: x.vespene_contents > 0 and not self.state.units.filter(x.name in [EXTRACTOR, ASSIMILATOR, REFINERY]).closer_than(1.0, x)).exists
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
				self.expansions.append(False)
				if self.can_afford(SPAWNINGPOOL):
					await self.build(SPAWNINGPOOL, near = self.units(HATCHERY).ready.first)
		elif self.units(SPAWNINGPOOL).ready.exists:
			if self.drone_count > 33:
				if not self.already_pending(ROACHWARREN) and not self.units(ROACHWARREN).exists:
					self.unit_production.append(False)
					self.is_expanding.append(False)
					if self.can_afford(ROACHWARREN):
						await self.build(ROACHWARREN, near = self.units(HATCHERY).ready.first)



	################
	''' UPGRADES '''
	################


	############################################
	''' ATTACKING UNIT DECISION MAKING '''
	############################################
	# makes decision whether to be attacking and or defending
	def attack_decision(self):
		if self.supply_used > 180:
			self.unit_strategy = "all_in_attack"
		# only want to defend
		elif self.units(ROACH).amount > 3:
			self.unit_strategy = "pure_defense"

	#x.orders[0].ability.id in [AbilityId.MOVE, AbilityId.SCAN_MOVE, AbilityId.ATTACK]
	# acting upon decision above
	async def updating_unit_targetting(self):
		if self.unit_strategy == "all_in_attack":
			myArmy = self.units(ROACH)
			targets = self.get_target()
			target = None
			if targets.exists:
				target = targets.closest_to(self.first_hatchery)
			else:
				target = self.opponentInfo["spawnLocation"]
			for unit in myArmy.idle:
				await self.do(unit.attack(target.position))
		elif self.unit_strategy == "pure_defense":
			myArmy = self.units(ROACH)
			targets = self.get_target(defence = True)
			target = None
			if targets.exists:
				target = targets.closest_to(self.first_hatchery)
				for unit in myArmy.idle:
					await self.do(unit.attack(target.position))

	# returns all "known enemy units and structures" with an option defence which will limit the enemy units to ones within range of a townhall
	def get_target(self, defence = False, air = False, ground = True, include_invisible = False):
		threats = self.state.units.enemy
		if not include_invisible:
			threats = threats.filter(lambda x: x.is_visible)
		if not air:
			threats = threats.filter(lambda x: not x.is_flying)
		if not ground:
			threats = threats.filter(lambda x: x.is_flying)
		if defence:
			enemy_tags = set()
			for hatch in self.townhalls:
				enemy_tags |= {x.tag for x in threats.closer_than(self.defendRangeToTownhalls, hatch.position)}
			threats = threats.filter(lambda x: x.tag in enemy_tags)
		return threats

	#######################
	''' BASIC FUNCTIONS '''
	#######################
	def drone_saturation(self, mineral = True, gas = True) -> bool:
		# if there is a unsaturated townhall
		if mineral:
			if self.townhalls.ready.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters) > 0:
				return False
		if gas:
			if self.units(EXTRACTOR).ready.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters) > 0:
				return False
		return True

	async def start_stuff(self):
		print("Bot has started iteration: " + str(iteration))
		self.opponentInfo["spawnLocation"] = self.enemy_start_locations[0]
		self.first_hatchery = self.townhalls.random

	#UNFINISHED
	############################################################################################################
	#def get_unsaturated_bases(self) -> Units:
	#	return self.townhalls.ready.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters)
	#
	#def get_oversaturated_bases(self) -> Units:
	#	return self.townhalls.ready.filter(lambda x: x.assigned_harvesters > x.ideal_harvesters)
	#
	#def get_saturated(self) -> Units:
	#	return self.townhalls.ready.filter(lambda x: x.assigned_harvesters >= x.ideal_harvesters)
	#
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
			await self.start_stuff()

		# updating variables
		self.drone_count = self.units(DRONE).amount + self.already_pending(DRONE)
		self.extractor_count = self.units(EXTRACTOR).amount + self.already_pending(EXTRACTOR)

		self.unit_production = [True]
		self.building_production = [True]

		# defaulting to inbuilt function for now, await self.manage_drones()
		if iteration % self.workerTransferInterval == 0:
			await self.distribute_workers()
		if iteration % self.buildStuffInverval == 0:
			# units - larva
			self.larva_controller()
			await self.build_units()
			# buildings
			await self.offensive_force_buildings()
			await self.expand()
			await self.gas_control()
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

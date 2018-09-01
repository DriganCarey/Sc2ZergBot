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

		# self.state.units will show all visible units on map (all creatures and structures and geysers and minerals)
		self.mineral_and_gas_name = ["MineralField750", "MineralField", "VespeneGeyser"]
		self.rock_name = ["DestructibleRockEx1DiagonalHugeBLUR", "UnbuildableRocksDestructible", "DestructibleRockEx14x4"]
		self.non_attacking_units = ["Drone", "Overlord"]
		# KEY NOTE - this will include all unfinished buildings and will also name them
		# KEY NOTE - eggs and units from them don't retain the same tags
		# KEY NOTES - this will not show if the structure is building something (via just printing the units list - could orders show this?)
		# self.state.units.owned will filter to all stuff owned by player
		# self.state.units.enemy will filter to all stuff owned by opponent
		# guessing units.append(UNIT) will add this unit to the group!


		# PRINTING OUT UNITS:
		# Unit(name='Queen', tag = 123)
		# UnitOrder(AbilityData(name = QUEEN or zergmissileweapons1), 0, float_number_of_how_completed) #triggered by unit.orders, will show [] for enemy units, .build_progress will show build progress for enemy units/structures
		# is there a way to tell a units upgrades?
		# is there a way to tell whether something is building - lit up, pulsating etc

	
	async def on_step(self, iteration):
		if iteration % 300 == 0:
			print("Number: " + str(iteration/300))
			#print("All mineral fields and gas geysers")
			#print(self.state.units.structure.filter(lambda x: x.is_mineral_field or x.is_vespene_geyser))
			#print("----------------------------------------------------------------")
			#print("All destructible rocks")
			#print(self.state.units.filter(lambda x: x.name in self.rock_name))
			#print("----------------------------------------------------------------")
			#print("All of my units")
			#print(self.state.units.owned.not_structure.filter(lambda x: not x.name in self.non_attacking_units))
			#print("----------------------------------------------------------------")
			#print("All of my structures")
			#for structure in self.state.units.owned.structure:
			#	print (str(structure) + ": " + str(structure.orders))
			for structure in self.units(EXTRACTOR).ready:
				print(str(structure.assigned_harvesters) + " out of " + str(structure.ideal_harvesters))
			#print("----------------------------------------------------------------")
			#print("All of my opponents units")
			#print(self.state.units.enemy.not_structure)
			#print("----------------------------------------------------------------")
			#print("All of my opponents structure")
			#for structure in self.state.units.enemy.structure:
			#	print ("orders: " + str(structure) + ": " + str(structure.build_progress))
			#print (dir(self.state.units))
			print("=================================================================")


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, TestBot()), Computer(Race.Terran, Difficulty.Medium)], realtime = True)
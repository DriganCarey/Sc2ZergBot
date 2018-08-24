import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.data import race_townhalls

class ZergBot(sc2.BotAI):
	def __init__(self):
		self.max_drone = 75
		self.aim_drone_count = 75 
		self.drone_count = 0

	async def on_step(self, iteration):
		self.drone_count = self.units(DRONE).amount + self.already_pending(DRONE)
		if (iteration%5 == 0):
			await self.decision_tree()

	async def decision_tree(self):
		if self.drone_count <= self.max_drone and self.drone_count <=  self.aim_drone_count and self.could_afford("DRONE"):
			await self.do(self.units(LARVA).random.train(DRONE))
		else:
			await manage_drones()

	''' Will manage drones'''
	async def manage_drones(self):
		# idle drones
		for idle_worker in self.units(DRONE).idle:
			if (self.get_unsaturated_bases.exists):
				target_hatch = self.get_unsaturated_bases.closest_to(idle_worker)
			else:
				target_hatch = self.townhalls.closest_to(idle_worker)
			await self.do(idle_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
			break
		# oversaturated mineral lines (only manages if there are un-saturated bases)
		if not self.drone_saturation:
			for original_hatch in self.get_oversaturated_bases():
				for random_worker in self.workers.closer_than(17, original_hatch):
					target_hatch = self.get_unsaturated_bases.closest_to(original_hatch)
					await self.do(random_worker.gather(self.state.mineral_field.closest_to(target_hatch)))
					break

	def could_afford(self, input_unit):
		if input_unit == "DRONE":
			if self.units(LARVA).exists and self.supply_left >= 1 and self.can_afford(DRONE):
				return True
		return False

	# supporting functions:
	@property
	def get_unsaturated_bases(self) -> "Units":
		return self.townhalls.filter(lambda x: x.assigned_harvesters < x.ideal_harvesters)

	@property
	def get_oversaturated_bases(self) -> "Units":
		return self.townhalls.filter(lambda x: x.assigned_harvesters > x.ideal_harvesters)
#running the game:
# first parameter is the map
# second parameter is the list of players/bots
# third is whether the game should be in a realtime, or sped up
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, ZergBot()), Computer(Race.Zerg, Difficulty.Easy)], realtime = True)
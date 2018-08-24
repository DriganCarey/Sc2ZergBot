# Sc2ZergBot
A bot that should hopefully be able to make decisions and follow build orders in order to play the strategy game known as starcraft II

My aim:
  1. Economy (passive):
    i. Managing drones - no idle drones, mining enough gas to mineral ratio, oversatured bases
    ii.  Building drones until it reaches the wanted number of drones
    iii. Building overlords to meet future supply demand in 18 seconds
    iv. Constantly injecting with inject queens
    v. Spreading creep with creep queens
  2. Defense and vision (some passive, some reactive):
    i. Pulling queens (creep queens first, and if threat escalates inject queens) and units to defend harrassment
    ii. Building blind spores at appropiate time (4:30)
    iii. Scouting - leaving lings around map, overlords in empty space (pull them in if anti-air unit seen in area)
    iv. Keeping track of number of enemy bases
    v. Keeping track of enemy army size, position and composition
    vi. Building defensive units when needed
  3. Attacking (reactive):
    i. Bot should attack when it is confident it can win against enemy army
    ii. When the enemy army is out of position
    iii. Trading when it is maxed
    iv. Micro
  4. Build orders:
    2 base bane bust/all-in,
    3 base roach ravager all-in, 
    3 base ling bane hydra, 
    12/13 speedling all in, 
  5. Economic openers:
    17 hatch 18 gas 17 pool
    17 pool 18 gas 17 hatch
  ....
  a. Bot can defeat the very easy ai
  b. Bot can defeat the easy ai
  c. Bot can defeat the medium ai
  d. Bot can defeat the hard ai
  e. Bot can defeat the very hard ai
  f. Bot can defeat the elite ai
  g. Bot can defeat the insane cheater ai
  ....
  x. Bot will be able to choose a build order at the beginning of the game and attempt to follow the build order, making decisions/changes as it sees fit to react to the opponent
  x + 1. Machine learning?

Other details:
  I want to try and build a decision tree - the bot should only try to take one action at a time
  Want to attempt to randomise choices in order to prevent bot from acting completely predictably

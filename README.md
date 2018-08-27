# Sc2ZergBot
A bot that should hopefully be able to make decisions and follow build orders in order to play the strategy game known as starcraft II

For now:<br />
  Building some functions that are able to predict the amount of larva in the next x seconds and income in the next x seconds if the user does not do anything<br />

My aim:<br />
  1. Economy (passive):<br />
    i. Managing drones - no idle drones, mining enough gas to mineral ratio, oversatured bases<br />
    ii.  Building drones until it reaches the wanted number of drones<br />
    iii. Building overlords to meet future supply demand in 18 seconds<br />
    iv. Constantly injecting with inject queens<br />
    v. Spreading creep with creep queens<br />
  2. Defense and vision (some passive, some reactive):<br />
    i. Pulling queens (creep queens first, and if threat escalates inject queens) and units to defend harrassment<br />
    ii. Building blind spores at appropiate time (4:30)<br />
    iii. Scouting - leaving lings around map, overlords in empty space (pull them in if anti-air unit seen in area)<br />
    iv. Keeping track of number of enemy bases<br />
    v. Keeping track of enemy army size, position and composition<br />
    vi. Building defensive units when needed<br />
  3. Attacking (reactive):<br />
    i. Bot should attack when it is confident it can win against enemy army<br />
    ii. When the enemy army is out of position<br />
    iii. Trading when it is maxed<br />
    iv. Micro<br />
  4. Build orders:<br />
    2 base bane bust/all-in,<br />
    3 base roach ravager all-in, <br />
    3 base ling bane hydra, <br />
    12/13 speedling all in, <br />
  5. Economic openers:<br />
    17 hatch 18 gas 17 pool<br />
    17 pool 18 gas 17 hatch<br />
  ....<br />
  a. Bot can defeat the very easy ai<br />
  b. Bot can defeat the easy ai<br />
  c. Bot can defeat the medium ai<br />
  d. Bot can defeat the hard ai<br />
  e. Bot can defeat the very hard ai<br />
  f. Bot can defeat the elite ai<br />
  g. Bot can defeat the insane cheater ai<br />
  ....<br />
  x. Bot will be able to choose a build order at the beginning of the game and attempt to follow the build order, making decisions/changes as it sees fit to react to the opponent<br />
  x + 1. Machine learning?<br />

Other details:<br />
  I want to try and build a decision tree - the bot should only try to take one action at a time<br />
  Want to attempt to randomise choices in order to prevent bot from acting completely predictably<br />

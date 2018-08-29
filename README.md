# Sc2ZergBot
A bot that should hopefully be able to make decisions and follow build orders in order to play the strategy game known as starcraft II

For now:<br />
  Refinining my basic bot so that it is more efficient<br />
  

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
  a. Bot has defeated the very easy ai ☑<br />
  b. Bot can defeat the very easy ai consistently (5 times in a row) ☑<br />
  c. Bot has defeated the easy ai ☑<br />
  d. Bot can defeat the easy ai consistently (5 times in a row) ☑<br />
  e. Bot has defeated the medium ai ✘<br />
  f. Bot can defeat the medium ai consistently (5 times in a row) ✘<br />
  g. Bot has defeated the hard ai ✘<br />
  h. Bot can defeat the hard ai consistently (5 times in a row) ✘<br />
  i. Bot has defeated the very hard ai ✘<br />
  j. Bot can defeat the very hard ai consistently (5 times in a row)<br />
  k. Bot has defeated the elite ai ✘<br />
  l. Bot can defeat the elite ai consistently (5 times in a row) ✘<br />
  m. Bot has defeated the cheater (vision) ai ✘<br />
  n. Bot can defeat the cheater (vision) ai consistently (5 times in a row) ✘<br />
  o. Bot has defeated the cheater (money) ai ✘<br />
  p. Bot can defeat the cheater (money) ai consistently (5 times in a row) ✘<br />
  q. Bot has defeated the insane cheater ai ✘<br />
  r. Bot can defeat the insane cheater ai consistently (5 times in a row) ✘<br />
  ....<br />
  x. Bot will be able to choose a build order at the beginning of the game and attempt to follow the build order, making decisions/changes as it sees fit to react to the opponent<br />
  x + 1. Machine learning?<br />

Other details:<br />
  I want to try and build a decision tree - the bot should only try to take one action at a time<br />
  Want to attempt to randomise choices in order to prevent bot from acting completely predictably<br />

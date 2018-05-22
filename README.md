# DuopolyAnalysis
Analysis part of Duopoly project

# Data 

A csv file containing all the results is available at ****data/data.csv****.

Formatting details:
 * Each room contains two players who each pass two rounds: **PVE** (Player Versus Environment), and **PVP** (Player vs Player).
Each room therefore contains a total of three rounds (two **PVE**, one **PVP**).

* The **PVE** rounds hosts a human and a bot, while the **PVP** rounds constitute the final confrontation between the two human players.

* The type of treatment (**PVE**, **PVP**) is indicated by the column **PVP** (**0** if **PVE**, **1** if **PVP**).

* When the treatment is **PVE**, one of the two firm_id is designed by **-1** (the bot identifier). 


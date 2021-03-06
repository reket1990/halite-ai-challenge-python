import hlt
import logging

################################### HELPER FUNCTIONS ###################################
def attack(ship, game_map):
    # Get enemy ships by distance
    foreign_ships = game_map.nearby_entities_by_distance(ship, 'Ship')
    enemy_ships = list(filter(
        lambda foreign_ship: foreign_ship.owner.id != game_map.get_me().id,
        foreign_ships
    ))
    docked_enemy_ships = list(filter(
        lambda enemy_ship: enemy_ship.docking_status != ship.DockingStatus.UNDOCKED,
        enemy_ships
    ))

    # No enemy targets to kill, move closer slowly
    if len(docked_enemy_ships) == 0:
        target = enemy_ships[0]
        logging.info("Ship " + str(ship.id) + ": No targets, moving closer")
        return ship.navigate(
            ship.closest_point_to(target, distance=hlt.constants.WEAPON_RADIUS+1),
            game_map,
            ignore_ships=True)

    # Attack enemy docked ship
    else:
        target = docked_enemy_ships[0]
        logging.info("Ship " + str(ship.id) + ": Target Found")
        return ship.navigate(
            ship.closest_point_to(target, distance=hlt.constants.WEAPON_RADIUS),
            game_map,
            ignore_ships=True)
################################# END: HELPER FUNCTIONS ################################

######################################### BOTS #########################################
def two_players(game_map):
    """
    Bot for 2 player games

    :param game_map.Map game_map: The map of the game, from which obstacles will be extracted
    :return list: The list of commands trying to be passed to the Halite engine
    :rtype: list[str]
    """
    command_queue = []

    for ship in game_map.get_me().all_ships():
        # One in 3 ships are attacker ships
        if ship.id % 3 == 2:
            navigate_command = attack(ship, game_map)

        # All other ships are econ ships
        else:
            # Skip ship is already docking / docked
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                continue

            # Get planets by distance
            planets = game_map.nearby_entities_by_distance(ship, 'Planet')
            mineable_planets = list(filter(
                lambda planet:
                    not planet.is_owned() or
                    (planet.owner.id == game_map.get_me().id and not planet.is_full()),
                planets
            ))

            # If no mineable planets, ship becomes attack ship
            if len(mineable_planets) == 0:
                logging.info("Ship " + str(ship.id) + ": No mineable planets, attacking")
                navigate_command = attack(ship, game_map)

            # Else, econ
            else:
                target = mineable_planets[0]
                if ship.can_dock(target):
                    logging.info("Ship " + str(ship.id) + ": Docking")
                    navigate_command = ship.dock(target)
                else:
                    # If we can't dock, we move towards the planet
                    logging.info("Ship " + str(ship.id) + ": Moving towards planet")
                    navigate_command = ship.navigate(
                        ship.closest_point_to(target, distance=hlt.constants.DOCK_RADIUS),
                        game_map)

        if navigate_command:
            command_queue.append(navigate_command)

    return command_queue


def four_players(game_map):
    """
    Bot for 4 player games

    :param game_map.Map game_map: The map of the game, from which obstacles will be extracted
    :return list: The list of commands trying to be passed to the Halite engine
    :rtype: list[str]
    """
    # For now just use the two player bot
    return two_players(game_map)
####################################### END: BOTS ######################################

####################################### GAMEPLAY #######################################
# GAME START
# Here we define the bot's name as reket1990 and initialize the game, including communication with the Halite engine
game = hlt.Game("reket1990")
# Then we print our start message to the logs
logging.info("Starting up reket1990 bot")

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    if len(game_map.all_players()) == 2:
        command_queue = two_players(game_map)

    else:
        command_queue = four_players(game_map)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
##################################### END: GAMEPLAY ####################################

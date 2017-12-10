"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as reket1990 and initialize the game, including communication with the Halite engine.
game = hlt.Game("reket1990")
# Then we print our start message to the logs
logging.info("Starting up reket1990!")


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
                navigate_command = ship.navigate(
                    ship.closest_point_to(target, min_distance=6),
                    game_map,
                    speed=4,
                    ignore_ships=True)

            # Attack enemy docked ship
            else:
                target = docked_enemy_ships[0]
                navigate_command = ship.navigate(
                    ship.closest_point_to(target, min_distance=5),
                    game_map,
                    speed=7,
                    ignore_ships=True)

            if navigate_command:
                command_queue.append(navigate_command)

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

            target = mineable_planets[0]
            if ship.can_dock(target):
                command_queue.append(ship.dock(planet))
            else:
                # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
                navigate_command = ship.navigate(
                    ship.closest_point_to(target),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=True)

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
    two_players(game_map)

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

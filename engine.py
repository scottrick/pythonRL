import tcod as tcod

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys 
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, RenderOrder

def main():
    name = "pythonRL"

    screenWidth = 80
    screenHeight = 50

    bar_width = 20
    panel_height = 7
    panel_y = screenHeight - panel_height

    message_x = bar_width + 2
    message_width = screenWidth - bar_width - 1
    message_height = panel_height - 1

    mapWidth = 80
    mapHeight = 43

    room_min_size = 6
    room_max_size = 10
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3

    colors = {
        'dark_wall': tcod.Color(61, 31, 0),
        'dark_ground': tcod.Color(41, 21, 0),
        'light_wall': tcod.Color(77, 38, 0),
        'light_ground': tcod.Color(56, 28, 0),
        'nothing': tcod.Color(0, 0, 0)
    }

    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, "@", tcod.white, "Player", blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
    entities = [player]

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(screenWidth, screenHeight, name, False, tcod.RENDERER_SDL2, "F", True)

    con = tcod.console.Console(screenWidth, screenHeight, "F")
    panel = tcod.console.Console(screenWidth, panel_height)

    game_map = GameMap(mapWidth, mapHeight)
    game_map.make_map(max_rooms, room_min_size, room_max_size, mapWidth, mapHeight, player, entities, max_monsters_per_room)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYERS_TURN

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screenWidth, screenHeight, bar_width, panel_height, panel_y, mouse, colors)

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        generate = action.get("gen")

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entities_at_location(entities, dest_x, dest_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if exit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get("message")
            dead_entity = player_turn_result.get("dead")

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player: 
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get("message")
                        dead_entity = enemy_turn_result.get("dead")

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


        if generate:
            game_map.clear()
            game_map.make_map(max_rooms, room_min_size, room_max_size, mapWidth, mapHeight, player)
            fov_map = initialize_fov(game_map)
            fov_recompute = True



if __name__ == '__main__':
    main()



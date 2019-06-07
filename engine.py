import tcod as tcod

from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys 
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all

def main():
    name = "pythonRL"

    screenWidth = 80
    screenHeight = 50
    mapWidth = 80
    mapHeight = 50

    room_min_size = 6
    room_max_size = 10
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(20, 20, 120),
        'light_ground': tcod.Color(70, 70, 170),
        'nothing': tcod.Color(0, 0, 0)
    }

    player = Entity(int(screenWidth / 2), int(screenHeight / 2), "@", tcod.white)
    npc = Entity(int(screenWidth / 2 - 5), int(screenHeight / 2 - 5), "@", tcod.blue)
    entities = [npc, player]

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(screenWidth, screenHeight, name, False, tcod.RENDERER_SDL2, "F", True)

    con = tcod.console.Console(screenWidth, screenHeight, "F")

    game_map = GameMap(mapWidth, mapHeight)
    game_map.make_map(max_rooms, room_min_size, room_max_size, mapWidth, mapHeight, player)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, entities, game_map, fov_map, fov_recompute, screenWidth, screenHeight, colors)

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        generate = action.get("gen")

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)
                fov_recompute = True

        if exit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if generate:
            game_map.clear()
            game_map.make_map(max_rooms, room_min_size, room_max_size, mapWidth, mapHeight, player)
            fov_map = initialize_fov(game_map)
            fov_recompute = True



if __name__ == '__main__':
    main()



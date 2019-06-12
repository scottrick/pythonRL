import tcod as tcod

from enum import Enum

class RenderOrder(Enum):
	CORPSE = 1
	ITEM = 2
	ACTOR = 3

def render_all(con, entities, player, game_map, fov_map, fov_recompute, screenWidth, screenHeight, colors):
	#draw all tiles in the game
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):
				visible = tcod.map_is_in_fov(fov_map, x, y)
				wall = game_map.tiles[x][y].block_sight

				if visible:
					if wall:
						tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
					else:
						tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)

					game_map.tiles[x][y].explored = True
				elif game_map.tiles[x][y].explored:
					if wall:
						tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
					else:
						tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)
				else:
					tcod.console_set_char_background(con, x, y, colors.get('nothing'), tcod.BKGND_SET)

	entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

	#draw all entities in the list
	for entity in entities_in_render_order:
		draw_entity(con, entity, fov_map)

		tcod.console_set_default_foreground(con, tcod.white)
		tcod.console_print_ex(con, 1, screenHeight - 2, tcod.BKGND_NONE, tcod.LEFT, "HP: {0:02}/{1:02}".format(player.fighter.hp, player.fighter.max_hp))

	tcod.console_blit(con, 0, 0, screenWidth, screenHeight, 0, 0, 0)


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)

def draw_entity(con, entity, fov_map):
	if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
		tcod.console_set_default_foreground(con, entity.color)
		tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

def clear_entity(con, entity):
	# erase the character that represents this entity
	tcod.console_put_char(con, entity.x, entity.y, " ", tcod.BKGND_NONE)


//test code pls ignore
var/list/skip_vars = list(
    "skip_vars",
    "UNIX", "MS_WINDOWS",
    "NORTH","SOUTH","EAST","WEST", "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST", "UP", "DOWN",
    "BLIND","SEE_MOBS","SEE_OBJS","SEE_TURFS","SEE_SELF","SEE_INFRA","SEE_PIXELS","SEE_THRU","SEE_BLACKNESS",
    "MOB_PERSPECTIVE","EDGE_PERSPECTIVE","EYE_PERSPECTIVE",
    "FLOAT_LAYER","AREA_LAYER","TURF_LAYER","OBJ_LAYER","MOB_LAYER","FLY_LAYER","EFFECTS_LAYER","TOPDOWN_LAYER","BACKGROUND_LAYER",
    "FLOAT_PLANE",
    "TOPDOWN_MAP", "ISOMETRIC_MAP", "SIDE_MAP", "TILED_ICON_MAP",
    "TRUE", "FALSE",
    "MALE", "FEMALE", "NEUTER", "PLURAL",
    "MOUSE_INACTIVE_POINTER", "MOUSE_ACTIVE_POINTER", "MOUSE_DRAG_POINTER", "MOUSE_DROP_POINTER", "MOUSE_ARROW_POINTER", "MOUSE_CROSSHAIRS_POINTER","MOUSE_HAND_POINTER",
    "MOUSE_LEFT_BUTTON","MOUSE_RIGHT_BUTTON","MOUSE_MIDDLE_BUTTON",
    "MOUSE_CTRL_KEY","MOUSE_SHIFT_KEY","MOUSE_ALT_KEY",
    "SOUND_MUTE", "SOUND_PAUSED", "SOUND_STREAM", "SOUND_UPDATE",
    "BLEND_DEFAULT", "BLEND_OVERLAY", "BLEND_ADD", "BLEND_SUBTRACT", "BLEND_MULTIPLY", "BLEND_INSET_OVERLAY"
)

var/datum/d = new

var/list/observed_types = list()

mob/admin_commands/verb
   shutdown_world()
      world.Del()
   reboot_world()
      world.Reboot()

mob/admin_commands/proc
    hi()
        return 5

/proc/print_vars(vs)
    for(var/v in vs)
        if (v in skip_vars) 
            continue
        world.log << "[v] [json_encode(typesof(vs[v]))]"

/proc/main()
    var/path = text2path("/")
    world.log << "[json_encode(path)]"
    world.log << "[json_encode(typesof(path))]" 


from ..common import *

class Stdlib:
    class Builder(object):
        def __init__(self):
            self.current_path = []
            self.parent_types = {}
            self.procs = collections.defaultdict(dict)
            self.vars = collections.defaultdict(dict)

        class _dmtype(object):
            def __init__(self, builder, paths):
                self.builder = builder
                self.paths = paths

            def __enter__(self):
                self.builder.current_path += self.paths

            def __exit__(self, *args):
                self.builder.current_path = self.builder.current_path[:-len(self.paths)]

        def get_current_path(self):
            return tuple(self.current_path)

        def dmtype(self, *paths):
            return self._dmtype(self, paths)

        def parent_type(self, *path):
            self.parent_types[ self.get_current_path() ] = path

        def dmproc(self, name, **options):
            self.procs[ self.get_current_path() ][name] = options

        def dmvar(self, name, **options):
            self.vars[ self.get_current_path() ][name] = options

        def dmop(self, name):
            pass

    def initialize():
        b = Stdlib.Builder()

        # testing/debug
        b.dmproc("ASSERT")
        b.dmproc("CRASH")

        # math
        b.dmproc("abs")
        b.dmproc("arccos")
        b.dmproc("arcsin")
        b.dmproc("arctan")
        b.dmproc("clamp")
        b.dmproc("cos")
        b.dmproc("generator")
        b.dmproc("log")
        b.dmproc("max")
        b.dmproc("min")
        b.dmproc("pick")
        b.dmproc("prob")
        b.dmproc("rand")
        b.dmproc("rand_seed")
        b.dmproc("roll")
        b.dmproc("round")
        b.dmproc("sin")
        b.dmproc("sqrt")
        b.dmproc("tan")

        # generics
        b.dmproc("length")

        # constructors
        b.dmproc("icon")
        b.dmproc("image")
        b.dmproc("list")
        b.dmproc("matrix")
        b.dmproc("regex")
        b.dmproc("rgb")

        # syntax
        b.dmproc("arglist")
        b.dmproc("initial")

        # filesystem
        b.dmproc("fcopy")
        b.dmproc("fcopy_rsc")
        b.dmproc("fdel")
        b.dmproc("fexists")
        b.dmproc("file")
        b.dmproc("file2text")
        b.dmproc("flist")

        # conversion
        b.dmproc("ascii2text")
        b.dmproc("json_decode")
        b.dmproc("json_encode")
        b.dmproc("list2params")
        b.dmproc("params2list")
        b.dmproc("num2text")
        b.dmproc("rgb2num")
        b.dmproc("text2ascii")
        b.dmproc("text2file")
        b.dmproc("text2num")
        b.dmproc("text2path")
        b.dmproc("time2text")

        # text
        b.dmproc("addtext")
        b.dmproc("ckey")
        b.dmproc("ckeyEx")
        b.dmproc("cKey")
        b.dmproc("cmptext")
        b.dmproc("cmptextEx")
        b.dmproc("copytext")
        b.dmproc("findlasttext")
        b.dmproc("findlasttextEx")
        b.dmproc("findtext")
        b.dmproc("findtextEx")
        b.dmproc("html_decode")
        b.dmproc("html_encode")
        b.dmproc("jointext")
        b.dmproc("lentext")
        b.dmproc("lowertext")
        b.dmproc("md5")
        b.dmproc("nonspantext")
        b.dmproc("REGEX_QUOTE")
        b.dmproc("replacetext")
        b.dmproc("replacetextEx")
        b.dmproc("sha1")
        b.dmproc("sorttext")
        b.dmproc("sorttextEx")
        b.dmproc("spantext")
        b.dmproc("splicetext")
        b.dmproc("splittext")
        b.dmproc("text")
        b.dmproc("uppertext")
        b.dmproc("url_decode")
        b.dmproc("url_encode")

        # input
        b.dmproc("alert")
        b.dmproc("input")

        # server
        b.dmproc("shell")
        b.dmproc("shutdown")
        b.dmproc("startup")

        # runtime
        b.dmproc("sleep")
        b.dmproc("spawn")

        # client
        b.dmproc("ftp")
        b.dmproc("load_resource")

        # display
        b.dmproc("animate")
        b.dmproc("browse")
        b.dmproc("browse_rsc")
        b.dmproc("filter")
        b.dmproc("flick")
        b.dmproc("gradient")
        b.dmproc("icon_states")
        b.dmproc("link")
        b.dmproc("output")
        b.dmproc("stat")
        b.dmproc("statpanel")
        b.dmproc("turn")
        b.dmproc("winclone")
        b.dmproc("winexists")
        b.dmproc("winget")
        b.dmproc("winset")
        b.dmproc("winshow")

        #sound
        b.dmproc("sound")

        # pixel movement
        b.dmproc("bounds")
        b.dmproc("bounds_dist")
        b.dmproc("obounds")
        
        # map
        b.dmproc("block")
        b.dmproc("get_dir")
        b.dmproc("get_dist")
        b.dmproc("get_step")
        b.dmproc("get_step_away")
        b.dmproc("get_step_rand")
        b.dmproc("get_step_to")
        b.dmproc("get_step_towards")
        b.dmproc("hearers")
        b.dmproc("locate")
        b.dmproc("missile")
        b.dmproc("ohearers")
        b.dmproc("orange")
        b.dmproc("oview")
        b.dmproc("oviewers")
        b.dmproc("range")
        b.dmproc("step")
        b.dmproc("step_away")
        b.dmproc("step_rand")
        b.dmproc("step_to")
        b.dmproc("step_towards")
        b.dmproc("view")
        b.dmproc("viewers")
        b.dmproc("walk")
        b.dmproc("walk_away")
        b.dmproc("walk_rand")
        b.dmproc("walk_to")
        b.dmproc("walk_towards")

        # savefile
        b.dmproc("issaved")

        #reflection
        b.dmproc("hascall")
        b.dmproc("isarea")
        b.dmproc("isfile")
        b.dmproc("isicon")
        b.dmproc("islist")
        b.dmproc("isloc")
        b.dmproc("ismob")
        b.dmproc("ismovable")
        b.dmproc("isnull")
        b.dmproc("isnum")
        b.dmproc("isobj")
        b.dmproc("ispath")
        b.dmproc("istext")
        b.dmproc("isturf")
        b.dmproc("istype")
        b.dmproc("typesof")

### Exception
        with b.dmtype("exception"):
            b.parent_type("datum")
                
            b.dmvar("name")
            b.dmvar("file")
            b.dmvar("line")
            b.dmvar("desc")

###### Datum
        with b.dmtype("datum"):
            b.dmproc("Del")
            b.dmproc("New")
            b.dmproc("Read")
            b.dmproc("Topic")
            b.dmproc("Write")

            b.dmvar("parent_type")
            b.dmvar("tag")
            b.dmvar("type")
            b.dmvar("vars")

###### Atom
        with b.dmtype("atom"):
            b.parent_type("datum")

            Stdlib.Common.mouse_procs(b)
            Stdlib.Common.movement_procs(b)
            b.dmproc("Stat")

            Stdlib.Common.appearance_vars(b)
            b.dmvar("appearance")
            b.dmvar("contents")
            b.dmvar("loc")
            b.dmvar("x", allow_override=False)
            b.dmvar("y", allow_override=False)
            b.dmvar("z", allow_override=False)

            b.dmproc("x", allow_override=False)
            b.dmproc("y", allow_override=False)
            b.dmproc("z", allow_override=False)

        with b.dmtype("atom", "movable"):
            b.parent_type("atom")
            b.dmproc("Bump")
            b.dmproc("Move")

            b.dmvar("animate_movement")
            b.dmvar("bound_x")
            b.dmvar("bound_y")
            b.dmvar("bound_width")
            b.dmvar("bound_height")
            b.dmvar("locs") 
            b.dmvar("screen_loc")
            b.dmvar("glide_size")
            b.dmvar("particles")
            b.dmvar("step_size")
            b.dmvar("step_x")
            b.dmvar("step_y")
            
        with b.dmtype("area"):
            b.parent_type("atom")

        with b.dmtype("turf"):
            b.parent_type("atom")

        with b.dmtype("obj"):
            b.parent_type("atom", "movable")

        with b.dmtype("mob"):
            b.parent_type("atom","movable")
            b.dmproc("Login")
            b.dmproc("Logout")

            b.dmvar("ckey")
            b.dmvar("client")
            b.dmvar("group")
            b.dmvar("key")
            b.dmvar("see_in_dark")
            b.dmvar("see_infrared")
            b.dmvar("see_invisible")
            b.dmvar("sight")

### List
        with b.dmtype("list"):
            b.dmvar("associations")

            b.dmop("[]")
            b.dmop("?[]")

            b.dmop("+")
            b.dmop("+=")
            b.dmop("-")
            b.dmop("-=")
            b.dmop("|")
            b.dmop("|=")
            b.dmop("&")
            b.dmop("&=")
            b.dmop("^")
            b.dmop("^=")
            b.dmop("in")

            b.dmproc("Add")
            b.dmproc("Copy")
            b.dmproc("Cut")
            b.dmproc("Find")
            b.dmproc("Insert")
            b.dmproc("Join")
            b.dmproc("Remove")
            b.dmproc("Splice")
            b.dmproc("Swap")

            b.dmvar("len")

### Matrix
        with b.dmtype("matrix"):
            b.dmop("+")
            b.dmop("+=")
            b.dmop("-")
            b.dmop("-=")
            b.dmop("*")
            b.dmop("*=")
            b.dmop("/")
            b.dmop("/=")
            b.dmop("~")

            b.dmproc("Add")
            b.dmproc("Interpolate")
            b.dmproc("Invert")
            b.dmproc("Multiply")
            b.dmproc("New")
            b.dmproc("Scale")
            b.dmproc("Subtract")
            b.dmproc("Translate")
            b.dmproc("Turn")

### Regex
        with b.dmtype("regex"):
            b.dmproc("Find")
            b.dmproc("New")
            b.dmproc("Replace")

            b.dmvar("flags")
            b.dmvar("group")
            b.dmvar("index")
            b.dmvar("match")
            b.dmvar("name")
            b.dmvar("next")
            b.dmvar("text")

###### World
        with b.dmtype("world"):
            b.dmproc("AddCredits")
            b.dmproc("ClearMedal")
            b.dmproc("Del")
            b.dmproc("Export")
            b.dmproc("Error")
            b.dmproc("GetConfig")
            b.dmproc("GetCredits")
            b.dmproc("GetMedal")
            b.dmproc("GetScopes")
            b.dmproc("Import")
            b.dmproc("ISBanned")
            b.dmproc("IsSubscribed")
            b.dmproc("New")
            b.dmproc("OpenPort")
            b.dmproc("PayCredits")
            b.dmproc("Profile")
            b.dmproc("Reboot")
            b.dmproc("Repop")
            b.dmproc("SetConfig")
            b.dmproc("SetMedal")
            b.dmproc("SetScores")
            b.dmproc("Topic")

            b.dmvar("address")
            b.dmvar("area")
            b.dmvar("byond_build")
            b.dmvar("byond_version")
            b.dmvar("cache_lifespan")
            b.dmvar("contents")
            b.dmvar("cpu")
            b.dmvar("executor")
            b.dmvar("fps")
            b.dmvar("game_state")
            b.dmvar("host")
            b.dmvar("hub")
            b.dmvar("hub_password")
            b.dmvar("icon_size")
            b.dmvar("internet_address")
            b.dmvar("log")
            b.dmvar("loop_checks")
            b.dmvar("map_cpu")
            b.dmvar("map_format")
            b.dmvar("maxx")
            b.dmvar("maxy")
            b.dmvar("maxz")
            b.dmvar("mob")
            b.dmvar("movement_mode")
            b.dmvar("name")
            b.dmvar("params")
            b.dmvar("port")
            b.dmvar("realtime")
            b.dmvar("reachable")
            b.dmvar("sleep_offline")
            b.dmvar("status")
            b.dmvar("system_type")
            b.dmvar("tick_lag")
            b.dmvar("tick_usage")
            b.dmvar("time")
            b.dmvar("timeofday")
            b.dmvar("timezone")
            b.dmvar("turf")
            b.dmvar("url")
            b.dmvar("version")
            b.dmvar("view")
            b.dmvar("visibility")

### Database
        with b.dmtype("database"):
            b.dmproc("Close")
            b.dmproc("Error")
            b.dmproc("ErrorMsg")
            b.dmproc("New")
            b.dmproc("Open")

### Database/Query
            with b.dmtype("query"):
                b.dmproc("Add")
                b.dmproc("Clear")
                b.dmproc("Close")
                b.dmproc("Columns")
                b.dmproc("Error")
                b.dmproc("ErrorMsg")
                b.dmproc("Execute")
                b.dmproc("GetColumn")
                b.dmproc("GetRowData")
                b.dmproc("New")
                b.dmproc("NextRow")
                b.dmproc("Reset")
                b.dmproc("RowsAffected")

### Savefile
        with b.dmtype("savefile"):
            b.dmop(">>")
            b.dmop("<<")

            b.dmproc("ExportText")
            b.dmproc("Flush")
            b.dmproc("ImportText")
            b.dmproc("Lock")
            b.dmproc("New")
            b.dmproc("Unlock")

            b.dmvar("cd")
            b.dmvar("dir")
            b.dmvar("eof")
            b.dmvar("name")

### Client
        with b.dmtype("client"):
            b.parent_type("datum")

            Stdlib.Common.mouse_procs(b)
                
            b.dmproc("AllowUpload")
            b.dmproc("Center")
            b.dmproc("CheckPassport")
            b.dmproc("Command")
            b.dmproc("Export")
            b.dmproc("GetAPI")
            b.dmproc("Import")
            b.dmproc("IsByondMember")
            b.dmproc("MeasureText")
            b.dmproc("SendPage")
            b.dmproc("SetAPI")
            b.dmproc("SoundQuery")

            b.dmproc("Move")
            b.dmproc("Stat")

            b.dmproc("North")
            b.dmproc("Northeast")
            b.dmproc("Northwest")
            b.dmproc("South")
            b.dmproc("Southeast")
            b.dmproc("Southwest")
            b.dmproc("West")
            b.dmproc("East")

            b.dmvar("address")
            b.dmvar("authenticate")
            b.dmvar("bounds")
            b.dmvar("byond_build")
            b.dmvar("byond_version")
            b.dmvar("CGI")
            b.dmvar("ckey")
            b.dmvar("color")
            b.dmvar("command_text")
            b.dmvar("connection")
            b.dmvar("control_freak")
            b.dmvar("computer_id")
            b.dmvar("default_verb_category")
            b.dmvar("dir")
            b.dmvar("edge_limit")
            b.dmvar("eye")
            b.dmvar("fps")
            b.dmvar("gender")
            b.dmvar("glide_size")
            b.dmvar("images")
            b.dmvar("inactivity")
            b.dmvar("key")
            b.dmvar("lazy_eye")
            b.dmvar("mob")
            b.dmvar("mouse_pointer_icon")
            b.dmvar("perspective")
            b.dmvar("pixel_x")
            b.dmvar("pixel_y")
            b.dmvar("pixel_w")
            b.dmvar("pixel_z")
            b.dmvar("pixel_z")
            b.dmvar("preload_rsc")
            b.dmvar("screen")
            b.dmvar("script")
            b.dmvar("show_map")
            b.dmvar("show_popup_menus")
            b.dmvar("show_verb_panel")
            b.dmvar("statobj")
            b.dmvar("statpanel")
            b.dmvar("tick_lag")
            b.dmvar("timezone")
            b.dmvar("verbs")
            b.dmvar("view")
            b.dmvar("virtual_eye")

        with b.dmtype("icon"):
            b.dmproc("Blend")
            b.dmproc("Crop")
            b.dmproc("DrawBox")
            b.dmproc("Flip")
            b.dmproc("GetPixel")
            b.dmproc("Height")
            b.dmproc("IconStates")
            b.dmproc("Insert")
            b.dmproc("MapColors")
            b.dmproc("New")
            b.dmproc("Scale")
            b.dmproc("SetIntensity")
            b.dmproc("Shift")
            b.dmproc("SwapColor")
            b.dmproc("Turn")
            b.dmproc("Width")

### Image
        with b.dmtype("image"):
            b.parent_type("atom")

            Stdlib.Common.appearance_vars(b)
            b.dmvar("loc")

### Mutable_appearance
        with b.dmtype("mutable_appearance"):
            b.parent_type("image")

### Sound
        with b.dmtype("sound"):
            b.dmvar("file")
            b.dmvar("repeat")
            b.dmvar("wait")
            b.dmvar("channel")
            b.dmvar("volume")
            b.dmvar("frequency")
            b.dmvar("offset")
            b.dmvar("len")
            b.dmvar("pan")
            b.dmvar("priority")
            b.dmvar("status")
            b.dmvar("x")
            b.dmvar("y")
            b.dmvar("z")
            b.dmvar("falloff")
            b.dmvar("environment")
            b.dmvar("echo")

        return b

    class Common(object):
        def mouse_procs(b):
            b.dmproc("Click")
            b.dmproc("DblClick")
            b.dmproc("MouseDown")
            b.dmproc("MouseDrag")
            b.dmproc("MouseDrop")
            b.dmproc("MouseEntered")
            b.dmproc("MouseExited")
            b.dmproc("MouseMove")
            b.dmproc("MouseUp")
            b.dmproc("MouseWheel")

        def movement_procs(b):
            b.dmproc("Cross")
            b.dmproc("Crossed")
            b.dmproc("Enter")
            b.dmproc("Entered")
            b.dmproc("Exit")
            b.dmproc("Exited")
            b.dmproc("Uncross")
            b.dmproc("Uncrossed")

        def appearance_vars(b):
            # cloned vars
            b.dmvar("alpha")
            b.dmvar("appearance_flags")
            b.dmvar("blend_mode")
            b.dmvar("color")
            b.dmvar("desc")
            b.dmvar("gender")
            b.dmvar("icon")
            b.dmvar("icon_state")
            b.dmvar("invisibility")
            b.dmvar("infra_luminosity")
            b.dmvar("filters")
            b.dmvar("layer")
            b.dmvar("luminosity")
            b.dmvar("maptext")
            b.dmvar("maptext_width")
            b.dmvar("maptext_height")
            b.dmvar("maptext_x")
            b.dmvar("maptext_y")
            b.dmvar("mouse_over_pointer")
            b.dmvar("mouse_drag_pointer")
            b.dmvar("mouse_drop_pointer")
            b.dmvar("mouse_drop_zone")
            b.dmvar("mouse_opacity")
            b.dmvar("name")
            b.dmvar("opacity")
            b.dmvar("overlays")
            b.dmvar("override")
            b.dmvar("pixel_x")
            b.dmvar("pixel_y")
            b.dmvar("pixel_w")
            b.dmvar("pixel_z")
            b.dmvar("plane")
            b.dmvar("render_source")
            b.dmvar("render_target")
            b.dmvar("suffix")
            b.dmvar("text")
            b.dmvar("transform")
            b.dmvar("underlays")
            b.dmvar("vis_flags")

            # non-cloned vars
            b.dmvar("density")
            b.dmvar("dir")
            b.dmvar("verbs")        

class Display:
    def raw_lines(text):
        i = 1
        for line in text.split('\n'):
            yield {"lineno":i, "text":line}
            i += 1

    def byond_errors(text):
        for line in text.split('\n'):
            if line == "":
                continue
            ss = line.split(':')
            if len(ss) < 3:
                continue
            if ss[2] in ['error', 'warning']:
                yield {"file":ss[0], "lineno":int(ss[1]), "type":ss[2], "msg":":".join(ss[3:]), "text":line}
    
    def opendream_errors(text):
        for line in text.split('\n'):
            if not line.startswith("Error at "):
                continue
            ss = line.split(" ")
            if len(ss) < 3:
                continue
            # TODO: this probably will not work for filename with spaces
            ff = ss[2].split(":")
            if len(ff) >= 2:
                yield {"file":ff[0].strip(), "lineno":int(ff[1]), "msg":" ".join(ss[3:]), "text":line }

        
    # TODO: this may not work for macro expansion
    def clparse_tree(text):
        for line in text.split('\n'):
            ss = line.split("|||")
            if len(ss) != 3:
                continue
            ff = ss[2].split(":")
            if len(ff) >= 2:
                yield {"file":ff[0].strip(), "lineno":int(ff[1]), "text":line }

    def dm_file_info( text ):
        info = {"lines": sorted(list(Display.raw_lines( text )), key=lambda line: line["lineno"]) }
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        return info

    def byond_errors_info( text ):
        info = {"lines": sorted(list(Display.byond_errors(text)), key=lambda line: line["lineno"]) }
        info["lines"] = [ line for line in info["lines"] if line["file"] == 'test.dm' ]
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        return info

    def opendream_errors_info( text ):
        info = {"lines": sorted(list(Display.opendream_errors(text)), key=lambda line: line["lineno"]) }
        info["lines"] = [ line for line in info["lines"] if line["file"] == 'test.dm' ]
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        return info

    def collider_errors_info( model ):
        info = {"lines":[]}
        for lineno, errid in model["errors"]:
            info["lines"].append( {"lineno":lineno, "text":f"{lineno}:{errid}"} )
        info["width"] = 20
        return info

    def clparser_tree_info( text ):
        info = {"lines": sorted(list(Display.clparse_tree(text)), key=lambda line: line["lineno"]) }
        info["lines"] = [ line for line in info["lines"] if line["file"] == 'test.dm' and line["lineno"] != 0 ]
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
        for i in range(0, len(info["lines"])-1):
            if info["lines"][i+1]["lineno"] == 0:
                info["lines"][i+1]["lineno"] = info["lines"][i]["lineno"]
        return info

    def merge_text(*infos):
        c_is = len(infos)*[0]
        first_line = min( line["lineno"] for info in infos for line in info["lines"] )
        last_line =  max( line["lineno"] for info in infos for line in info["lines"] )
        current_line = first_line
        text = ""
        while current_line <= last_line:
            next_line = ""
            did_inc = False
            for i, info in enumerate(infos):
                c_i = c_is[i]
                if c_i >= len(info["lines"]):
                    next_line += ''.ljust( info["width"], " ")
                    continue
                lineinfo = info["lines"][c_i]
                if lineinfo["lineno"] == current_line:
                    c_is[i] += 1
                    did_inc = True
                    next_line += lineinfo["text"].ljust( info["width"], ' ')
                else:
                    next_line += ''.ljust( info["width"], " ")
            if did_inc:
                text += f'{current_line}'.ljust(6, ' ') + '|' + next_line
                text += '\n'
                continue

            current_line += 1
        return text
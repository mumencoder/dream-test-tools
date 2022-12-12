
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
            if ss[2] in ['error', 'warning']:
                yield {"file":ss[0], "lineno":int(ss[1]), "type":ss[2], "msg":ss[3], "text":line}
    
    # TODO: this may not work for macro expansion
    def clparse_tree(text):
        for line in text.split('\n'):
            ss = line.split("|||")
            if len(ss) != 3:
                continue
            ff = ss[2].split(":")
            if len(ff) >= 2:
                yield {"file":ff[0].strip(), "lineno":int(ff[1]), "text":line }

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
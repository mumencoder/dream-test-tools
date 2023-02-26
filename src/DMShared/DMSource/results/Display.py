
from ...common import *
class Display:
    def sparse_to_full(values):
        result = io.StringIO()
        current_line = 1
        it = iter(values)
        try:
            next_line = next(it)
        except StopIteration:
            return []
        while current_line <= next_line["line"]:
            if current_line == next_line["line"]:
                result.write( str(next_line["value"]) )
                current_line += 1
                result.write('\n')
                try:
                    next_line = next(it)
                except StopIteration:
                    pass
            else:
                current_line += 1
                result.write('\n')
        return result.getvalue()

    def raw_lines(text):
        i = 1
        for line in text.split('\n'):
            yield {"lineno":i, "text":line}
            i += 1

    def dm_file_info( text ):
        info = {"lines": sorted(list(Display.raw_lines( text )), key=lambda line: line["lineno"]) }
        info["width"] = max( [len(line["text"]) for line in info["lines"] ]) + 8
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

    def all(tenv):
        if tenv.attr_exists('.test.files.dm_file'):
            tenv.attr.test.dm_lines["dm_file"] = Display.dm_file_info( tenv.attr.test.files.dm_file )

    def process_errors(env):
        if env.attr_exists('.test.metadata.paths.byond_errors'):
            with open( env.attr.test.root_dir / env.attr.test.metadata.paths.byond_errors, "r") as f:
                byond_errors = Display.byond_errors_info( f.read() )
                for line in byond_errors["lines"]:
                    Errors.byond_category(line)
        if env.attr_exists('.test.metadata.paths.opendream_errors'):
            with open( env.attr.test.root_dir / env.attr.test.metadata.paths.opendream_errors, "r") as f:
                opendream_errors = Display.opendream_errors_info( f.read() )
                for line in opendream_errors["lines"]:
                    Errors.opendream_category(line)
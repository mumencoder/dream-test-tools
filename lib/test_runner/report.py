
import html, os, json
import collections
import test_runner

import Shared

class Report(object):
    def load_result(env):
        env.attr.result.ccode = Shared.File.read_if_exists(env.attr.test.base_dir / "compile.returncode.log")
        if env.attr.result.ccode is None:
            return False

        env.attr.result.ccode = int(env.attr.result.ccode)
        
        #print( env.attr.test.base_dir / "compile.returncode.log", env.attr.result.ccode )
        if env.attr.result.ccode == 0:
            runlog_path = env.attr.test.base_dir / "run_log.out"
            env.attr.result.runlog = Shared.File.read_if_exists(runlog_path, lambda s: json.loads(s) )
        return True

    def match_ccode(env1, env2):
        return (env1.attr.result.ccode == 0) and (env2.attr.result.ccode == 0)

    def match_runlog(env1, env2):
        return Shared.match(env1.attr.result.runlog, env2.attr.result.runlog) is None

    def match_test(env1, env2):
        ccode_compare = Report.match_ccode(env1, env2) 
        if env1.attr.result.ccode == 0 and ccode_compare is True: 
            return Report.match_runlog(env1, env2)
        return ccode_compare

    def compare_results(benv, oenv, nenv):
        o_compare = Report.match_test(benv, oenv)
        n_compare = Report.match_test(benv, nenv)

        if o_compare is True and n_compare is False:
            result = "breaking"
        elif o_compare is False and n_compare is True:
            result = "fixing"
        elif o_compare is False and n_compare is False:
            result = "mismatch"
        elif o_compare is True and n_compare is True:
            result = "match"

        return result

class CompileReport(object):
    def display_result(self, result):
        return f"""
<tr>
    <td>{result["1"]["config"]["test.id"]}</td>
    <td>{result["note"]}</td>
    <td><a href="#{result["1"]["config"]["test.id"]}">View</a></td>
</tr>
"""

    def get_report(self):
        self.process_results()
        self.row_tables = collections.defaultdict(str)

        result_output = ""
        for result in self.results:
            result_output += f"""
<hr size=5 noshade id="{result["1"]["config"]["test.id"]}">
{self.string(result["1"]["config"]['test.id'])}<br>
<pre><code>{self.string(result["1"]["config"]['test.text'])}</code></pre>
<hr>
"""
            if result["category"] == "compile code mismatch":
                if result["1"]["ccode"] == 0:
                    result_output += f'<pre><code>{self.string(json.dumps(result["1"]["runlog"]))}</code></pre><hr>'                
                else:
                    result_output += f"""
<pre><code>{self.string(result["1"]["ctext"])}</code></pre>
<hr>
"""
                if result["2"]["ccode"] == 0:
                    result_output += f'<pre><code>{self.string(json.dumps(result["2"]["runlog"]))}</code></pre><hr>'                
                else:
                    result_output += f"""
<pre><code>{self.string(result["2"]["ctext"])}</code></pre>
<hr>
"""
            if result["category"] == "runlog mismatch":
                result_output += f"""
<pre><code>{self.string(json.dumps(result["1"]["runlog"]))}</code></pre><hr>
"""
                result_output += f"""
<pre><code>{self.string(json.dumps(result["2"]["runlog"]))}</code></pre><hr>
"""

        for category in self.category_rows.keys():
            for result in self.category_rows[category]:
                self.row_tables[category] += self.display_result(result)

        s = f"""
<html>
    <head></head>
    <body>
    <table border=1px>
        <caption>{len(self.category_rows["compile code mismatch"])} compile returncode mismatch</caption>
        <tr>
            <th>Test ID</th>
            <th>Info</th>
            <th>Output</th>
        </tr>
        {self.row_tables["compile code mismatch"]}
    </table>
    <table border=1px>
        <caption>{len(self.category_rows["runlog mismatch"])} runlog mismatch</caption>
        <tr>
            <th>Test ID</th>
            <th>Info</th>
            <th>Output</th>
        </tr>
        {self.row_tables["runlog mismatch"]}
    </table>
    <hr>
    <table border=1px>
        <caption>{len(self.category_rows["same"])} matched</caption>
        <tr>
            <th>Test ID</th>
            <th>Info</th>
            <th>Output</th>
        </tr>
        {self.row_tables["same"]}
    </table>
    {result_output}
    </body>
</html>
"""

        return s

class CompareReport(object):
    def __init__(self, install):
        self.install = install
        self.results = []

    def string(self, s): 
        return html.escape(s)

    def add_result(self, config):
        result = {}
        result['config'] = config = config.branch("1")

        config['test.install'] = self.install
        test_runner.get_test_info(config, 'curated')
        json_path = config['test.base_dir'] / "clopen_result.json"

        if os.path.exists(json_path):
            with open(json_path) as f:
                result["json"] = json.load(f)
        else:
            result["json"] = None
        self.results.append( result )

    def get_report(self):
        uncategorized_ct = 0
        uncategorized_rows = ""
        json_missing_ct = 0
        json_missing_rows = ""
        uncaught_exception_ct = 0
        uncaught_exception_rows = ""
        byond_error_ct = 0
        byond_error_rows = ""
        mismatch_error_ct = 0
        mismatch_error_rows = ""
        no_mismatch_ct = 0
        no_mismatch_rows = ""

        result_output = ""
        for result in self.results:
            if result["json"] is None:
                json_missing_ct += 1
                json_missing_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
            elif "uncaught_exception" in result["json"] and result["json"]["uncaught_exception"] is True:
                uncaught_exception_ct += 1
                uncaught_exception_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""

            elif "byond_compile_error" in result["json"]:
                byond_error_ct += 1
                byond_error_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
            elif "mismatch_count" in result["json"]:
                if result["json"]["mismatch_count"] == 0:
                    no_mismatch_ct += 1
                    no_mismatch_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
                else:
                    mismatch_error_ct += 1
                    mismatch_error_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
            else:
                uncategorized_ct += 1
                uncategorized_rows += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
            result_output += f"""
<hr id="{result["config"]["test.id"]}">
<pre><code>{self.string(result["config"]['test.text'])}</code></pre>
"""

        s = f"""
<html>
    <head></head>
    <body>
    <table border=1px>
        <caption>{uncategorized_ct} uncategorized rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {uncategorized_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{json_missing_ct} json missing rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {json_missing_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{uncaught_exception_ct} uncaught exception rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {uncaught_exception_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{mismatch_error_ct} mismatch rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {mismatch_error_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{byond_error_ct} byond error rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {byond_error_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{no_mismatch_ct} validated rows</caption>
        <tr>
            <th>Test ID</th>
            <th>Output</th>
        </tr>
        {no_mismatch_rows}
    </table>
    {result_output}
    </body>
</html>
"""
        return s

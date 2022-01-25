
import html, os, json
import collections
import test_runner

import Shared

class CompileReport(object):
    def __init__(self, install1, install2):
        self.install1 = install1
        self.install2 = install2
        self.results = []

    def string(self, s): 
        return html.escape(s)

    def load_result(self, config, install):
        result = {}
        result['config'] = config = config.branch("result").copy()
        config['test.install'] = install
        test_runner.get_test_info(config, 'curated')
        result["ccode"] = int(Shared.File.read_if_exists(config['test.base_dir'] / "compile.returncode.txt"))
        result["ctext"] = Shared.File.read_if_exists( config['test.base_dir'] / "compile.txt")
        if result["ccode"] == 0:
            runlog_path = config['test.base_dir'] / "run_log.out"
            result["runlog"] = Shared.File.read_if_exists(runlog_path, lambda s: json.loads(s) )
        return result

    def add_result(self, config):
        result = {}
        result["1"] = self.load_result(config, self.install1)
        result["2"] = self.load_result(config, self.install2)
        self.results.append( result )
        
    def result_compiled(self, result):
        return (result["1"]["ccode"] == 0) and (result["2"]["ccode"] == 0)

    def result_runlog(self, result):
        return Shared.match(result["1"]["runlog"], result["2"]["runlog"])

    def get_result_summary(self):
        summ = {}
        for result in self.results:
            summ_result = {}
            summ[result["1"]['config']['test.id']] = summ_result
            summ_result["category"] = result["category"]
        return summ

    def process_results(self):
        self.category_rows = collections.defaultdict(list)
        for result in self.results:
            result["note"] = ""
            if self.result_compiled(result):
                result["runlog_match"] = self.result_runlog(result)
                if self.result_runlog(result) is None:
                    result["category"] = "same"
                else:
                    result["category"] = "runlog mismatch"
            else:
                result["category"] = "compile code mismatch"

            self.category_rows[result["category"]].append( result )

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
                    result_output += f"{self.install1['install_id']}: No errors<br><hr>"                
                else:
                    result_output += f"""
<pre><code>{self.string(result["1"]["ctext"])}</code></pre>
<hr>
"""
                if result["2"]["ccode"] == 0:
                    result_output += f"{self.install2['install_id']}: No errors<br><hr>"                
                else:
                    result_output += f"""
<pre><code>{self.string(result["2"]["ctext"])}</code></pre>
<hr>
"""
            if result["category"] == "runlog mismatch":
                result_output += f"""
<pre><code>{self.string(json.dumps(result["1"]["runlog"]))}</code></pre>
"""
                result_output += f"""
<pre><code>{self.string(json.dumps(result["2"]["runlog"]))}</code></pre>
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

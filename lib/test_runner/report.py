
import html, os, json
import test_runner

class CompileReport(object):
    def __init__(self, install1, install2):
        self.install1 = install1
        self.install2 = install2
        self.id1 = f"{install1['platform']}.{install1['install_id']}"
        self.id2 = f"{install2['platform']}.{install2['install_id']}"
        self.results = []

    def string(self, s): 
        return html.escape(s)

    def add_result(self, config):
        result = {}
        result['config1'] = config1 = config.branch("1")
        result['config2'] = config2 = config.branch("2")

        config1['test.platform'] = self.install1['platform']
        config1['test.install_id'] = self.install1['install_id']
        test_runner.get_test_info(config1, 'curated')
        code1_path = config1['test.base_dir'] / "compile.returncode.txt"

        config2['test.platform'] = self.install2['platform']
        config2['test.install_id'] = self.install2['install_id']
        test_runner.get_test_info(config2, 'curated')
        code2_path = config2['test.base_dir'] / "compile.returncode.txt"

        if os.path.exists(code1_path):
            with open(code1_path) as f:
                result["code1"] = int(f.read())
        else:
            result["code1"] = None
        if os.path.exists(code2_path):
            with open(code2_path) as f:
                result["code2"] = int(f.read())
        else:
            result["code2"] = None
        self.results.append( result )

    def get_report(self):
        diff_total = 0
        diff_result_rows = ""
        match_total = 0
        match_result_rows = ""
        result_output = ""
        for result in self.results:
            if (result["code1"] == 0) != (result["code2"] == 0):
                diff_total += 1
                diff_result_rows += f"""
<tr>
    <td>{result["config1"]["test.id"]}</td>
    <td>{result["code1"]}</td>
    <td>{result["code2"]}</td>
    <td><a href="#{result["config1"]["test.id"]}">View</a>
</tr>
"""
            else:
                match_total += 1
                match_result_rows += f"""
<tr>
    <td>{result["config1"]["test.id"]}</td>
    <td>{result["code1"]}</td>
    <td>{result["code2"]}</td>
    <td><a href="#{result["config1"]["test.id"]}">View</a>
</tr>
"""
            result_output += f"""
<hr id="{result["config1"]["test.id"]}">
<pre><code>{self.string(result["config1"]['test.text'])}</code></pre>
"""

        s = f"""
<html>
    <head></head>
    <body>
    <table border=1px>
        <caption>{diff_total} mismatch rows</caption>
        <tr>
            <th>Test ID</th>
            <th>{self.id1}</th>
            <th>{self.id2}</th>
            <th>Output</th>
        </tr>
        {diff_result_rows}
    </table>
    <hr>
    <table border=1px>
        <caption>{match_total} matched rows</caption>
        <tr>
            <th>Test ID</th>
            <th>{self.id1}</th>
            <th>{self.id2}</th>
            <th>Output</th>
        </tr>
        {match_result_rows}
    </table>
    {result_output}
    </body>
</html>
"""

        return s

class CompareReport(object):
    def __init__(self, install):
        self.install = install
        self.id = f"{install['platform']}.{install['install_id']}"
        self.results = []

    def string(self, s): 
        return html.escape(s)

    def add_result(self, config):
        result = {}
        result['config'] = config = config.branch("1")

        config['test.platform'] = self.install['platform']
        config['test.install_id'] = self.install['install_id']
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

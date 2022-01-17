
import html, os
import test_runner

class TestReport(object):
    def __init__(self, install1, install2):
        self.install1 = install1
        self.install2 = install2
        self.id1 = f"{install1['platform']}.{install1['install_id']}"
        self.id2 = f"{install2['platform']}.{install2['install_id']}"
        self.results = []

    def string(self, s): 
        return s
        return html.escape(s).replace('\n', '<br>' ).replace('\t', '&ensp;')

    def compile_result(self, config):
        result = {}
        result['config1'] = config1 = config.branch("1")
        result['config2'] = config2 = config.branch("2")

        config1['test.platform'] = self.install1['platform']
        config1['test.install_id'] = self.install1['install_id']
        test_runner.get_test_info(config1)
        code1_path = config1['test.base_dir'] / "compile.returncode.txt"

        config2['test.platform'] = self.install2['platform']
        config2['test.install_id'] = self.install2['install_id']
        test_runner.get_test_info(config2)
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

    def compile_report(self):
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
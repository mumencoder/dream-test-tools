
import html

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

    def compare(self, config):
        result = {}
        result["config"] = config
        with open(config['test.base_dir'] / f"{self.id1}.compile.returncode.txt") as f:
            result["code1"] = f.read()
        with open(config['test.base_dir'] / f"{self.id2}.compile.returncode.txt") as f:
            result["code2"] = f.read()
        self.results.append( result )

    def print(self):
        s1 = ""
        s2 = ""
        for result in self.results:
            s1 += f"""
<tr>
    <td>{result["config"]["test.id"]}</td>
    <td>{result["code1"]}</td>
    <td>{result["code2"]}</td>
    <td><a href="#{result["config"]["test.id"]}">View</a>
</tr>
"""
            s2 += f"""
<hr id="{result["config"]["test.id"]}">
<pre><code>{self.string(result["config"]['test.text'])}</code></pre>
"""

        s = f"""
<html>
    <head></head>
    <body>
    <table border=1px>
        <tr>
            <th>Test ID</th>
            <th>{self.id1}</th>
            <th>{self.id2}</th>
            <th>Output</th>
        </tr>
        {s1}
    </table>
    {s2}
    </body>
</html>
"""


        return s
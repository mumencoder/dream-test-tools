
import requests
import json

class Github(object):
    @staticmethod
    def list_pull_requests(env):
        url = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}/pulls'
        headers = {'Accept': 'application/vnd.github.v3+json'}

        r = requests.get(url, headers=headers)
        return json.loads(r.text)

    @staticmethod
    def pull_request_to_install(pr):
        r = {'type':'repo'}
        r['url'] = pr["head"]["repo"]["clone_url"]
        r['branch'] = {'remote':'origin', 'name':pr["head"]["ref"]}
        return r

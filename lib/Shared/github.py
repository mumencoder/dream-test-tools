
import requests
import json

class Github(object):
    @staticmethod 
    def make_request(env, url):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Bad status code")
        env.attr.github.limit_remaining = r.headers['x-ratelimit-remaining']
        return json.loads(r.text)

    @staticmethod
    def list_pull_requests(env):
        url = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}/pulls'
        return Github.make_request(env, url)

    @staticmethod
    def get_pull_request(env):
        url = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}/pulls/{env.attr.github.number}'
        return Github.make_request(env, url)

    @staticmethod
    def pull_request_to_install(pr):
        r = {'type':'repo'}
        r['url'] = pr["head"]["repo"]["clone_url"]
        r['branch'] = {'remote':'origin', 'name':pr["head"]["ref"]}
        return r

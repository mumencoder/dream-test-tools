
import requests
import json

import Shared

class Github(object):
    @staticmethod 
    def make_request(env, url):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Bad status code", url, r.status_code)
        env.attr.github.limit_remaining = r.headers['x-ratelimit-remaining']
        return json.loads(r.text)

    @staticmethod
    def prepare(env):
        github = env.prefix('.github')
        github.endpoint = 'api.github.com'
        github.url = f'https://github.com/{github.owner}/{github.repo}'
        github.repo_id = f'{github.repo}.{github.owner}'

    @staticmethod
    def list_pull_requests(env):
        url = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}/pulls'
        return Github.make_request(env, url)

    @staticmethod
    def get_pull_request(env):
        url = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}/pulls/{env.attr.github.number}'
        return Github.make_request(env, url)

    @staticmethod
    def load_pull_request(env, pull_info):
        env.attr.pull.id = f'github.{env.attr.github.repo_id}.pulls.{pull_info["number"]}'
        env.attr.source.id = f'github.{env.attr.github.repo_id}.{pull_info["merge_commit_sha"]}'
        # TODO: this should not really have a default
        env.attr.git.repo.remote = 'origin'
        env.attr.git.repo.remote_ref = pull_info["merge_commit_sha"]

    @staticmethod
    def pull_request_buildable(env):
        env.attr.scheduler.event_name = f'{env.attr.pull.id}.build'
        pull_info = env.attr.pull.info
        build_result = Shared.Scheduler.get_result(env)

        if build_result is None or 'recent_build_sha' not in build_result:
            build = True
        elif build_result['recent_build_sha'] != pull_info['merge_commit_sha']:
            build = True
        else: 
            build = False

        return build
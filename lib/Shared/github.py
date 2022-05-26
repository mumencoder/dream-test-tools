
import requests
import json, datetime, time

import Shared

class Github(object):
    @staticmethod 
    def make_request(env, url):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Bad status code", url, r.status_code)
        env.attr.github.limit_remaining = r.headers['x-ratelimit-remaining']
        print("remaining github requests: ", env.attr.github.limit_remaining)
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
    def parse_datetime(s):
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def list_all_commits(env, existing_commits=None):
        newest_commit = None
        oldest_commit = None
        have_newest = False
        have_oldest = False
        commits = {}

        url_prefix = f'https://{env.attr.github.endpoint}/repos/{env.attr.github.owner}/{env.attr.github.repo}'

        def add_commits(new_commits):
            nonlocal newest_commit
            nonlocal oldest_commit
            for commit in new_commits:
                commits[ commit["sha"] ] = commit
                commit[ "time" ] = Github.parse_datetime( commit["commit"]["committer"]["date"] )

                if newest_commit is None:
                    newest_commit = oldest_commit = commit

                if commit[ "time" ] > newest_commit["time"]:
                    newest_commit = commit
                if commit[ "time" ] < oldest_commit["time"]:
                    oldest_commit = commit

        if existing_commits is None:
            existing_commits = {}
            url = f'{url_prefix}/commits?per_page=100'
            more_commits = Github.make_request(env, url)
            if len(more_commits) == 0:
                raise Exception("no results on fresh listing")
            add_commits(more_commits)
        else:
            add_commits(existing_commits)

        while not have_newest or not have_oldest:
            print(newest_commit["time"], oldest_commit["time"])
            if not have_newest:
                url = f'{url_prefix}/commits?per_page=100&since={newest_commit["commit"]["committer"]["date"]}'
                more_commits = Github.make_request(env, url)
                if len(more_commits) == 1:
                    if more_commits[0]["sha"] == newest_commit["sha"]:
                        have_newest = True
                elif len(more_commits) == 0:
                    have_newest = True
                add_commits(more_commits)
            if not have_oldest:
                url = f'{url_prefix}/commits?per_page=100&until={oldest_commit["commit"]["committer"]["date"]}'
                more_commits = Github.make_request(env, url)
                if len(more_commits) == 1:
                    if more_commits[0]["sha"] == oldest_commit["sha"]:
                        have_oldest = True
                elif len(more_commits) == 0:
                    have_oldest = True
                add_commits(more_commits)
            time.sleep(1.0)
        return commits

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
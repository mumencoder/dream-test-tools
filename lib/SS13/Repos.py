
import Shared

class Repos(object):
    @staticmethod
    async def iter_community_repos(config):
        for repo_info in config['ss13.repo_infos']:
            config = repo_info['config'] = config.branch('update')
            config['ss13.base_dir']  = config['ss13.dirs.repos'] / repo_info['name']
            config['ss13.repo_info'] = repo_info
            yield config

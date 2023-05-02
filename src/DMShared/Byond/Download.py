
from ..common import *

class Download(object):
    @staticmethod
    def parse_official_filename(filename):
        def readint(pos):
            while pos < len(filename) and filename[pos].isnumeric():
                pos += 1
            return pos
        
        pos = 0
        result = {"filename":filename}
        if (new_pos := readint(pos)) != pos:
            result["major"] = filename[pos:new_pos]
            pos = new_pos
        else:
            return {"type":"unknown"}

        if filename[pos] != ".":
            return {"type":"unknown"}
        pos += 1

        if (new_pos := readint(pos)) != pos:
            result["minor"] = filename[pos:new_pos]
            pos = new_pos
        else:
            return {"type":"unknown"}

        if filename[pos] != "_":
            return {"type":"unknown"}
        pos += 1

        if filename[pos:] in [
            "byond_freebsd.zip", "byond_linux.zip",
            "byondexe.zip", "byond_setup.zip", "byond.zip", "byond.exe",
            "byond_netbsd.zip", "byond_openbsd.zip", "byond_linux_old_glibc.zip",
            "byond_macosx.zip",
            "byond_mfc120.zip",
            ]:
            result["type"] = filename[pos:]
            return result
        else:
            return {"type":"unknown"}

    @staticmethod
    def from_official_source(env):
        env.attr.byond.version_directory_url = "https://www.byond.com/download/build/"

    @staticmethod
    def fetch_version_directory(env):
        result = requests.get(env.attr.byond.version_directory_url)
        if result.status_code == 200:
            env.attr.byond.version_directory = requests.get(env.attr.byond.version_directory_url).content
        else:
            raise Exception(result.status_code)
        
    @staticmethod
    def parse_apache_dir(env, page):
        soup = BeautifulSoup(page, 'html.parser')

        for link in soup.find_all('pre')[0].find_all('a'):
            yield link

    @staticmethod
    def iter_version_directories(env):
        for link in Download.parse_apache_dir(env, env.attr.byond.version_directory):
            if link['href'].startswith('?') or link['href'].startswith('/'):
                continue
            if not link['href'][0].isnumeric():
                continue
            yield link

    @staticmethod
    def fetch_version_files(env):
        for link in Download.iter_version_directories(env):
            url = env.attr.byond.version_directory_url + link['href']
            result = requests.get(url)
            if result.status_code == 200:                
                for link in Download.parse_apache_dir(env, result.content):
                    if link['href'].startswith('?') or link['href'].startswith('/'):
                        continue
                    yield {"url":url + link['href'], "file":link['href']}
            else:
                raise Exception(result.status_code)
            time.sleep(2.0)
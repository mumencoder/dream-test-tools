
import Byond
from DTT import App

class Main(App):
    def run(self, version=None):
        if version is None: 
            version = self.config['byond.version']
        Byond.Install.download(self.config, version)

main = Main()
main.run()
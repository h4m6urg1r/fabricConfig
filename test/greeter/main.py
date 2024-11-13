import fabric
from os.path import (
	join,
	dirname
)
from greeter.utils.helpers import applySCSS

def main():
	applySCSS(file = join(dirname(__file__), 'assets', 'main.scss'))
	fabric.start()

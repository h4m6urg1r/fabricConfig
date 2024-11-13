import sass
from loguru import logger
from fabric.utils import set_stylesheet_from_string

def applySCSS(file, *args):
	logger.info(f"[CSS] Applying: {file}")
	return set_stylesheet_from_string(sass.compile(filename = file, output_style = "compressed"))

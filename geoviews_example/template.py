import os
import jinja2


loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
env = jinja2.Environment(loader=loader)
INDEX = env.get_template("templates/index.html")

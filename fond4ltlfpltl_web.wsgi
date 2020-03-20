activate_this = '/home/fuggitti/virtualenvs/fond4ltlf/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

#!/usr/bin/python3.6
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/fond4ltlfpltl_web")

from fond4ltlfpltl_web import app as application

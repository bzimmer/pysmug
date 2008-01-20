
"""SmugMug API"""

__all__ = ("__version__", "SmugMug", "SmugMugException", "login")

__version__ = '0.1'

from pysmug.smugmug import SmugMug, SmugMugException

def login(conf=None):
  import os
  if not conf:
    home = os.environ.get("HOME", None)
    if not home:
      raise ValueError("unknown home directory")
    conf = os.path.join(home, ".pysmugrc")
    if not os.path.exists(conf):
      raise ValueError("'%s' not found" % (conf))
  config = eval(open(conf).read())
  return SmugMug().login_withPassword(config["username"], config["password"], config["apikey"])


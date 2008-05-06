
from pysmug import login, SmugMug, SmugMugException

class Example:
  def __init__(self, conf=None, apiKey=None):
    self.m = login(conf) if conf else SmugMug().login_anonymously(APIKey=apiKey)

  def example(self, *args, **kwargs):
    pass

def main(cls):
  import optparse, logging
  from getpass import getpass
  
  p = optparse.OptionParser()
  p.add_option("-f", "--conf", default=None, action="store")
  p.add_option("-a", "--apikey", default=None, action="store")
  p.add_option("-v", "--debug", default=False, action="store_true")
  opts, args = p.parse_args()

  if opts.debug:
    logging.basicConfig(level=logging.DEBUG)

  if not args:
    args = [630992] # Street Photos from Moon River Photography

  example = cls(opts.conf, opts.apikey)
  for arg in args:
    try:
      example.example(arg)
    except SmugMugException, e:
      # too bad error codes are not consistent
      if e.message in ("invalid user", "invalid session"):
        p.error("login with email address and password")
      raise
  raise SystemExit()


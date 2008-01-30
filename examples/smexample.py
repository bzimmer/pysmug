
from pysmug import SmugMug, SmugMugException

class Example:
  def __init__(self, APIKey, EmailAddress=None, Password=None):
    self.m = SmugMug()
    if EmailAddress and Password:
      self.m.login_withPassword(APIKey=APIKey,
        EmailAddress=EmailAddress, Password=Password)
    else:
      self.m.login_anonymously(APIKey=APIKey)

  def example(self, *args, **kwargs):
    pass

def main(cls):
  import optparse, logging
  from getpass import getpass
  
  apiKey = "1XhqbbxNfSygsmVReGQ8nek8D2Dz8F61"
  
  p = optparse.OptionParser()
  p.add_option("-a", "--apikey", default=apiKey, action="store")
  p.add_option("-e", "--email", action="store")
  p.add_option("-v", "--debug", action="store_true", default=False)
  opts, args = p.parse_args()

  if opts.debug:
    logging.basicConfig(level=logging.DEBUG)

  if not args:
    args = [630992] # Street Photos from Moon River Photography

  password = getpass() if opts.email else None
  example = cls(opts.apikey, opts.email, password)
  for arg in args:
    try:
      example.example(arg)
    except SmugMugException, e:
      # too bad error codes are not consistent
      if e.message in ("invalid user", "invalid session"):
        p.error("login with email address and password")
      raise
  raise SystemExit()


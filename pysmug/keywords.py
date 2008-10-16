
def _smugbool(value):
  """Formats the value into an appropriate boolean representation for SmugMug.
  The SmugMug API will accept boolean values as either C{true|false} or C{1|0} so
  this function accepts both strings and boolean/integer Python values and returns
  the appropriate representation for the API.  There is no corresponding mapping
  for inbound data.
  """
  if value is None:
    return value
  if isinstance(value, str):
    return value.lower()
  return int(value)

__apikeys = dict((x.lower(), (x, f)) for x, f in (
  ("APIKey", None),
  ("AlbumKey", None),
  ("EmailAddress", None),
  ("FileName", None),
  ("Heavy", _smugbool),
  ("ImageKey", None),
  ("PasswordHash", None),
  ("Pretty", _smugbool),
  ("Strict", _smugbool),
))
"""A mapping between lower-cased names and their SmugMug API case and formatting
function.  This is a one-way mapping usually used to format a Python C{bool}
into its numeric value usable by the SmugMug API.
"""

def _smugmug_keyword(k, v=None):
  if k == "method":
    return False, k, v
  if k[0].isupper():
    return False, k, v
  lk = k.lower()
  if lk in __apikeys:
    key, func = __apikeys[lk]
    # del kwargs[k]
    # kwargs[key] = func(v) if func else v
    return True, key, func(v) if func else v
  else:
    # del kwargs[k]
    if lk.endswith("id"):
      # kwargs[lk[:-2].title() + "ID"] = v
      return True, lk[:-2].title() + "ID", v
    else:
      # kwargs[lk.title()] = v
      return True, lk.title(), v

def smugmug_keyword(keyword):
  t, k, v = _smugmug_keyword(keyword)
  return k

def smugmug_keywords(fn):
  """Prepare the keywords for sending to SmugMug.

  The following operations are performed::
    1. If the key is "method", continue.
    2. If the key starts with an upper case letter, continue.
    3. If the key is in {methods.apikeys}, replace the key.
    4. If the key ends with {id}, upper case the first letter
       and {ID} and replace the key.
    5. Else, upper case the first letter only and replace the
       key.

  @param fn: the decorated function
  """
  def mg(*args, **kwargs):
    items = kwargs.items()
    for k, v, in items:
      t, key, value = _smugmug_keyword(k, v)
      if t:
        del kwargs[k]
        kwargs[key] = value
      # if k == "method":
      #   continue
      # if k[0].isupper():
      #   continue
      # lk = k.lower()
      # if lk in __apikeys:
      #   key, func = __apikeys[lk]
      #   del kwargs[k]
      #   kwargs[key] = func(v) if func else v
      # else:
      #   del kwargs[k]
      #   if lk.endswith("id"):
      #     kwargs[lk[:-2].title() + "ID"] = v
      #   else:
      #     kwargs[lk.title()] = v
    return fn(*args, **kwargs)
  return mg


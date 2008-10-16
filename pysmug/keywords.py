from pysmug.methods import apikeys

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
      if k == "method":
        continue
      if k[0].isupper():
        continue
      lk = k.lower()
      if lk in apikeys:
        key, func = apikeys[lk]
        del kwargs[k]
        kwargs[key] = func(v) if func else v
      else:
        del kwargs[k]
        if lk.endswith("id"):
          kwargs[lk[:-2].title() + "ID"] = v
        else:
          kwargs[lk.title()] = v
    return fn(*args, **kwargs)
  return mg

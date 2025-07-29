# module imports
from . import prompt

# stdlib imports
from dataclasses import dataclass
import os.path
from pathlib import Path
import re

CALLABLE_RE = re.compile(r'^\s*((app|serv)[a-z0-9_]*)\s+=', re.IGNORECASE)
WSGI_MODULES = [mod.strip() for mod in '''
Flask 
django
wsgi
falcon
tornado
wsgiref
pyramid
masonite
fastapi
'''.strip().splitlines()]

WSGI_MODULES_RE = re.compile('|'.join(WSGI_MODULES))


@dataclass
class WSGI:
  path: Path
  AppName: str = 'app'
  Callable: str = 'app'

  @classmethod
  def from_path(cls, path, app='app', ):
    path = Path(path).absolute()
    return WSGI(path.parent, path.stem, app)

def _possible_files(path):
  """Find *.py files that may match WSGI apps/frameworks."""
  path = Path(os.path.expanduser(path))

  for f in path.glob('**/*.py'):
    # Skip site-packages
    if 'site-packages' in f.parts:
      continue

    if _file_could_match(f):
      yield f

def _file_could_match(path):
  """Return True if this *may* be a WSGI app file."""
  with open(path) as f:
    for line in f:
      if WSGI_MODULES_RE.search(line):
        return True
  
  return False

def _get_callable(path):
  # Get the callable
  with open(path) as fobj:
    for line in fobj:
      if m := CALLABLE_RE.search(line):
        c = m.group(1)
        if prompt.ask_yes_no(f'Is this your WSGI callable? {c}'):
          return c

  # Couldn't find the callable
  msg = 'What is your WSGI callable?'
  c = prompt.update_field(msg, 'app')

  return c

def find_all(path='.'):
  """Attempt to find all WSGI apps in the given directory."""

  found = False

  # Find the path to the *.py
  for f in _possible_files(path):
    msg = f"Add to module.xml? {f}"
    if prompt.ask_yes_no(msg):
      found = True
      c = _get_callable(f)
      yield WSGI.from_path(f, c)
      continue

  # *.py not found.  Ask the user for the path
  if not found:
    path = None
    while not path or not path.exists() or path.suffix != '.py':
      msg = 'What is the path to your WSGI *.py file?'
      path = prompt.update_field(msg)

    c = _get_callable(path)

    yield WSGI.from_path(path, c)

def find(path='.'):
  for wsgi in find_all(path):
    return wsgi

  return None

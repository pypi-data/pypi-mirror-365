# module imports
from .module import ModuleFile
from .web_app import WebApplication, FileCopy
from . import prompt
from . import wsgi_finder

# stdlib imports
from importlib.metadata import version
from pathlib import Path
import sys

USAGE = '''
Usage: wsgi-to-zpm [OPTION]

  -v, --version
                 Print version
  -h, --help
                 Print this help

wsgi-to-zpm will create or modify an InterSystems ZPM/IPM module.xml file
based on WSGI web applications found in the current directory.
'''

def _version():
  print(f'wsgi-to-zpm version: {version("wsgi_to_zpm")}')

def _help():
  print(USAGE)

def main():
  args = sys.argv[1:]
  
  for arg in args:
    if arg in ('-v', '--version'):
      _version()
      sys.exit()
    elif arg in ('-h', '--help'):
      _help()
      sys.exit()

  this_dir = Path('.')

  f = ModuleFile(this_dir / 'module.xml', create_if_missing=True)

  # Find the WSGI apps from this directory
  for wsgi in wsgi_finder.find_all(Path('.')):
    # Determine the project name
    name = wsgi.path.absolute().name
    mod_name = f.get_name()

    if name != mod_name:
      new_name = None
      msg = f'Would you like to update the project name to "{name}"?'
      if prompt.ask_yes_no(msg):
        new_name = name
      elif prompt.ask_yes_no('Would you like to update the project name?'):
        new_name, modified = prompt.update_field('Project Name', f.get_name())
        if not modified:
          new_name = None

      if new_name:
        f.set_name(new_name)

    # Determine local files to include
    basepath = wsgi.path.absolute().relative_to(this_dir.absolute())

    local_choices = [this_dir]

    for part in basepath.parts:
      prev = local_choices[-1]
      local_choices.append(prev / part)

    local_choices.append(basepath / (wsgi.AppName + '.py'))

    local_dir = None
    print('')
    msg = 'Choose a local path to include in the module'
    for local_dir, idx in prompt.choose(msg, local_choices):
      pass

    # Determine installed url
    basepath = wsgi.path.absolute().relative_to(this_dir.absolute())

    url_choices = []

    for part in reversed(basepath.parts):
      if len(url_choices) > 0:
        prev = url_choices[-1]
      else:
        prev = ''

      url_choices.append('/' + part + prev)

    if len(url_choices) == 0:
      url_choices.append('/' + wsgi.AppName)

    if mod_name != name:
      url_choices = [
        *url_choices,
        *['/' + (new_name or mod_name) + url for url in url_choices],
      ]

    url = None
    print('')
    msg = 'Choose a URL for your WSGI app'
    for url, idx in prompt.choose(msg, url_choices, allow_freetext=True):
      pass

    # Build xml and add to module.xml
    # Vars: new_name, wsgi, local_dir, url
    possible_dests = [
      '${libDir}',
      '${mgrDir}',
      '${cspDir}',
    ]
    msg = 'Choose a base directory to install this WSGI app in'
    for dest_base, idx in prompt.choose(msg, possible_dests, allow_freetext=True):
      # Don't put slashes after ${variable} entries
      dest_base = dest_base.replace('}/', '}')

      # Make sure dest_base ends with either } or /
      last_char = dest_base[-1]
      if last_char not in '}/':
        dest_base += '/'

    dest = str(wsgi.path.relative_to(this_dir.absolute()))
    if dest == '.':
      dest = dest_base
    else:
      dest = dest_base + dest

    filecopy = FileCopy.from_path(local_dir, dest)
    el = filecopy.add_to_module_xml(f)

    web_app = WebApplication(url)
    web_app.WSGIAppLocation = dest
    web_app.WSGIAppName = wsgi.AppName
    web_app.WSGICallable = wsgi.Callable
    el = web_app.add_to_module_xml(f)

    print("")

  # Save any changes to module.xml
  if f.modified:
    print(f"Saving {f.path}")
    f.save()

if __name__ == '__main__':
  main()

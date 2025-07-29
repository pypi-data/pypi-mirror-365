# pip imports
from lxml import etree

# stdlib imports
from dataclasses import dataclass
from pathlib import Path

#####################################################
# <FileCopy Name="webapps/hc_export_editor" Target="${libdir}hc_export_editor/"/>
# <WebApplication
#   Url="/my/wsgi/app"
#   AutheEnabled="#{ 32 + ${authUnauthenticated} }"
#   Description="My WSGI application"
#   MatchRoles=":${globalsDbRole}"
#   NameSpace="${ns}"
#   WSGIAppLocation="${libdir}my-wsgi-app/"
#   WSGIAppName="app"
#   WSGICallable="app"
#   DispatchClass="%SYS.Python.WSGI"
# />
#####################################################

@dataclass
class FileCopy:
  Name:str
  Target:str
  Overlay:bool = False
  Defer:bool = False

  @classmethod
  def from_path(self, path, target):
    path = Path(path)

    name = str(path)
    if path.is_dir():
      name += '/'

    return FileCopy(name, target)

  def add_to_module_xml(self, f):
    f.modified = True

    # Find existing FileCopy entries with this name
    # and remove them.
    for fc in f.mod.xpath('./FileCopy'):
      if fc.attrib['Name'] == self.Name:
        print(f'Removing existing FileCopy: {etree.tostring(fc).decode("utf-8")}')
        f.mod.remove(fc)

    el = etree.SubElement(f.mod, 'FileCopy')
    
    el.attrib['Name'] = self.Name
    el.attrib['Target'] = self.Target

    if self.Overlay:
      el.attrib['Overlay'] = 'true'

    if self.Defer:
      el.attrib['Defer'] = 'true'

    return el

@dataclass
class WebApplication:
  Url:str
  AutheEnabled:str = "32"
  Description:str = ""
  MatchRoles:str = ":${globalsDbRole}"
  NameSpace:str = "${ns}"
  WSGIAppLocation:str = "${libdir}my-wsgi-app/"
  WSGIAppName:str = "app"
  WSGICallable:str = "app"
  DispatchClass:str = "%SYS.Python.WSGI"

  def add_to_module_xml(self, f):
    f.modified = True

    # Find existing FileCopy entries with this name
    # and remove them.
    for webapp in f.mod.xpath('./WebApplication'):
      webapp_path = webapp.attrib.get('WSGIAppLocation', '') + webapp.attrib.get('WSGIAppName', '')
      self_path = self.WSGIAppLocation + self.WSGIAppName

      if webapp.attrib['Url'] == self.Url or webapp_path == self_path:
        print(f'Removing existing WebApplication: {etree.tostring(webapp).decode("utf-8")}')
        f.mod.remove(webapp)

    el = etree.SubElement(f.mod, 'WebApplication')
    
    el.attrib['Url'] = self.Url
    el.attrib['AutheEnabled'] = self.AutheEnabled
    el.attrib['Description'] = self.Description
    el.attrib['MatchRoles'] = self.MatchRoles
    el.attrib['NameSpace'] = self.NameSpace
    el.attrib['WSGIAppLocation'] = self.WSGIAppLocation
    el.attrib['WSGIAppName'] = self.WSGIAppName
    el.attrib['WSGICallable'] = self.WSGICallable
    el.attrib['DispatchClass'] = self.DispatchClass

    return el

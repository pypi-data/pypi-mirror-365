# pip imports
from lxml import etree

# stdlib imports
from importlib import resources
import os.path
from pathlib import Path

class ModuleFile:
  def __init__(self, path = 'module.xml', create_if_missing=False):
    self.orig_path = path
    self.path = Path(os.path.expanduser(path))
    self._tree = None
    self._src_path = None
    self.modified = False
    self.save_on_modify = True

    if not self.path.exists():
      if not create_if_missing:
        raise FileNotFoundError(path)

      # Open the default module.xml and write it to file
      with open(self.path, 'w') as f:
        print(f'Creating module.xml')
        f.write(resources.read_text('wsgi_to_zpm', 'module.xml'))

    if not self.path.is_file():
      raise ValueError(f'Not a file: {path}')

  @property
  def tree(self):
    if not self._tree:
      with open(self.path) as f:
        self._tree = etree.parse(f)

    return self._tree

  @property
  def src_path(self):
    if not self._src_path:
      self._src_path = ([el.text for el in self.xpath('//SourcesRoot')] or ['src'])[0]

    return Path(self._src_path)

  def print_tree(self):
    etree.indent(self.tree, '  ')
    print(etree.tostring(self.tree, pretty_print=True).decode('utf-8'))

  def xpath(self, q):
    return self.tree.xpath(q)

  def xpath_first(self, q):
    for el in self.tree.xpath(q):
      return el

    return None

  @property
  def mod(self):
    return self.xpath_first('/Export/Document/Module')

  @property
  def author(self):
    return self.xpath_first('/Export/Document/Module/Author')

  def get_name(self):
    el = self.mod.find('Name')
    if el == None:
      return None
    else:
      return el.text

  def set_name(self, value):
    # TODO: Add name checking
    doc = self.mod.getparent()
    doc.attrib['name'] = f'{value}.ZPM'

    el = self.mod.find('Name')

    if el == None:
      el = etree.SubElement(f.mod, 'Name')

    el.text = value
    self.modified = True

  def format_xml(self):
    # TODO: Sort elements
    etree.indent(self.tree, '  ')

  def save(self, filepath = 'module.xml', force = False):
    if not self.save_on_modify:
      return False

    if force or (self.modified and self._tree != None):
      self.format_xml()

      with open(filepath, 'wb') as f:
        self._tree.write(f)
        self.modified = False
        self._tree == None
        return True

    return False

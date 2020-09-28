import xml.etree.ElementTree as ET
tree = ET.parse('resp.xml')
root = tree.getroot()
inf = {}
for i in root.find('overlays'):
    inf['overlay' + str(i.attrib['number'])] = i.text
inf['preview'] = root.find('preview').text
inf['active'] = root.find('active').text
print(inf)
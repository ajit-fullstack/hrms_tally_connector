import re

class Utils():
    def clean_tally_xml(xml_text):
        xml_text = re.sub(r'&#\d+;', '', xml_text)
        xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', xml_text)
        return xml_text
    
    def get_text(parent, tag):
        for child in parent:
            if child.tag.endswith(tag):
                return child.text
        return None
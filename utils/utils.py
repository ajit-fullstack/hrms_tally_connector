import re

class Utils():
    @staticmethod
    def clean_tally_xml(xml_text: str) -> str:
        xml_text = re.sub(r'&#\d+;', '', xml_text)
        xml_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', xml_text)
        xml_text = re.sub(r'<(/?)UDF:', r'<\1', xml_text)
        xml_text = re.sub(r'xmlns:UDF="[^"]*"', '', xml_text)
        xml_text = xml_text.replace("&apos;", "'")
        return xml_text
    
    @staticmethod
    def parse_tally_qty(qty_string: str):
        if not qty_string:
            return 1, None

        qty_string = qty_string.strip()
        match = re.search(r'([\d.]+)\s*[/ ]?\s*([A-Za-z]+)', qty_string)

        if match:
            quantity = float(match.group(1))
            unit = match.group(2).upper()
            return quantity, unit

        return 1, None
    
    @staticmethod
    def get_text(parent, tag):
        for child in parent:
            if child.tag.endswith(tag):
                return child.text
        return None
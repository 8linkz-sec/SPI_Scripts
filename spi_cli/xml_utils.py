"""XML parsing utilities for APIs that return XML instead of JSON."""
import xml.etree.ElementTree as ET


def xml_to_dict(element):
    """Convert XML element to dict recursively."""
    result = {}
    for child in element:
        child_data = xml_to_dict(child) if len(child) > 0 else child.text
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    return result


def parse_xml_response(text):
    """Parse XML response text and return as dict."""
    root = ET.fromstring(text)
    return {root.tag: xml_to_dict(root)}

import mysql.connector
import xml.etree.ElementTree as ET
import json
from datetime import datetime


XML_FILE = "C:\\Users\\kesh2\\Downloads\\official-cpe-dictionary_v2.3.xml\\official-cpe-dictionary_v2.3.xml"


DBCONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Keshav@1435',
    'database': 'cpe',
    'charset': 'utf8mb4'
}


ns = {
    'default': 'http://cpe.mitre.org/dictionary/2.0',
    'cpe23': 'http://scap.nist.gov/schema/cpe-extension/2.3',
    'meta': 'http://scap.nist.gov/schema/cpe-dictionary-metadata/0.2'
}

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    rows = []

    for idx, item in enumerate(root.findall('default:cpe-item', ns)):
        if idx >= 5000:
            break

        
        title_elem = item.find('default:title', ns)
        cpe_title = title_elem.text.strip() if title_elem is not None and title_elem.text else None

       
        cpe_22_uri = None
        cpe_22_deprecation_date = None

        
        cpe23_elem = item.find('cpe23:cpe23-item', ns)
        cpe_23_uri = cpe23_elem.attrib.get("name") if cpe23_elem is not None else None

        
        ref_elems = item.findall('default:references/default:reference', ns)
        reference_links = [ref.attrib.get('href') for ref in ref_elems if ref.attrib.get('href')]

        
        cpe_23_deprecation_date = None
        if cpe23_elem is not None:
            for child in cpe23_elem:
                tag = child.tag.split("}")[-1]
                if tag == "deprecation_date" and child.text:
                    try:
                        raw_date = child.text.strip()
                        formatted = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%b %d, %Y")
                        cpe_23_deprecation_date = formatted
                    except Exception as e:
                        print(f"[WARN] Skipping invalid date: {child.text}")

        
        rows.append((
            cpe_title,
            cpe_22_uri,
            cpe_23_uri,
            json.dumps(reference_links),
            cpe_22_deprecation_date,
            cpe_23_deprecation_date
        ))

    return rows

def insert_to_mysql(entries):
    conn = mysql.connector.connect(**DBCONFIG)
    cursor = conn.cursor()

    
    cursor.execute("DELETE FROM cpentries")
    cursor.execute("ALTER TABLE cpentries AUTO_INCREMENT = 1")

    query = """
        INSERT INTO cpentries (
            cpe_title,
            cpe_22_uri,
            cpe_23_uri,
            reference_links,
            cpe_22_deprecation_date,
            cpe_23_deprecation_date
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(query, entries)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{len(entries)} records inserted successfully.")

if __name__ == "__main__":
    parsed_data = parse_xml(XML_FILE)
    insert_to_mysql(parsed_data)
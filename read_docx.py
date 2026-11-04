import zipfile
import xml.etree.ElementTree as ET
import sys

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # The namespace for WordprocessingML
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Find all text elements
            paragraphs = []
            for p in tree.findall('.//w:p', namespaces=ns):
                texts = [node.text for node in p.findall('.//w:t', namespaces=ns) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
            
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    text = read_docx(r'C:\Users\shrey\Downloads\Lab Examination - sample Question.docx')
    with open('extracted_docx.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Done")

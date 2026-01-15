import io
import re


def extract_pdf_metadata(file_bytes):
    """Extract metadata from PDF bytes."""
    try:
        import PyPDF2
        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        info = pdf.metadata

        title = info.get('/Title', '') if info else ''
        author = info.get('/Author', '') if info else ''
        pages = len(pdf.pages)

        return title, author, pages
    except Exception:
        return '', '', 0


def extract_epub_metadata(file_bytes):
    """Extract metadata from EPUB bytes."""
    try:
        import zipfile
        from xml.etree import ElementTree as ET

        with zipfile.ZipFile(io.BytesIO(file_bytes)) as epub:
            # Find the OPF file
            container = epub.read('META-INF/container.xml')
            container_tree = ET.fromstring(container)

            ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            rootfile = container_tree.find('.//container:rootfile', ns)
            opf_path = rootfile.get('full-path')

            # Parse OPF for metadata
            opf_content = epub.read(opf_path)
            opf_tree = ET.fromstring(opf_content)

            dc_ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
            opf_ns = {'opf': 'http://www.idpf.org/2007/opf'}

            title_elem = opf_tree.find('.//{http://purl.org/dc/elements/1.1/}title')
            author_elem = opf_tree.find('.//{http://purl.org/dc/elements/1.1/}creator')

            title = title_elem.text if title_elem is not None else ''
            author = author_elem.text if author_elem is not None else ''

            return title, author, 0  # EPUB doesn't have simple page count
    except Exception:
        return '', '', 0


def parse_filename(filename):
    """Parse book info from filename patterns."""
    # Remove extension
    for ext in ['.pdf', '.epub', '.mobi', '.azw3', '.fb2']:
        filename = filename.replace(ext, '')

    # Try pattern: "Author - Title"
    if ' - ' in filename:
        parts = filename.split(' - ', 1)
        return parts[1].strip(), parts[0].strip()  # title, author

    # Try pattern: "Title (Author)"
    match = re.search(r'(.*?)\s*\((.*?)\)\s*$', filename)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # Try pattern: "Title by Author"
    match = re.search(r'(.*?)\s+by\s+(.*?)$', filename, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    return filename.strip(), ''


def extract_metadata(file_bytes, filename):
    """Extract metadata from file, falling back to filename parsing."""
    format = filename.split('.')[-1].lower() if '.' in filename else ''

    title, author, pages = '', '', 0

    if format == 'pdf':
        title, author, pages = extract_pdf_metadata(file_bytes)
    elif format == 'epub':
        title, author, pages = extract_epub_metadata(file_bytes)

    # Fallback to filename parsing if no metadata found
    if not title:
        title, author = parse_filename(filename)

    return title, author, pages, format

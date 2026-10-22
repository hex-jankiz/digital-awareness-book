import sys
import os
import re
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
import markdown

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path('c:/Users/lenovo/Desktop/jankiz/book_digital_awareness')
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
KIT_DIR = BASE_DIR / "commercial_publishing_kit"
KIT_DIR.mkdir(exist_ok=True)

print("=== Starting Complete Arabic Book Production System ===")

# -------------------------------------------------------------
# 1. READ ALL MANUSCRIPT FILES & EXTRACT STRUCTURE
# -------------------------------------------------------------
CHAPTER_SPECS = [
    ("00_front_matter.md", "الصفحات التمهيدية"),
    ("01_chapter_human_digital_age.md", "الفصل الأول: الإنسان في العصر الرقمي"),
    ("02_chapter_software_and_apps.md", "الفصل الثاني: كيف تعمل البرامج والتطبيقات؟"),
    ("03_chapter_programming_logic.md", "الفصل الثالث: البرمجة وفن التفكير المنطقي"),
    ("04_chapter_cybersecurity_risks.md", "الفصل الرابع: الأمن السيبراني وفهم المخاطر الرقمية"),
    ("05_chapter_protect_yourself_family.md", "الفصل الخامس: كيف تحمي نفسك وعائلتك رقمياً؟"),
    ("06_chapter_secure_software_systems.md", "الفصل السادس: بناء البرمجيات والأنظمة الآمنة"),
    ("07_chapter_ai_future.md", "الفصل السابع: الذكاء الاصطناعي ومستقبل الإنسان"),
    ("08_chapter_digital_missteps.md", "الفصل الثامن: أخطاء رقمية قد تغير حياتك"),
    ("09_chapter_tech_for_society.md", "الفصل التاسع: التكنولوجيا في خدمة المجتمع"),
    ("10_chapter_knowledge_to_impact.md", "الفصل العاشر: من المعرفة إلى التأثير"),
    ("11_conclusion_glossary_references.md", "الخاتمة ومعجم المصطلحات والمراجع")
]

raw_chapters = {}
for fname, title in CHAPTER_SPECS:
    fpath = BASE_DIR / fname
    with open(fpath, 'r', encoding='utf-8') as f:
        raw_chapters[fname] = f.read()

print(f"Successfully loaded {len(raw_chapters)} manuscript files.")

# Verify Front & Back Cover Images
front_cover_path = BASE_DIR / "front_cover.jpg"
back_cover_path = BASE_DIR / "back_cover.jpg"

if not front_cover_path.exists():
    raise FileNotFoundError("front_cover.jpg not found!")
if not back_cover_path.exists():
    raise FileNotFoundError("back_cover.jpg not found!")

# Copy covers to commercial kit
shutil.copy(front_cover_path, KIT_DIR / "book_cover_flat_front.jpg")
shutil.copy(back_cover_path, KIT_DIR / "book_cover_flat_back.jpg")
print("Verified & copied front and back cover images to publishing kit.")

# -------------------------------------------------------------
# 2. BUILD EPUB 3 PACKAGE
# -------------------------------------------------------------
print("\n--- Generating Valid EPUB 3 Digital Book ---")
epub_path = BASE_DIR / "book_digital_awareness.epub"
epub_kit_path = KIT_DIR / "book_digital_awareness.epub"

# Helper to convert Markdown to clean XHTML for EPUB
md_converter = markdown.Markdown(extensions=['extra', 'tables', 'fenced_code', 'nl2br', 'sane_lists'])

def md_to_xhtml(md_text):
    md_converter.reset()
    # Replace math blocks or markdown specific artifacts if any
    html = md_converter.convert(md_text)
    # Ensure closing tags for XHTML compliance
    html = re.sub(r'<hr>', '<hr />', html)
    html = re.sub(r'<br>', '<br />', html)
    html = re.sub(r'<img ([^>]+)>', r'<img \1 />', html)
    return html

# Structure EPUB entries
epub_entries = [
    ("cover.xhtml", "الغلاف", f'<div class="cover-container"><img src="images/front_cover.jpg" alt="غلاف كتاب الوعي الرقمي - جنكيز" class="cover-img" /></div>'),
    ("title.xhtml", "صفحة العنوان", md_to_xhtml('''# الوعي الرقمي
## المعرفة التي تحميك وتصنع مستقبلك

<div class="title-meta">

### تأليف: جنكيز

> «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».

---

**الطبعة الأولى — 2026م / 1447هـ**  
*جميع الحقوق محفوظة للمؤلف*

</div>''')),
]

# Extract sections from 00_front_matter.md
fm_text = raw_chapters["00_front_matter.md"]
# Split by page-break or headers
fm_parts = re.split(r'<div style="page-break-after: always;"></div>', fm_text)
if len(fm_parts) >= 4:
    # Copyright
    epub_entries.append(("copyright.xhtml", "حقوق النشر والبيانات الببليوغرافية", md_to_xhtml(fm_parts[1].strip())))
    # Dedication
    epub_entries.append(("dedication.xhtml", "الإهداء", md_to_xhtml(fm_parts[2].strip())))
    # Author word + Intro
    rest_fm = fm_parts[3].strip()
    intro_split = re.split(r'## المقدمة:', rest_fm)
    if len(intro_split) == 2:
        epub_entries.append(("author_word.xhtml", "كلمة المؤلف: جنكيز", md_to_xhtml(intro_split[0].strip())))
        epub_entries.append(("intro.xhtml", "مقدمة الكتاب", md_to_xhtml("## المقدمة:" + intro_split[1].strip())))
    else:
        epub_entries.append(("author_word.xhtml", "كلمة المؤلف والمقدمة", md_to_xhtml(rest_fm)))
else:
    epub_entries.append(("front_matter.xhtml", "الصفحات التمهيدية", md_to_xhtml(fm_text)))

# Chapters 1 to 10
for i in range(1, 11):
    fname = f"{i:02d}_chapter_" + [s[0].split('_chapter_')[1] for s in CHAPTER_SPECS if s[0].startswith(f"{i:02d}_")][0]
    title = [s[1] for s in CHAPTER_SPECS if s[0] == fname][0]
    ch_text = raw_chapters[fname]
    epub_entries.append((f"chapter_{i:02d}.xhtml", title, md_to_xhtml(ch_text)))

# Conclusion, Glossary, References, About Author, Back Cover from 11_
conc_text = raw_chapters["11_conclusion_glossary_references.md"]
conc_parts = re.split(r'<div style="page-break-after: always;"></div>', conc_text)
if len(conc_parts) >= 5:
    epub_entries.append(("conclusion.xhtml", "الخاتمة", md_to_xhtml(conc_parts[0].strip())))
    epub_entries.append(("glossary.xhtml", "معجم المصطلحات التقنية", md_to_xhtml(conc_parts[1].strip())))
    epub_entries.append(("references.xhtml", "قائمة المصادر والمراجع المعتمدة", md_to_xhtml(conc_parts[2].strip())))
    epub_entries.append(("about_author.xhtml", "عن المؤلف: جنكيز", md_to_xhtml(conc_parts[3].strip())))
    epub_entries.append(("back_cover.xhtml", "الغلاف الخلفي", f'<div class="cover-container"><img src="images/back_cover.jpg" alt="الغلاف الخلفي - الوعي الرقمي" class="cover-img" /></div>\n' + md_to_xhtml(conc_parts[4].strip())))
else:
    epub_entries.append(("conclusion_all.xhtml", "الخاتمة والمراجع", md_to_xhtml(conc_text)))

# Build EPUB zip
with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as ep:
    # 1. mimetype (must be first, uncompressed)
    ep.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    
    # 2. META-INF/container.xml
    container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
    ep.writestr("META-INF/container.xml", container_xml)
    
    # 3. OEBPS/style.css
    style_css = '''@charset "UTF-8";
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');

html, body {
  direction: rtl;
  text-align: justify;
  text-justify: inter-word;
  font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
  font-size: 1.15em;
  line-height: 1.85;
  color: #1e293b;
  background-color: #fcfbf9;
  margin: 0;
  padding: 0 4%;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
  color: #0f172a;
  text-align: right;
  line-height: 1.4;
  margin-top: 1.4em;
  margin-bottom: 0.6em;
  font-weight: 700;
}

h1 { font-size: 1.8em; color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3em; text-align: center; }
h2 { font-size: 1.4em; color: #0369a1; }
h3 { font-size: 1.2em; color: #334155; }

p { margin: 0.8em 0; }

blockquote {
  border-right: 4px solid #0ea5e9;
  background-color: rgba(14, 165, 233, 0.06);
  margin: 1.2em 0;
  padding: 0.8em 1.2em;
  border-radius: 4px;
  font-style: italic;
  color: #0f172a;
}

pre, code {
  font-family: "Courier New", Courier, monospace;
  direction: ltr;
  text-align: left;
  background-color: #f1f5f9;
  border-radius: 4px;
  padding: 0.2em 0.4em;
  font-size: 0.9em;
}

pre {
  padding: 1em;
  overflow-x: auto;
  border: 1px solid #cbd5e1;
  line-height: 1.5;
}

pre code {
  background: none;
  padding: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
}

th, td {
  border: 1px solid #cbd5e1;
  padding: 8px 12px;
  text-align: right;
}

th {
  background-color: #f1f5f9;
  font-weight: bold;
}

.cover-container {
  text-align: center;
  padding: 0;
  margin: 0;
}

.cover-img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.title-meta {
  text-align: center;
  margin-top: 2em;
}
'''
    ep.writestr("OEBPS/style.css", style_css)

    # 4. Images
    with open(front_cover_path, 'rb') as f:
        ep.writestr("OEBPS/images/front_cover.jpg", f.read())
    with open(back_cover_path, 'rb') as f:
        ep.writestr("OEBPS/images/back_cover.jpg", f.read())

    # 5. XHTML Chapters
    manifest_items = [
        '<item id="style" href="style.css" media-type="text/css"/>',
        '<item id="img_front" href="images/front_cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
        '<item id="img_back" href="images/back_cover.jpg" media-type="image/jpeg"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
    ]
    spine_items = []
    nav_links = []
    ncx_navpoints = []

    for idx, (filename, entry_title, xhtml_body) in enumerate(epub_entries, 1):
        item_id = f"item_{idx:02d}"
        manifest_items.append(f'<item id="{item_id}" href="{filename}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{item_id}"/>')
        nav_links.append(f'<li><a href="{filename}">{entry_title}</a></li>')
        ncx_navpoints.append(f'''  <navPoint id="navPoint-{idx}" playOrder="{idx}">
    <navLabel><text>{entry_title}</text></navLabel>
    <content src="{filename}"/>
  </navPoint>''')

        full_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ar" xml:lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <title>{entry_title}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{xhtml_body}
</body>
</html>'''
        ep.writestr(f"OEBPS/{filename}", full_xhtml)

    # 6. OEBPS/nav.xhtml
    nav_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ar" xml:lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <title>فهرس المحتويات</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>فهرس المحتويات</h1>
    <ol>
      {"".join(nav_links)}
    </ol>
  </nav>
</body>
</html>'''
    ep.writestr("OEBPS/nav.xhtml", nav_xhtml)

    # 7. OEBPS/toc.ncx
    toc_ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="ar" dir="rtl">
  <head>
    <meta name="dtb:uid" content="urn:uuid:digital-awareness-jankiz-2026"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>الوعي الرقمي: المعرفة التي تحميك وتصنع مستقبلك</text></docTitle>
  <docAuthor><text>جنكيز</text></docAuthor>
  <navMap>
{"".join(ncx_navpoints)}
  </navMap>
</ncx>'''
    ep.writestr("OEBPS/toc.ncx", toc_ncx)

    # 8. OEBPS/content.opf
    content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId" dir="rtl" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:digital-awareness-jankiz-2026</dc:identifier>
    <dc:title>الوعي الرقمي: المعرفة التي تحميك وتصنع مستقبلك</dc:title>
    <dc:creator>جنكيز</dc:creator>
    <dc:language>ar</dc:language>
    <dc:description>كتاب عربي تعليمي واحترافي في مجال الوعي الرقمي والأمن السيبراني والبرمجة والذكاء الاصطناعي — تأليف: جنكيز. «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».</dc:description>
    <dc:publisher>جنكيز (نشر مستقل)</dc:publisher>
    <dc:date>2026-10-23</dc:date>
    <dc:rights>© 2026 جنكيز. جميع الحقوق محفوظة.</dc:rights>
    <meta property="dcterms:modified">2026-10-23T12:00:00Z</meta>
    <meta property="page-progression-direction">rtl</meta>
  </metadata>
  <manifest>
    {"".join(manifest_items)}
  </manifest>
  <spine page-progression-direction="rtl" toc="ncx">
    {"".join(spine_items)}
  </spine>
</package>'''
    ep.writestr("OEBPS/content.opf", content_opf)

# Copy to publishing kit
shutil.copy(epub_path, epub_kit_path)
print(f"Generated EPUB successfully: {epub_path} ({os.path.getsize(epub_path):,} bytes)")


# -------------------------------------------------------------
# 3. BUILD PRINT & DIGITAL PDF (A5 Vector Publication)
# -------------------------------------------------------------
print("\n--- Generating Publication Print Document (HTML -> PDF) ---")
print_html_path = BASE_DIR / "print_book.html"
pdf_path = BASE_DIR / "book_digital_awareness_complete.pdf"
pdf_kit_path = KIT_DIR / "book_digital_awareness_complete.pdf"

# Combine full book into continuous print-ready pages with running headers, footers, and page breaks
print_sections_html = []

# Front Cover
print_sections_html.append('''<div class="print-page cover-page" style="page-break-after: always; padding: 0; margin: 0; width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f172a;">
  <img src="front_cover.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="غلاف كتاب الوعي الرقمي" />
</div>''')

# Inside Title Page
print_sections_html.append('''<div class="print-page inside-title-page" style="page-break-after: always; text-align: center; padding-top: 25mm;">
  <div style="font-size: 16pt; color: #64748b; font-weight: 600; margin-bottom: 12mm;">كتاب تخصصي في الثقافة التقنية والأمن السيبراني</div>
  <h1 style="font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif; font-size: 36pt; color: #1e3a8a; margin-bottom: 6mm; font-weight: 700;">الوعي الرقمي</h1>
  <div style="font-family: 'Noto Naskh Arabic', serif; font-size: 18pt; color: #0284c7; margin-bottom: 20mm; font-weight: 600;">المعرفة التي تحميك وتصنع مستقبلك</div>
  
  <div style="margin: 25mm auto; width: 60px; height: 3px; background: #fbbf24;"></div>
  
  <div style="font-size: 20pt; font-weight: 700; color: #0f172a; margin-bottom: 15mm;">تأليف: جنكيز</div>
  
  <blockquote style="font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif; font-size: 15pt; color: #334155; line-height: 1.8; margin: 0 auto; max-width: 80%; border: none; font-style: italic;">
    «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».
  </blockquote>
  
  <div style="margin-top: 30mm; font-size: 11pt; color: #94a3b8;">
    الطبعة الأولى — 2026م / 1447هـ
  </div>
</div>''')

# Front matter parts
for title, md_content in [
    ("صفحة حقوق النشر والبيانات الببليوغرافية", fm_parts[1].strip() if len(fm_parts) >= 4 else ""),
    ("الإهداء", fm_parts[2].strip() if len(fm_parts) >= 4 else ""),
    ("كلمة المؤلف والمقدمة", rest_fm if len(fm_parts) >= 4 else fm_text)
]:
    if md_content:
        converted = md_to_xhtml(md_content)
        print_sections_html.append(f'<div class="print-page front-matter-section" style="page-break-after: always;">\n{converted}\n</div>')

# Chapters 1 to 10
for i in range(1, 11):
    fname = f"{i:02d}_chapter_" + [s[0].split('_chapter_')[1] for s in CHAPTER_SPECS if s[0].startswith(f"{i:02d}_")][0]
    title = [s[1] for s in CHAPTER_SPECS if s[0] == fname][0]
    ch_text = raw_chapters[fname]
    converted = md_to_xhtml(ch_text)
    print_sections_html.append(f'''<div class="print-page chapter-page" style="page-break-before: always; page-break-after: always;" data-chapter="{title}">
  <div class="chapter-running-header" style="display: none;">{title}</div>
  {converted}
</div>''')

# Conclusion, Glossary, References, About Author
if len(conc_parts) >= 5:
    for part in conc_parts[:4]:
        converted = md_to_xhtml(part.strip())
        print_sections_html.append(f'<div class="print-page back-matter-section" style="page-break-before: always; page-break-after: always;">\n{converted}\n</div>')
else:
    converted = md_to_xhtml(conc_text)
    print_sections_html.append(f'<div class="print-page back-matter-section" style="page-break-before: always; page-break-after: always;">\n{converted}\n</div>')

# Back Cover
print_sections_html.append('''<div class="print-page back-cover-page" style="page-break-before: always; padding: 0; margin: 0; width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f172a;">
  <img src="back_cover.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="الغلاف الخلفي لكتاب الوعي الرقمي" />
</div>''')

full_print_html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>كتاب الوعي الرقمي — تأليف: جنكيز</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');
    
    @page {{
      size: A5 portrait;
      margin: 18mm 14mm 20mm 14mm;
      @bottom-center {{
        content: counter(page);
        font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
        font-size: 10pt;
        color: #475569;
      }}
    }}
    
    @page:first {{
      margin: 0;
      @bottom-center {{ content: none; }}
    }}

    * {{ box-sizing: border-box; }}
    
    body {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 11pt;
      line-height: 1.85;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
      text-align: justify;
      text-justify: inter-word;
    }}

    h1, h2, h3, h4 {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      color: #0f172a;
      break-after: avoid;
    }}

    h1 {{
      font-size: 20pt;
      color: #1e3a8a;
      text-align: center;
      margin-top: 15mm;
      margin-bottom: 8mm;
      border-bottom: 1.5pt solid #cbd5e1;
      padding-bottom: 4mm;
    }}

    h2 {{
      font-size: 14pt;
      color: #0284c7;
      margin-top: 10mm;
      margin-bottom: 4mm;
      border-right: 3pt solid #0284c7;
      padding-right: 3mm;
    }}

    h3 {{
      font-size: 12pt;
      color: #334155;
      margin-top: 7mm;
      margin-bottom: 3mm;
    }}

    p {{
      margin: 0 0 4mm 0;
      text-indent: 5mm;
    }}

    blockquote {{
      margin: 5mm 0;
      padding: 4mm 6mm;
      background: #f8fafc;
      border-right: 3pt solid #38bdf8;
      border-radius: 4px;
      font-style: italic;
      color: #1e293b;
    }}

    pre, code {{
      font-family: "Courier New", Courier, monospace;
      direction: ltr;
      text-align: left;
      font-size: 9pt;
      background: #f1f5f9;
      border-radius: 4px;
    }}

    pre {{
      padding: 4mm;
      border: 1pt solid #cbd5e1;
      white-space: pre-wrap;
      word-break: break-all;
      margin: 4mm 0;
      line-height: 1.45;
    }}

    code {{
      padding: 1mm 2mm;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 5mm 0;
      font-size: 9.5pt;
    }}

    th, td {{
      border: 1pt solid #cbd5e1;
      padding: 3mm;
      text-align: right;
    }}

    th {{
      background: #f1f5f9;
      font-weight: 700;
    }}

    ul, ol {{
      margin: 3mm 0;
      padding-right: 6mm;
    }}

    li {{
      margin-bottom: 2mm;
    }}

    hr {{
      border: none;
      border-top: 0.5pt solid #e2e8f0;
      margin: 6mm 0;
    }}
  </style>
</head>
<body>
{"".join(print_sections_html)}
</body>
</html>'''

with open(print_html_path, 'w', encoding='utf-8') as f:
    f.write(full_print_html)

print(f"Generated print HTML: {print_html_path} ({os.path.getsize(print_html_path):,} bytes)")

# Convert to PDF via Chrome Headless
print("Compiling PDF via Chrome Headless...")
cmd_pdf = [
    CHROME_PATH,
    '--headless',
    '--disable-gpu',
    '--run-all-compositor-stages-before-draw',
    f'--print-to-pdf={pdf_path}',
    '--no-pdf-header-footer',
    str(print_html_path.resolve())
]
res_pdf = subprocess.run(cmd_pdf, capture_output=True, text=True)
if res_pdf.returncode == 0 and pdf_path.exists():
    shutil.copy(pdf_path, pdf_kit_path)
    print(f"Generated Vector PDF successfully: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
else:
    print("PDF compilation error:", res_pdf.stderr)

print("\nPDF & EPUB generation complete.")

import sys
import os
import re
import unicodedata
import subprocess
from pathlib import Path
import markdown
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path('c:/Users/lenovo/Desktop/jankiz/book_digital_awareness')
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_PDF = BASE_DIR / "book_digital_awareness_A4.pdf"
PRINT_HTML_TEMP = BASE_DIR / "temp_a4_book.html"

print("=========================================================")
print("=== Starting Professional A4 PDF Book Generation System ===")
print("=========================================================")

# -------------------------------------------------------------
# 1. LOAD MANUSCRIPT FILES
# -------------------------------------------------------------
CHAPTER_SPECS = [
    ("01_chapter_human_digital_age.md", "الفصل الأول: الإنسان في العصر الرقمي"),
    ("02_chapter_software_and_apps.md", "الفصل الثاني: كيف تعمل البرامج والتطبيقات؟"),
    ("03_chapter_programming_logic.md", "الفصل الثالث: البرمجة وفن التفكير المنطقي"),
    ("04_chapter_cybersecurity_risks.md", "الفصل الرابع: الأمن السيبراني وفهم المخاطر الرقمية"),
    ("05_chapter_protect_yourself_family.md", "الفصل الخامس: كيف تحمي نفسك وعائلتك رقمياً؟"),
    ("06_chapter_secure_software_systems.md", "الفصل السادس: بناء البرمجيات والأنظمة الآمنة"),
    ("07_chapter_ai_future.md", "الفصل السابع: الذكاء الاصطناعي ومستقبل الإنسان"),
    ("08_chapter_digital_missteps.md", "الفصل الثامن: أخطاء رقمية قد تغير حياتك"),
    ("09_chapter_tech_for_society.md", "الفصل التاسع: التكنولوجيا في خدمة المجتمع"),
    ("10_chapter_knowledge_to_impact.md", "الفصل العاشر: من المعرفة إلى التأثير")
]

md_converter = markdown.Markdown(extensions=['extra', 'tables', 'fenced_code', 'nl2br', 'sane_lists'])

def md2html(text):
    md_converter.reset()
    return md_converter.convert(text)

# Read 00_front_matter.md
with open(BASE_DIR / '00_front_matter.md', 'r', encoding='utf-8') as f:
    fm_raw = f.read()

fm_splits = re.split(r'<div style="page-break-after: always;"></div>', fm_raw)
fm_copyright = fm_splits[1].strip() if len(fm_splits) >= 2 else ""
fm_dedication = fm_splits[2].strip() if len(fm_splits) >= 3 else ""
fm_author_word = fm_splits[3].strip() if len(fm_splits) >= 4 else ""
fm_intro = fm_splits[4].strip() if len(fm_splits) >= 5 else ""

# Read 11_conclusion_glossary_references.md
with open(BASE_DIR / '11_conclusion_glossary_references.md', 'r', encoding='utf-8') as f:
    bm_raw = f.read()

bm_splits = re.split(r'<div style="page-break-after: always;"></div>', bm_raw)
bm_conclusion = bm_splits[0].strip() if len(bm_splits) >= 1 else ""
bm_glossary = bm_splits[1].strip() if len(bm_splits) >= 2 else ""
bm_references = bm_splits[2].strip() if len(bm_splits) >= 3 else ""
bm_about_author = bm_splits[3].strip() if len(bm_splits) >= 4 else ""

# Read all 10 chapters
chapters_content = []
for fname, full_title in CHAPTER_SPECS:
    with open(BASE_DIR / fname, 'r', encoding='utf-8') as f:
        ch_md = f.read()
    chapters_content.append((fname, full_title, ch_md))

print(f"Loaded all manuscripts: Front Matter, {len(chapters_content)} Chapters, Back Matter.")

# -------------------------------------------------------------
# 2. HTML BUILDER FUNCTION
# -------------------------------------------------------------
TOC_ITEMS_DEF = [
    ("كلمة المؤلف: جنكيز", "SEC_AUTHOR_WORD"),
    ("مقدمة الكتاب: لماذا نحتاج إلى الوعي الرقمي؟", "SEC_INTRO"),
    ("الفصل الأول: الإنسان في العصر الرقمي", "SEC_CH_01"),
    ("الفصل الثاني: كيف تعمل البرامج والتطبيقات؟", "SEC_CH_02"),
    ("الفصل الثالث: البرمجة وفن التفكير المنطقي", "SEC_CH_03"),
    ("الفصل الرابع: الأمن السيبراني وفهم المخاطر الرقمية", "SEC_CH_04"),
    ("الفصل الخامس: كيف تحمي نفسك وعائلتك رقمياً؟", "SEC_CH_05"),
    ("الفصل السادس: بناء البرمجيات والأنظمة الآمنة", "SEC_CH_06"),
    ("الفصل السابع: الذكاء الاصطناعي ومستقبل الإنسان", "SEC_CH_07"),
    ("الفصل الثامن: أخطاء رقمية قد تغير حياتك", "SEC_CH_08"),
    ("الفصل التاسع: التكنولوجيا في خدمة المجتمع", "SEC_CH_09"),
    ("الفصل العاشر: من المعرفة إلى التأثير", "SEC_CH_10"),
    ("الخاتمة: التكنولوجيا في خدمة الإنسان", "SEC_CONCLUSION"),
    ("معجم المصطلحات التقنية الموحد", "SEC_GLOSSARY"),
    ("قائمة المصادر والمراجع الرسمية", "SEC_REFERENCES"),
    ("عن المؤلف: جنكيز", "SEC_ABOUT_AUTHOR"),
    ("الغلاف الخلفي", "SEC_BACK_COVER")
]

def build_html(toc_page_mapping=None):
    def get_p(marker_key, default_val="--"):
        if toc_page_mapping and marker_key in toc_page_mapping:
            return str(toc_page_mapping[marker_key])
        return default_val

    sections = []

    # 1. Front Cover (Page 1)
    sections.append('''<div class="pdf-page-section cover-section" style="page-break-before: auto; page-break-after: always; margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f172a;">
      <div class="section-tag" style="display:none;">[TAG:SEC_FRONT_COVER]</div>
      <img src="front_cover.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="غلاف كتاب الوعي الرقمي" />
    </div>''')

    # 2. Inside Title Page
    sections.append('''<div class="pdf-page-section inside-title-section" style="page-break-before: always; page-break-after: always; text-align: center; padding-top: 30mm;">
      <div class="section-tag" style="display:none;">[TAG:SEC_TITLE_PAGE]</div>
      <div style="font-size: 15pt; color: #64748b; font-weight: 600; margin-bottom: 12mm;">كتاب تخصصي في الثقافة التقنية والأمن السيبراني</div>
      <h1 style="font-size: 38pt; color: #1e3a8a; margin-bottom: 6mm; font-weight: 800; border: none; padding: 0;">الوعي الرقمي</h1>
      <div style="font-size: 18pt; color: #0284c7; margin-bottom: 18mm; font-weight: 600;">المعرفة التي تحميك وتصنع مستقبلك</div>
      
      <div style="margin: 20mm auto; width: 70px; height: 3.5px; background: #d97706; border-radius: 2px;"></div>
      
      <div style="font-size: 22pt; font-weight: 700; color: #0f172a; margin-bottom: 16mm;">تأليف: جنكيز</div>
      
      <blockquote style="font-size: 15pt; color: #334155; line-height: 1.8; margin: 0 auto 25mm auto; max-width: 82%; border: none; font-style: italic; background: transparent;">
        «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».
      </blockquote>
      
      <div style="font-size: 12pt; color: #94a3b8; font-weight: 500;">
        الطبعة الأولى — 2026م / 1447هـ<br/>
        جميع الحقوق محفوظة للمؤلف
      </div>
    </div>''')

    # 3. Copyright Page
    sections.append(f'''<div class="pdf-page-section copyright-section" style="page-break-before: always; page-break-after: always; padding-top: 10mm;">
      <div class="section-tag" style="display:none;">[TAG:SEC_COPYRIGHT]</div>
      {md2html(fm_copyright)}
    </div>''')

    # 4. Dedication Page
    sections.append(f'''<div class="pdf-page-section dedication-section" style="page-break-before: always; page-break-after: always; padding-top: 25mm; text-align: center;">
      <div class="section-tag" style="display:none;">[TAG:SEC_DEDICATION]</div>
      {md2html(fm_dedication)}
    </div>''')

    # 5. Author's Word
    sections.append(f'''<div class="pdf-page-section author-word-section" style="page-break-before: always; page-break-after: always; padding-top: 10mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_AUTHOR_WORD]</div>
      {md2html(fm_author_word)}
    </div>''')

    # 6. Introduction
    sections.append(f'''<div class="pdf-page-section intro-section" style="page-break-before: always; page-break-after: always; padding-top: 10mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_INTRO]</div>
      {md2html(fm_intro)}
    </div>''')

    # 7. Table of Contents
    toc_rows = []
    for item_title, marker_key in TOC_ITEMS_DEF:
        p_str = get_p(marker_key)
        toc_rows.append(f'''<div class="pdf-toc-row">
          <span class="pdf-toc-title">{item_title}</span>
          <span class="pdf-toc-dots"></span>
          <span class="pdf-toc-badge">ص {p_str}</span>
        </div>''')

    sections.append(f'''<div class="pdf-page-section toc-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
      <div class="section-tag" style="display:none;">[TAG:SEC_TOC]</div>
      <h2 style="text-align: center; font-size: 22pt; color: #1e3a8a; margin: 0 0 2mm 0; border: none; padding: 0;">فهرس المحتويات</h2>
      <div style="margin: 0 auto 6mm auto; width: 50px; height: 2.5px; background: #d97706; border-radius: 2px;"></div>
      <div class="pdf-toc-container">
        {"".join(toc_rows)}
      </div>
    </div>''')

    # 8. Chapters 1 to 10
    for idx, (fname, full_title, ch_md) in enumerate(chapters_content, 1):
        m_tag = f"SEC_CH_{idx:02d}"
        sections.append(f'''<div class="pdf-page-section chapter-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
          <div class="section-anchor-header">كتاب الوعي الرقمي — [{m_tag}]</div>
          {md2html(ch_md)}
        </div>''')

    # 9. Conclusion
    sections.append(f'''<div class="pdf-page-section back-matter-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_CONCLUSION]</div>
      {md2html(bm_conclusion)}
    </div>''')

    # 10. Glossary
    sections.append(f'''<div class="pdf-page-section back-matter-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_GLOSSARY]</div>
      {md2html(bm_glossary)}
    </div>''')

    # 11. References
    sections.append(f'''<div class="pdf-page-section back-matter-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_REFERENCES]</div>
      {md2html(bm_references)}
    </div>''')

    # 12. About Author
    sections.append(f'''<div class="pdf-page-section back-matter-section" style="page-break-before: always; page-break-after: always; padding-top: 6mm;">
      <div class="section-anchor-header">كتاب الوعي الرقمي — [SEC_ABOUT_AUTHOR]</div>
      {md2html(bm_about_author)}
    </div>''')

    # 13. Back Cover (Final Page)
    sections.append('''<div class="pdf-page-section back-cover-section" style="page-break-before: always; margin: 0; padding: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f172a;">
      <div class="section-tag" style="display:none;">[TAG:SEC_BACK_COVER]</div>
      <img src="back_cover.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="الغلاف الخلفي لكتاب الوعي الرقمي" />
    </div>''')

    full_html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>كتاب الوعي الرقمي — تأليف: جنكيز</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
  
  <style>
    @page {{
      size: A4 portrait;
      margin: 20mm 18mm 22mm 18mm;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 11pt;
      line-height: 1.85;
      color: #0f172a;
      background: #ffffff;
      direction: rtl;
      text-align: justify;
      text-justify: inter-word;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }}

    .section-anchor-header {{
      font-size: 7.5pt;
      color: #94a3b8;
      font-weight: 500;
      margin-bottom: 2mm;
      text-align: left;
      direction: ltr;
      letter-spacing: 0.5px;
    }}

    h1, h2, h3, h4 {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      color: #1e3a8a;
      font-weight: 700;
      line-height: 1.45;
      page-break-after: avoid;
    }}

    h1 {{
      font-size: 22pt;
      border-bottom: 2.5px solid #0284c7;
      padding-bottom: 4mm;
      margin-top: 0;
      margin-bottom: 7mm;
      text-align: center;
      color: #0f172a;
    }}

    h2 {{
      font-size: 15pt;
      color: #0369a1;
      margin-top: 7mm;
      margin-bottom: 3.5mm;
      border-bottom: 1px solid rgba(2, 132, 199, 0.2);
      padding-bottom: 1.5mm;
    }}

    h3 {{
      font-size: 12.5pt;
      color: #334155;
      margin-top: 5mm;
      margin-bottom: 2.5mm;
    }}

    p {{
      margin: 0 0 3.8mm 0;
      text-indent: 4mm;
    }}

    blockquote {{
      margin: 4.5mm 0;
      padding: 3.5mm 5.5mm;
      background: #f8fafc;
      border-right: 3.5pt solid #d97706;
      border-radius: 4px;
      font-style: italic;
      color: #1e293b;
      page-break-inside: avoid;
    }}

    pre, code {{
      font-family: 'Consolas', 'Courier New', Courier, monospace;
      direction: ltr;
      text-align: left;
      font-size: 9.2pt;
      background: #f1f5f9;
      border-radius: 4px;
    }}

    pre {{
      padding: 3.5mm 4.5mm;
      border: 1pt solid #cbd5e1;
      white-space: pre-wrap;
      word-break: break-all;
      margin: 3.5mm 0;
      line-height: 1.4;
      page-break-inside: avoid;
    }}

    code {{
      padding: 1mm 2mm;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 5mm 0;
      font-size: 9.8pt;
      page-break-inside: avoid;
    }}

    th, td {{
      border: 1pt solid #cbd5e1;
      padding: 2.8mm 3.5mm;
      text-align: right;
    }}

    th {{
      background: #f1f5f9;
      font-weight: 700;
      color: #0f172a;
    }}

    ul, ol {{
      margin: 2.5mm 0 4mm 0;
      padding-right: 5mm;
    }}

    li {{
      margin-bottom: 1.8mm;
    }}

    hr {{
      border: none;
      border-top: 0.8pt solid #e2e8f0;
      margin: 5mm 0;
    }}

    /* Table of Contents Styling for A4 */
    .pdf-toc-container {{
      display: flex;
      flex-direction: column;
      gap: 2.2mm;
      margin-top: 3mm;
    }}

    .pdf-toc-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 10.5pt;
      padding: 1.2mm 0;
    }}

    .pdf-toc-title {{
      font-weight: 600;
      color: #0f172a;
    }}

    .pdf-toc-dots {{
      flex: 1;
      border-bottom: 1.5pt dotted #94a3b8;
      margin: 0 3.5mm;
      min-width: 15mm;
    }}

    .pdf-toc-badge {{
      white-space: nowrap !important;
      font-weight: 700;
      color: #b45309;
      font-size: 10pt;
      background: rgba(217, 119, 6, 0.1);
      border: 1px solid rgba(217, 119, 6, 0.3);
      padding: 1mm 3mm;
      border-radius: 12px;
      min-width: 15mm;
      text-align: center;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
  </style>
</head>
<body>
{"".join(sections)}
</body>
</html>'''
    return full_html

# -------------------------------------------------------------
# 3. PDF COMPILATION & DETECTION
# -------------------------------------------------------------
def compile_pdf(html_path, output_pdf_path):
    header_html = '<div style="font-size:8.5pt; font-family:sans-serif; width:100%; text-align:center; color:#64748b; direction:rtl;"><span>كتاب الوعي الرقمي — تأليف: جنكيز</span></div>'
    footer_html = '<div style="font-size:9pt; font-family:sans-serif; width:100%; padding:0 18mm; display:flex; justify-content:space-between; color:#64748b; direction:rtl;"><span>الوعي الرقمي • جنكيز</span><span style="font-weight:bold; color:#b45309;">ص <span class="pageNumber"></span></span></div>'

    cmd = [
        CHROME_PATH,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--run-all-compositor-stages-before-draw',
        f'--print-to-pdf={output_pdf_path.resolve()}',
        '--display-header-footer',
        f'--header-template={header_html}',
        f'--footer-template={footer_html}',
        html_path.resolve().as_uri()
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not output_pdf_path.exists():
        raise RuntimeError(f"Chrome PDF generation failed: {res.stderr}")
    return output_pdf_path

def detect_section_pages(pdf_path):
    r = PdfReader(str(pdf_path))
    total_pages = len(r.pages)
    print(f"Reading PDF with {total_pages} total pages...", flush=True)

    page_texts = []
    for i, p in enumerate(r.pages, 1):
        txt = unicodedata.normalize('NFKC', p.extract_text() or '')
        page_texts.append((i, txt))

    mapping = {}
    for item_title, marker_key in TOC_ITEMS_DEF:
        if marker_key == "SEC_BACK_COVER":
            mapping[marker_key] = total_pages
            continue
            
        needle = f"[{marker_key}]"
        found_page = None
        for page_no, text in page_texts:
            if needle in text:
                found_page = page_no
                break
        
        if found_page is None:
            # Fallback search by title
            for page_no, text in page_texts:
                if page_no > 8 and item_title.split(':')[0] in text:
                    found_page = page_no
                    break
        
        mapping[marker_key] = found_page or 1

    return mapping

# -------------------------------------------------------------
# 4. EXECUTION
# -------------------------------------------------------------
print("\n--- Pass 1: Compiling draft PDF to measure exact chapter page offsets ---")
draft_html = build_html(toc_page_mapping=None)
with open(PRINT_HTML_TEMP, 'w', encoding='utf-8') as f:
    f.write(draft_html)

compile_pdf(PRINT_HTML_TEMP, OUTPUT_PDF)
print(f"Draft PDF compiled successfully ({OUTPUT_PDF.stat().st_size:,} bytes).")

detected_pages = detect_section_pages(OUTPUT_PDF)
print("\nDetected exact starting pages in PDF:")
for item_title, key in TOC_ITEMS_DEF:
    print(f"  {item_title:45s} -> Page {detected_pages.get(key)}")

current_mapping = detected_pages
pass_num = 2
while pass_num <= 4:
    print(f"\n--- Pass {pass_num}: Re-generating PDF with synchronized Table of Contents ---")
    final_html = build_html(toc_page_mapping=current_mapping)
    with open(PRINT_HTML_TEMP, 'w', encoding='utf-8') as f:
        f.write(final_html)

    compile_pdf(PRINT_HTML_TEMP, OUTPUT_PDF)
    print(f"Pass {pass_num} A4 PDF compiled ({OUTPUT_PDF.stat().st_size:,} bytes).")

    verified_pages = detect_section_pages(OUTPUT_PDF)
    all_synced = True
    for item_title, key in TOC_ITEMS_DEF:
        p1 = current_mapping.get(key)
        p2 = verified_pages.get(key)
        if p1 != p2:
            print(f"  [SHIFT] {item_title}: Target was p.{p1}, actually landed on p.{p2}")
            all_synced = False

    if all_synced:
        print("\n[SUCCESS] 100% Convergence verified! PDF TOC page numbers identically match actual PDF pages!")
        break
    else:
        current_mapping = verified_pages
        pass_num += 1

print(f"\nFinal Verified A4 PDF File: {OUTPUT_PDF}")
print(f"Page Count: {len(PdfReader(str(OUTPUT_PDF)).pages)} pages")
print(f"File Size: {OUTPUT_PDF.stat().st_size:,} bytes ({OUTPUT_PDF.stat().st_size / (1024*1024):.2f} MB)")

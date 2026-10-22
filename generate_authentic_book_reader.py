import sys
import os
import re
import json
from pathlib import Path
import markdown

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path('c:/Users/lenovo/Desktop/jankiz/book_digital_awareness')
INDEX_FILE = BASE_DIR / 'index.html'

print("=== Generating Authentic Arabic Book Reader (index.html) ===")

# Markdown converter
md = markdown.Markdown(extensions=['extra', 'tables', 'fenced_code', 'nl2br', 'sane_lists'])

def md2html(text):
    md.reset()
    return md.convert(text)

def chunk_markdown_to_pages(md_text, target_words_per_page=270):
    paragraphs = re.split(r'\n{2,}', md_text.strip())
    pages = []
    current_page = []
    current_words = 0
    in_code_block = False

    for para in paragraphs:
        p_strip = para.strip()
        if not p_strip:
            continue
            
        fence_count = p_strip.count('```')
        if fence_count % 2 != 0:
            in_code_block = not in_code_block

        p_words = len(re.sub(r'[#*`_\[\]\(\)\-\<\>]', ' ', p_strip).split())
        is_major_heading = p_strip.startswith('## ') and not in_code_block
        
        if (current_words + p_words > target_words_per_page or (is_major_heading and current_words > 130)) and not in_code_block and current_page:
            pages.append('\n\n'.join(current_page))
            current_page = [p_strip]
            current_words = p_words
        else:
            current_page.append(p_strip)
            current_words += p_words

    if current_page:
        pages.append('\n\n'.join(current_page))

    return pages

# Prepare Book Structure
book_pages = [] # List of dicts: {'type': 'cover'|'content'|'back_cover', 'header_right': '', 'header_left': '', 'html': '', 'toc_title': '', 'chapter_index': int}

# 1. Front Cover (Page 1)
book_pages.append({
    'type': 'cover',
    'title': 'الغلاف الأمامي',
    'header_right': 'الوعي الرقمي',
    'header_left': 'تأليف: جنكيز',
    'html': '''<div class="book-cover-inner">
      <img src="front_cover.jpg" alt="غلاف كتاب الوعي الرقمي - تأليف جنكيز" class="cover-image-main" />
      <div class="cover-quick-prompt">
        <span class="cover-title-badge">الوعي الرقمي</span>
        <span class="cover-author-badge">تأليف: جنكيز</span>
        <button class="open-book-btn" onclick="goToPage(2)">افتح الكتاب وابدأ القراءة 📖</button>
      </div>
    </div>''',
    'is_special': True
})

# 2. Inside Title Page (Page 2)
book_pages.append({
    'type': 'title_page',
    'title': 'صفحة العنوان',
    'header_right': 'الوعي الرقمي',
    'header_left': 'صفحة العنوان',
    'html': '''<div class="inside-title-container">
      <div class="sub-label">كتاب عربي تعليمي واحترافي في الثقافة الرقمية والأمن السيبراني</div>
      <h1 class="main-title">الوعي الرقمي</h1>
      <h2 class="sub-title">المعرفة التي تحميك وتصنع مستقبلك</h2>
      <div class="divider-gold"></div>
      <div class="author-name">تأليف: جنكيز</div>
      <blockquote class="official-quote">
        «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».
      </blockquote>
      <div class="edition-notice">الطبعة الأولى — 2026م / 1447هـ<br/>جميع الحقوق محفوظة للمؤلف</div>
    </div>''',
    'is_special': True
})

# Read 00_front_matter.md
with open(BASE_DIR / '00_front_matter.md', 'r', encoding='utf-8') as f:
    fm_raw = f.read()

fm_splits = re.split(r'<div style="page-break-after: always;"></div>', fm_raw)

# 3. Copyright Page
if len(fm_splits) >= 2:
    book_pages.append({
        'type': 'copyright',
        'title': 'حقوق التأليف والنشر',
        'header_right': 'الوعي الرقمي',
        'header_left': 'حقوق النشر والتوثيق',
        'html': f'<div class="page-content-wrapper copyright-wrapper">{md2html(fm_splits[1].strip())}</div>',
        'is_special': True
    })

# 4. Dedication
if len(fm_splits) >= 3:
    book_pages.append({
        'type': 'dedication',
        'title': 'الإهداء',
        'header_right': 'الوعي الرقمي',
        'header_left': 'الإهداء',
        'html': f'<div class="page-content-wrapper dedication-wrapper">{md2html(fm_splits[2].strip())}</div>',
        'is_special': True
    })

# 5. Author's Word
rest_fm = fm_splits[3].strip() if len(fm_splits) >= 4 else ""
intro_split = re.split(r'## المقدمة:', rest_fm)

if len(intro_split) == 2:
    author_word_md = intro_split[0].strip()
    book_pages.append({
        'type': 'author_word',
        'title': 'كلمة المؤلف: جنكيز',
        'header_right': 'الوعي الرقمي',
        'header_left': 'كلمة المؤلف: جنكيز',
        'html': f'<div class="page-content-wrapper author-word-wrapper">{md2html(author_word_md)}</div>',
        'is_special': False
    })
    
    # Introduction Pages (may be 2 pages)
    intro_pages_md = chunk_markdown_to_pages("## المقدمة:" + intro_split[1].strip(), target_words_per_page=260)
    for p_idx, p_md in enumerate(intro_pages_md, 1):
        book_pages.append({
            'type': 'intro',
            'title': f'المقدمة ({p_idx})' if len(intro_pages_md) > 1 else 'المقدمة',
            'header_right': 'الوعي الرقمي',
            'header_left': 'مقدمة الكتاب',
            'html': f'<div class="page-content-wrapper">{md2html(p_md)}</div>',
            'is_special': False
        })

# 6. Table of Contents Page (Will be populated with actual page targets)
toc_page_index = len(book_pages) + 1
# Placeholder for TOC page, we will populate its HTML after mapping all chapters
book_pages.append({
    'type': 'toc',
    'title': 'فهرس المحتويات',
    'header_right': 'الوعي الرقمي',
    'header_left': 'فهرس المحتويات',
    'html': '__TOC_PLACEHOLDER__',
    'is_special': True
})

# Chapters 1 to 10
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

chapter_start_pages = []

for ch_idx, (fname, full_title) in enumerate(CHAPTER_SPECS, 1):
    with open(BASE_DIR / fname, 'r', encoding='utf-8') as f:
        ch_md = f.read()
    
    # Record starting page for TOC
    start_p_num = len(book_pages) + 1
    chapter_start_pages.append((ch_idx, full_title, start_p_num))
    
    pages_md = chunk_markdown_to_pages(ch_md, target_words_per_page=260)
    for p_sub_idx, p_text in enumerate(pages_md, 1):
        book_pages.append({
            'type': 'chapter',
            'title': f'{full_title} (ص {p_sub_idx})',
            'chapter_title': full_title,
            'header_right': 'الوعي الرقمي • جنكيز',
            'header_left': full_title.split('—')[0].split(':')[0] if ':' in full_title else full_title,
            'html': f'<div class="page-content-wrapper chapter-body">{md2html(p_text)}</div>',
            'is_special': False
        })

# Read 11_conclusion_glossary_references.md
with open(BASE_DIR / '11_conclusion_glossary_references.md', 'r', encoding='utf-8') as f:
    conc_raw = f.read()

conc_splits = re.split(r'<div style="page-break-after: always;"></div>', conc_raw)

# Conclusion
if len(conc_splits) >= 1:
    conc_pages = chunk_markdown_to_pages(conc_splits[0].strip(), target_words_per_page=260)
    conc_start_p = len(book_pages) + 1
    chapter_start_pages.append((11, "الخاتمة: التكنولوجيا في خدمة الإنسان", conc_start_p))
    for p_idx, p_md in enumerate(conc_pages, 1):
        book_pages.append({
            'type': 'conclusion',
            'title': f'الخاتمة (ص {p_idx})',
            'header_right': 'الوعي الرقمي',
            'header_left': 'خاتمة الكتاب',
            'html': f'<div class="page-content-wrapper">{md2html(p_md)}</div>',
            'is_special': False
        })

# Glossary
if len(conc_splits) >= 2:
    gloss_pages = chunk_markdown_to_pages(conc_splits[1].strip(), target_words_per_page=280)
    gloss_start_p = len(book_pages) + 1
    chapter_start_pages.append((12, "معجم المصطلحات التقنية الموحد", gloss_start_p))
    for p_idx, p_md in enumerate(gloss_pages, 1):
        book_pages.append({
            'type': 'glossary',
            'title': f'معجم المصطلحات ({p_idx})',
            'header_right': 'الوعي الرقمي',
            'header_left': 'معجم المصطلحات التقنية',
            'html': f'<div class="page-content-wrapper glossary-body">{md2html(p_md)}</div>',
            'is_special': False
        })

# References
if len(conc_splits) >= 3:
    ref_pages = chunk_markdown_to_pages(conc_splits[2].strip(), target_words_per_page=280)
    ref_start_p = len(book_pages) + 1
    chapter_start_pages.append((13, "قائمة المصادر والمراجع الرسمية", ref_start_p))
    for p_idx, p_md in enumerate(ref_pages, 1):
        book_pages.append({
            'type': 'references',
            'title': f'المراجع الرسمية ({p_idx})',
            'header_right': 'الوعي الرقمي',
            'header_left': 'المصادر والمراجع الرسمية',
            'html': f'<div class="page-content-wrapper references-body">{md2html(p_md)}</div>',
            'is_special': False
        })

# About Author
if len(conc_splits) >= 4:
    author_start_p = len(book_pages) + 1
    chapter_start_pages.append((14, "عن المؤلف: جنكيز", author_start_p))
    book_pages.append({
        'type': 'about_author',
        'title': 'عن المؤلف: جنكيز',
        'header_right': 'الوعي الرقمي',
        'header_left': 'عن المؤلف',
        'html': f'<div class="page-content-wrapper about-author-wrapper">{md2html(conc_splits[3].strip())}</div>',
        'is_special': False
    })

# Back Cover (Final Page)
back_cover_p = len(book_pages) + 1
chapter_start_pages.append((15, "الغلاف الخلفي", back_cover_p))
book_pages.append({
    'type': 'back_cover',
    'title': 'الغلاف الخلفي',
    'header_right': 'الوعي الرقمي',
    'header_left': 'تأليف: جنكيز',
    'html': '''<div class="book-cover-inner">
      <img src="back_cover.jpg" alt="الغلاف الخلفي لكتاب الوعي الرقمي" class="cover-image-main" />
      <div class="cover-quick-prompt">
        <span class="cover-title-badge">تم بحمد الله وتوفيقه</span>
        <button class="open-book-btn" onclick="goToPage(1)">العودة لغلاف البداية ↺</button>
      </div>
    </div>''',
    'is_special': True
})

print(f"Total structured book pages generated: {len(book_pages)} pages.")

# Populate Table of Contents HTML
toc_items_html = []
for idx, title, page_no in chapter_start_pages:
    toc_items_html.append(f'''<li class="toc-list-item" onclick="goToPage({page_no})">
  <span class="toc-item-title">{title}</span>
  <span class="toc-item-dots"></span>
  <span class="toc-item-page">ص {page_no}</span>
</li>''')

toc_full_html = f'''<div class="toc-page-container">
  <h2 class="toc-main-header">فهرس المحتويات</h2>
  <div class="divider-gold"></div>
  <ul class="toc-list">
    {"".join(toc_items_html)}
  </ul>
</div>'''

for p in book_pages:
    if p.get('html') == '__TOC_PLACEHOLDER__':
        p['html'] = toc_full_html

print("Table of Contents populated with exact page references.")

# Now compile the HTML and embed the page structure
# We serialize pages to a JSON array for client-side rendering
pages_json = json.dumps(book_pages, ensure_ascii=False)
toc_json = json.dumps(chapter_start_pages, ensure_ascii=False)

reader_html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>كتاب الوعي الرقمي — تأليف: جنكيز</title>
  
  <meta name="description" content="كتاب عربي تعليمي واحترافي في مجال الوعي الرقمي، والأمن السيبراني، والبرمجة، والذكاء الاصطناعي — تأليف: جنكيز. «المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها».">
  <meta name="author" content="جنكيز">
  <meta property="og:title" content="كتاب الوعي الرقمي — تأليف: جنكيز">
  <meta property="og:description" content="«المعرفة قوة، لكن قيمتها الحقيقية تتجلّى في نفع الآخرين بها» — اقرأ الكتاب الإلكتروني كاملاً بتجربة ورقية حقيقية.">
  <meta property="og:image" content="front_cover.jpg">
  <meta property="og:type" content="book">

  <!-- Classical & High-Legibility Arabic Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">

  <style>
    :root {{
      /* Paper Theme (Classic Sepia / Ivory - Default) */
      --bg-desk: #23272e;
      --paper-bg: #faf7f0;
      --paper-bg-alt: #f5f0e6;
      --text-main: #24292e;
      --text-muted: #57606a;
      --text-headings: #0f172a;
      --header-border: rgba(148, 163, 184, 0.4);
      --book-shadow: 0 16px 40px rgba(0, 0, 0, 0.45), 0 2px 8px rgba(0, 0, 0, 0.2);
      --spine-shadow: linear-gradient(to right, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0.04) 4%, transparent 12%);
      --accent-color: #0284c7;
      --accent-gold: #d97706;
      --callout-bg: rgba(14, 165, 233, 0.08);
      --code-bg: #ede8dc;
      --font-scale: 1.0;
    }}

    [data-theme="dark"] {{
      --bg-desk: #0d1117;
      --paper-bg: #161b22;
      --paper-bg-alt: #0f141c;
      --text-main: #e6edf3;
      --text-muted: #8b949e;
      --text-headings: #f0f6fc;
      --header-border: rgba(48, 54, 61, 0.8);
      --book-shadow: 0 16px 40px rgba(0, 0, 0, 0.8);
      --spine-shadow: linear-gradient(to right, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.2) 4%, transparent 12%);
      --accent-color: #38bdf8;
      --accent-gold: #fbbf24;
      --callout-bg: rgba(56, 189, 248, 0.12);
      --code-bg: #21262d;
    }}

    [data-theme="light"] {{
      --bg-desk: #e2e8f0;
      --paper-bg: #ffffff;
      --paper-bg-alt: #f8fafc;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-headings: #0284c7;
      --header-border: #cbd5e1;
      --book-shadow: 0 12px 32px rgba(100, 116, 139, 0.3);
      --spine-shadow: linear-gradient(to right, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.02) 4%, transparent 12%);
      --accent-color: #0369a1;
      --accent-gold: #b45309;
      --callout-bg: #f0f9ff;
      --code-bg: #f1f5f9;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}

    html, body {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: var(--bg-desk);
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      direction: rtl;
      user-select: text;
    }}

    /* Main Container (Desk View) */
    .desk-stage {{
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }}

    /* Minimalist Unobtrusive Floating Tools Bar */
    .floating-toolbar {{
      position: fixed;
      top: 14px;
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 6px 14px;
      border-radius: 30px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
      transition: opacity 0.3s ease, transform 0.3s ease;
    }}

    .floating-toolbar:hover, .floating-toolbar.active {{
      opacity: 1;
      transform: translateY(0);
    }}

    .tool-btn {{
      background: transparent;
      border: none;
      color: #f1f5f9;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 13px;
      font-weight: 600;
      padding: 6px 10px;
      border-radius: 20px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s, color 0.2s;
    }}

    .tool-btn:hover {{
      background: rgba(255, 255, 255, 0.15);
      color: #38bdf8;
    }}

    .tool-divider {{
      width: 1px;
      height: 18px;
      background: rgba(255, 255, 255, 0.2);
    }}

    /* The Real Book Container */
    .book-outer-wrapper {{
      width: 94vw;
      max-width: 1280px;
      height: 86vh;
      max-height: 860px;
      display: flex;
      justify-content: center;
      align-items: stretch;
      perspective: 2000px;
      position: relative;
      margin-top: 15px;
    }}

    /* Book Spread (Two-page or Single-page) */
    .book-spread {{
      width: 100%;
      height: 100%;
      display: flex;
      background: var(--paper-bg);
      border-radius: 8px;
      box-shadow: var(--book-shadow);
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(0,0,0,0.1);
      transition: background 0.3s ease;
    }}

    /* Individual Book Page */
    .book-page-leaf {{
      flex: 1;
      height: 100%;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      padding: 30px 42px 28px 42px;
      background: var(--paper-bg);
      color: var(--text-main);
    }}

    /* Right vs Left Page Details in Spread */
    .book-page-leaf.right-leaf {{
      border-left: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset -15px 0 25px -10px rgba(0, 0, 0, 0.08);
    }}

    .book-page-leaf.left-leaf {{
      border-right: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset 15px 0 25px -10px rgba(0, 0, 0, 0.08);
    }}

    /* Center Book Spine Binding Line */
    .book-spine-crease {{
      position: absolute;
      left: 50%;
      top: 0;
      bottom: 0;
      width: 30px;
      transform: translateX(-50%);
      background: linear-gradient(to right, rgba(0,0,0,0.12) 0%, rgba(0,0,0,0.02) 40%, rgba(0,0,0,0.02) 60%, rgba(0,0,0,0.12) 100%);
      pointer-events: none;
      z-index: 10;
    }}

    /* Running Header (ترويسة الصفحة) */
    .page-running-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      color: var(--text-muted);
      border-bottom: 1px solid var(--header-border);
      padding-bottom: 8px;
      margin-bottom: 16px;
      font-weight: 600;
      letter-spacing: 0.3px;
      flex-shrink: 0;
    }}

    .header-book-title {{
      color: var(--accent-color);
    }}

    /* Page Content Scroll/Body */
    .page-content-scroll {{
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding-left: 6px;
      padding-right: 2px;
      line-height: calc(1.88 * var(--font-scale));
      font-size: calc(16.5px * var(--font-scale));
      text-align: justify;
      text-justify: inter-word;
    }}

    /* Hide scrollbar for pristine book aesthetics */
    .page-content-scroll::-webkit-scrollbar {{
      width: 4px;
    }}
    .page-content-scroll::-webkit-scrollbar-thumb {{
      background: rgba(0, 0, 0, 0.15);
      border-radius: 4px;
    }}

    /* Running Footer (تذييل الصفحة) */
    .page-running-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      color: var(--text-muted);
      border-top: 1px solid var(--header-border);
      padding-top: 8px;
      margin-top: 14px;
      flex-shrink: 0;
    }}

    .footer-page-num {{
      font-weight: 700;
      color: var(--accent-gold);
    }}

    /* Navigation Arrows on Book Margins */
    .book-nav-arrow {{
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 48px;
      height: 70px;
      background: rgba(15, 23, 42, 0.4);
      color: #ffffff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      border-radius: 6px;
      z-index: 20;
      transition: background 0.2s, opacity 0.2s;
      opacity: 0.7;
    }}

    .book-nav-arrow:hover {{
      background: rgba(2, 132, 199, 0.85);
      opacity: 1;
    }}

    .nav-arrow-prev {{
      right: -24px;
    }}

    .nav-arrow-next {{
      left: -24px;
    }}

    /* Bottom Slider & Page Indicator */
    .bottom-status-bar {{
      position: fixed;
      bottom: 12px;
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 14px;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 6px 18px;
      border-radius: 30px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #f1f5f9;
      font-size: 13px;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
    }}

    .page-slider {{
      width: 140px;
      height: 6px;
      cursor: pointer;
      accent-color: var(--accent-color);
    }}

    /* Typography & Content Styles */
    h1, h2, h3, h4 {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      color: var(--text-headings);
      line-height: 1.4;
      margin-top: 0.8em;
      margin-bottom: 0.4em;
    }}

    h1 {{ font-size: 1.45em; border-bottom: 2px solid var(--accent-color); padding-bottom: 0.2em; text-align: center; }}
    h2 {{ font-size: 1.25em; color: var(--accent-color); }}
    h3 {{ font-size: 1.1em; color: var(--text-muted); }}

    p {{ margin-bottom: 0.8em; }}

    blockquote {{
      border-right: 3px solid var(--accent-gold);
      background: var(--callout-bg);
      padding: 10px 14px;
      margin: 12px 0;
      border-radius: 4px;
      font-style: italic;
    }}

    pre, code {{
      font-family: 'Courier New', Courier, monospace;
      direction: ltr;
      text-align: left;
      background: var(--code-bg);
      border-radius: 4px;
      color: #0f172a;
    }}

    pre {{
      padding: 10px 12px;
      overflow-x: auto;
      margin: 10px 0;
      font-size: 0.82em;
      line-height: 1.45;
      border: 1px solid rgba(0, 0, 0, 0.1);
    }}

    code {{ padding: 2px 4px; font-size: 0.9em; }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 0.88em;
    }}

    th, td {{
      border: 1px solid rgba(0, 0, 0, 0.12);
      padding: 6px 10px;
      text-align: right;
    }}

    th {{ background: rgba(0, 0, 0, 0.05); font-weight: bold; }}

    ul, ol {{ padding-right: 20px; margin-bottom: 10px; }}
    li {{ margin-bottom: 4px; }}

    /* Front Cover Inner Page Styling */
    .book-cover-inner {{
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      background: #0f172a;
      border-radius: 6px;
      overflow: hidden;
    }}

    .cover-image-main {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 4px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}

    .cover-quick-prompt {{
      position: absolute;
      bottom: 25px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(8px);
      padding: 14px 26px;
      border-radius: 12px;
      border: 1px solid rgba(56, 189, 248, 0.4);
    }}

    .cover-title-badge {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 22px;
      font-weight: 700;
      color: #fbbf24;
    }}

    .cover-author-badge {{
      font-size: 14px;
      color: #94a3b8;
    }}

    .open-book-btn {{
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff;
      border: none;
      padding: 10px 22px;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-weight: 700;
      font-size: 15px;
      border-radius: 25px;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
      transition: transform 0.2s, background 0.2s;
    }}

    .open-book-btn:hover {{
      transform: scale(1.04);
      background: #0ea5e9;
    }}

    /* Inside Title Page Styling */
    .inside-title-container {{
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 20px;
    }}

    .inside-title-container .sub-label {{
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 20px;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
    }}

    .inside-title-container .main-title {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 40px;
      color: var(--accent-color);
      margin-bottom: 8px;
      font-weight: 700;
      border: none;
    }}

    .inside-title-container .sub-title {{
      font-size: 18px;
      color: var(--accent-gold);
      margin-bottom: 25px;
      font-weight: 600;
    }}

    .divider-gold {{
      width: 50px;
      height: 2.5px;
      background: var(--accent-gold);
      margin: 15px auto 25px auto;
      border-radius: 2px;
    }}

    .inside-title-container .author-name {{
      font-size: 20px;
      font-weight: 700;
      color: var(--text-headings);
      margin-bottom: 20px;
    }}

    .inside-title-container .official-quote {{
      font-size: 17px;
      color: var(--text-main);
      max-width: 85%;
      margin: 0 auto 30px auto;
      line-height: 1.8;
      border-right: none;
      background: transparent;
    }}

    .inside-title-container .edition-notice {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* Table of Contents Styling */
    .toc-page-container {{
      padding: 10px 5px;
    }}

    .toc-main-header {{
      text-align: center;
      font-size: 24px;
      margin-bottom: 15px;
      border-bottom: none;
    }}

    .toc-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}

    .toc-list-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 8px;
      border-bottom: 1px dashed rgba(0, 0, 0, 0.1);
      cursor: pointer;
      border-radius: 4px;
      transition: background 0.15s, color 0.15s;
      font-size: 14.5px;
    }}

    .toc-list-item:hover {{
      background: var(--callout-bg);
      color: var(--accent-color);
    }}

    .toc-item-title {{
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .toc-item-dots {{
      flex: 1;
      border-bottom: 1px dotted rgba(0, 0, 0, 0.2);
      margin: 0 10px;
    }}

    .toc-item-page {{
      font-weight: 700;
      color: var(--accent-gold);
      font-size: 13.5px;
    }}

    /* Slide-over TOC & Tools Drawer */
    .drawer-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      z-index: 200;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}

    .drawer-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .side-drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 380px;
      max-width: 90vw;
      background: var(--paper-bg);
      color: var(--text-main);
      z-index: 210;
      transform: translateX(100%);
      transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      box-shadow: -8px 0 30px rgba(0, 0, 0, 0.4);
      border-left: 1px solid var(--header-border);
    }}

    .drawer-overlay.open .side-drawer {{
      transform: translateX(0);
    }}

    .drawer-header {{
      padding: 18px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--header-border);
    }}

    .drawer-title {{
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 18px;
      font-weight: 700;
      color: var(--text-headings);
    }}

    .drawer-close-btn {{
      background: transparent;
      border: none;
      font-size: 22px;
      cursor: pointer;
      color: var(--text-muted);
    }}

    .drawer-body {{
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px;
    }}

    .drawer-section-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--accent-color);
      text-transform: uppercase;
      margin: 18px 0 10px 0;
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
    }}

    .theme-picker-group {{
      display: flex;
      gap: 8px;
      margin-bottom: 15px;
    }}

    .theme-opt-btn {{
      flex: 1;
      padding: 9px 8px;
      border-radius: 8px;
      border: 1px solid var(--header-border);
      background: var(--paper-bg-alt);
      color: var(--text-main);
      font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
    }}

    .theme-opt-btn.active {{
      border-color: var(--accent-color);
      background: var(--callout-bg);
      color: var(--accent-color);
    }}

    .download-group {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 10px;
    }}

    .download-btn-card {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--paper-bg-alt);
      border: 1px solid var(--header-border);
      text-decoration: none;
      color: var(--text-main);
      transition: background 0.2s, border-color 0.2s;
    }}

    .download-btn-card:hover {{
      background: var(--callout-bg);
      border-color: var(--accent-color);
    }}

    .download-icon {{
      font-size: 22px;
    }}

    .download-meta-title {{
      font-weight: 700;
      font-size: 14px;
    }}

    .download-meta-desc {{
      font-size: 11px;
      color: var(--text-muted);
    }}

    /* Responsive Adaptation (Mobile vs Desktop Spread) */
    @media (max-width: 899px) {{
      .book-outer-wrapper {{
        width: 100vw;
        height: 100vh;
        max-height: 100vh;
        margin-top: 0;
      }}
      .book-spread {{
        border-radius: 0;
        box-shadow: none;
        border: none;
      }}
      .book-spine-crease {{
        display: none;
      }}
      .book-page-leaf.left-leaf {{
        display: none !important;
      }}
      .book-page-leaf {{
        padding: 60px 20px 55px 20px;
      }}
      .book-nav-arrow {{
        display: none;
      }}
      .floating-toolbar {{
        top: 8px;
        padding: 4px 10px;
      }}
      .bottom-status-bar {{
        bottom: 8px;
        padding: 4px 12px;
      }}
    }}

    @media (max-width: 600px) {{
      .floating-toolbar {{
        top: 6px;
        padding: 4px 8px;
        gap: 4px;
        max-width: 96vw;
        justify-content: center;
      }}
      .tool-btn {{
        padding: 4px 6px;
        font-size: 11px;
      }}
      .tool-btn span:not(:first-child) {{
        display: none;
      }}
      .bottom-status-bar {{
        bottom: 6px;
        padding: 4px 10px;
        gap: 8px;
        font-size: 11.5px;
      }}
      .page-slider {{
        width: 100px;
      }}
    }}
  </style>
</head>
<body>

  <!-- Desk Stage -->
  <div class="desk-stage" id="deskStage">

    <!-- Minimalist Floating Reading Controls -->
    <header class="floating-toolbar" id="mainToolbar">
      <button class="tool-btn" onclick="toggleDrawer()" title="فهرس الكتاب">
        <span>📖</span>
        <span>الفهرس</span>
      </button>

      <div class="tool-divider"></div>

      <button class="tool-btn" onclick="changeFontSize(-0.1)" title="تصغير الخط">A-</button>
      <button class="tool-btn" onclick="changeFontSize(0.1)" title="تكبير الخط">A+</button>

      <div class="tool-divider"></div>

      <button class="tool-btn" onclick="cycleTheme()" title="تغيير المظهر">
        <span id="themeIcon">📜</span>
        <span id="themeName">ورقي</span>
      </button>

      <div class="tool-divider"></div>

      <button class="tool-btn" onclick="openDownloadModal()" title="تنزيل الكتاب (PDF/EPUB)">
        <span>📥</span>
        <span>تحميل</span>
      </button>

      <div class="tool-divider"></div>

      <button class="tool-btn" onclick="toggleFullscreen()" title="ملء الشاشة">
        <span>⛶</span>
      </button>
    </header>

    <!-- The Authentic Book Wrapper -->
    <div class="book-outer-wrapper">
      
      <!-- Right Page Nav Arrow (Prev Page in RTL) -->
      <button class="book-nav-arrow nav-arrow-prev" onclick="prevSpread()" title="الصفحة السابقة (السهم الأيمن)">
        &#x25BA;
      </button>

      <!-- The Open Book Spread -->
      <main class="book-spread" id="bookSpread">
        
        <!-- Right Leaf (صفحة يمنى) -->
        <article class="book-page-leaf right-leaf" id="rightLeaf">
          <header class="page-running-header">
            <span class="header-book-title" id="rightHeaderBook">الوعي الرقمي</span>
            <span class="header-chapter-name" id="rightHeaderChapter">تأليف: جنكيز</span>
          </header>

          <section class="page-content-scroll" id="rightPageContent">
            <!-- Content Injected Dynamically -->
          </section>

          <footer class="page-running-footer">
            <span class="footer-author">جنكيز</span>
            <span class="footer-page-num" id="rightPageNum">ص ١</span>
          </footer>
        </article>

        <!-- Center 3D Spine Crease -->
        <div class="book-spine-crease"></div>

        <!-- Left Leaf (صفحة يسرى) -->
        <article class="book-page-leaf left-leaf" id="leftLeaf">
          <header class="page-running-header">
            <span class="header-chapter-name" id="leftHeaderChapter">تأليف: جنكيز</span>
            <span class="header-book-title" id="leftHeaderBook">«المعرفة قوة، تتجلّى في نفع الآخرين بها»</span>
          </header>

          <section class="page-content-scroll" id="leftPageContent">
            <!-- Content Injected Dynamically -->
          </section>

          <footer class="page-running-footer">
            <span class="footer-page-num" id="leftPageNum">ص ٢</span>
            <span class="footer-book-meta">الوعي الرقمي</span>
          </footer>
        </article>

      </main>

      <!-- Left Page Nav Arrow (Next Page in RTL) -->
      <button class="book-nav-arrow nav-arrow-next" onclick="nextSpread()" title="الصفحة التالية (السهم الأيسر)">
        &#x25C4;
      </button>

    </div>

    <!-- Bottom Reading Progress & Slider -->
    <footer class="bottom-status-bar" id="bottomBar">
      <span id="readingProgressText">ص 1 من {len(book_pages)}</span>
      <input type="range" class="page-slider" id="pageSlider" min="1" max="{len(book_pages)}" value="1" oninput="onSliderMove(this.value)" />
      <span id="readingPercentageText">1%</span>
    </footer>

  </div>

  <!-- Slide-over Drawer (TOC, Settings, Downloads) -->
  <div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer(event)">
    <aside class="side-drawer" onclick="event.stopPropagation()">
      <div class="drawer-header">
        <h3 class="drawer-title">فهرس وأدوات الكتاب</h3>
        <button class="drawer-close-btn" onclick="toggleDrawer()" title="إغلاق">✕</button>
      </div>

      <div class="drawer-body">
        
        <div class="drawer-section-title">نمط العرض والإضاءة</div>
        <div class="theme-picker-group">
          <button class="theme-opt-btn active" id="btnThemeSepia" onclick="setTheme('sepia')">📜 ورقي عاجي</button>
          <button class="theme-opt-btn" id="btnThemeDark" onclick="setTheme('dark')">🌙 ليلي هادئ</button>
          <button class="theme-opt-btn" id="btnThemeLight" onclick="setTheme('light')">☀️ نهاري ناصع</button>
        </div>

        <div class="drawer-section-title">فهرس الفصول والمحتويات</div>
        <ul class="toc-list" id="drawerTocList">
          <!-- Populated dynamically -->
        </ul>

        <div class="drawer-section-title">النسخ الرقمية المعتمدة</div>
        <div class="download-group">
          <a href="book_digital_awareness_complete.pdf" download class="download-btn-card">
            <span class="download-icon">📕</span>
            <div>
              <div class="download-meta-title">نسخة PDF للطباعة والقراءة</div>
              <div class="download-meta-desc">ملف بي دي إف رسمي متجهي عالي الدقة (A5)</div>
            </div>
          </a>

          <a href="book_digital_awareness.epub" download class="download-btn-card">
            <span class="download-icon">📱</span>
            <div>
              <div class="download-meta-title">نسخة EPUB الإلكترونية</div>
              <div class="download-meta-desc">متوافقة مع Apple Books وGoogle Play Books وكيندل</div>
            </div>
          </a>

          <a href="front_cover.jpg" download class="download-btn-card">
            <span class="download-icon">🖼️</span>
            <div>
              <div class="download-meta-title">الغلاف الأمامي عالي الجودة</div>
              <div class="download-meta-desc">تصميم الغلاف الرسمي بصيغة JPG عالية الدقة</div>
            </div>
          </a>

          <a href="back_cover.jpg" download class="download-btn-card">
            <span class="download-icon">📄</span>
            <div>
              <div class="download-meta-title">الغلاف الخلفي المعتمد</div>
              <div class="download-meta-desc">نبذة الغلاف والعبارة الرسمية وبيانات التصنيف</div>
            </div>
          </a>
        </div>

        <div style="margin-top: 25px; text-align: center; font-size: 11.5px; color: var(--text-muted); line-height: 1.6;">
          كتاب «الوعي الرقمي» — تأليف: جنكيز<br/>
          جميع الحقوق محفوظة للمؤلف © 2026
        </div>

      </div>
    </aside>
  </div>

  <script>
    // Embedded Manuscript Pages Data
    const BOOK_PAGES = {pages_json};
    const TOC_CHAPTERS = {toc_json};
    const TOTAL_PAGES = BOOK_PAGES.length;

    let currentPage = 1; // 1-based index
    let currentTheme = 'sepia';
    let currentFontScale = 1.0;

    // Convert Hindu-Arabic numbers for classical page display
    function toArabicDigits(num) {{
      const ar = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
      return String(num).replace(/[0-9]/g, d => ar[d]);
    }}

    function isDesktopSpread() {{
      return window.innerWidth >= 900;
    }}

    // Render Current Spread or Single Page
    function renderBook() {{
      const rightLeaf = document.getElementById('rightLeaf');
      const leftLeaf = document.getElementById('leftLeaf');
      const pageSlider = document.getElementById('pageSlider');
      const readingProgressText = document.getElementById('readingProgressText');
      const readingPercentageText = document.getElementById('readingPercentageText');

      if (!isDesktopSpread()) {{
        // Mobile Single Page View
        const pData = BOOK_PAGES[currentPage - 1];
        document.getElementById('rightHeaderBook').textContent = pData.header_right || 'الوعي الرقمي';
        document.getElementById('rightHeaderChapter').textContent = pData.header_left || 'جنكيز';
        document.getElementById('rightPageContent').innerHTML = pData.html;
        document.getElementById('rightPageNum').textContent = 'ص ' + toArabicDigits(currentPage);

        leftLeaf.style.display = 'none';
      }} else {{
        // Desktop Two-Page Spread
        leftLeaf.style.display = 'flex';

        // When on Page 1 (Cover) or last page, center it gracefully
        if (currentPage === 1) {{
          const coverData = BOOK_PAGES[0];
          document.getElementById('rightHeaderBook').textContent = 'الوعي الرقمي';
          document.getElementById('rightHeaderChapter').textContent = 'تأليف: جنكيز';
          document.getElementById('rightPageContent').innerHTML = coverData.html;
          document.getElementById('rightPageNum').textContent = 'الغلاف';

          // Left page shows Inside Title Page (Page 2)
          if (BOOK_PAGES.length > 1) {{
            const p2 = BOOK_PAGES[1];
            document.getElementById('leftHeaderBook').textContent = p2.header_right || 'الوعي الرقمي';
            document.getElementById('leftHeaderChapter').textContent = p2.header_left || 'صفحة العنوان';
            document.getElementById('leftPageContent').innerHTML = p2.html;
            document.getElementById('leftPageNum').textContent = 'ص ٢';
          }}
        }} else {{
          // Normal Spread: Right Page = currentPage, Left Page = currentPage + 1
          const rIndex = currentPage - 1;
          const lIndex = currentPage; // 0-based for next page

          const rData = BOOK_PAGES[rIndex];
          document.getElementById('rightHeaderBook').textContent = rData.header_right || 'الوعي الرقمي';
          document.getElementById('rightHeaderChapter').textContent = rData.header_left || '';
          document.getElementById('rightPageContent').innerHTML = rData.html;
          document.getElementById('rightPageNum').textContent = 'ص ' + toArabicDigits(currentPage);

          if (lIndex < TOTAL_PAGES) {{
            const lData = BOOK_PAGES[lIndex];
            document.getElementById('leftHeaderBook').textContent = lData.header_right || 'الوعي الرقمي';
            document.getElementById('leftHeaderChapter').textContent = lData.header_left || '';
            document.getElementById('leftPageContent').innerHTML = lData.html;
            document.getElementById('leftPageNum').textContent = 'ص ' + toArabicDigits(currentPage + 1);
            leftLeaf.style.visibility = 'visible';
          }} else {{
            // End of book blank left page
            document.getElementById('leftHeaderBook').textContent = '';
            document.getElementById('leftHeaderChapter').textContent = '';
            document.getElementById('leftPageContent').innerHTML = '<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-muted); font-size:14px;">نهاية الكتاب • تم بحمد الله</div>';
            document.getElementById('leftPageNum').textContent = '';
          }}
        }}
      }}

      // Scroll both pages back to top
      document.getElementById('rightPageContent').scrollTop = 0;
      document.getElementById('leftPageContent').scrollTop = 0;

      // Update Slider and Status
      pageSlider.value = currentPage;
      const pct = Math.round((currentPage / TOTAL_PAGES) * 100);
      readingProgressText.textContent = `ص ${{currentPage}} من ${{TOTAL_PAGES}}`;
      readingPercentageText.textContent = `${{pct}}%`;

      // Save bookmark in localStorage
      try {{
        localStorage.setItem('digital_awareness_last_page', String(currentPage));
      }} catch(e) {{}}
    }}

    function goToPage(p) {{
      p = parseInt(p, 10);
      if (isNaN(p)) return;
      if (p < 1) p = 1;
      if (p > TOTAL_PAGES) p = TOTAL_PAGES;

      // In desktop spread mode, ensure page is odd (right page) for consistent book feel,
      // except for page 1
      if (isDesktopSpread() && p > 1 && p % 2 === 1) {{
        currentPage = p;
      }} else if (isDesktopSpread() && p > 1 && p % 2 === 0) {{
        currentPage = p - 1;
      }} else {{
        currentPage = p;
      }}

      renderBook();
      closeDrawer();
    }}

    function nextSpread() {{
      const step = isDesktopSpread() ? 2 : 1;
      if (currentPage + step <= TOTAL_PAGES) {{
        goToPage(currentPage + step);
      }} else if (currentPage < TOTAL_PAGES) {{
        goToPage(TOTAL_PAGES);
      }}
    }}

    function prevSpread() {{
      const step = isDesktopSpread() ? 2 : 1;
      if (currentPage - step >= 1) {{
        goToPage(currentPage - step);
      }} else {{
        goToPage(1);
      }}
    }}

    function onSliderMove(val) {{
      goToPage(val);
    }}

    // Reading Themes
    function setTheme(theme) {{
      currentTheme = theme;
      const root = document.documentElement;
      root.removeAttribute('data-theme');
      if (theme !== 'sepia') {{
        root.setAttribute('data-theme', theme);
      }}

      // Update Toolbar Icon & Name
      const icon = document.getElementById('themeIcon');
      const name = document.getElementById('themeName');
      if (theme === 'sepia') {{
        icon.textContent = '📜';
        name.textContent = 'ورقي';
      }} else if (theme === 'dark') {{
        icon.textContent = '🌙';
        name.textContent = 'ليلي';
      }} else {{
        icon.textContent = '☀️';
        name.textContent = 'نهاري';
      }}

      // Update Drawer active button
      document.querySelectorAll('.theme-opt-btn').forEach(btn => btn.classList.remove('active'));
      if (theme === 'sepia') document.getElementById('btnThemeSepia').classList.add('active');
      if (theme === 'dark') document.getElementById('btnThemeDark').classList.add('active');
      if (theme === 'light') document.getElementById('btnThemeLight').classList.add('active');

      try {{
        localStorage.setItem('digital_awareness_theme', theme);
      }} catch(e) {{}}
    }}

    function cycleTheme() {{
      if (currentTheme === 'sepia') setTheme('dark');
      else if (currentTheme === 'dark') setTheme('light');
      else setTheme('sepia');
    }}

    // Font Size Scaling
    function changeFontSize(delta) {{
      currentFontScale = Math.max(0.85, Math.min(1.4, currentFontScale + delta));
      document.documentElement.style.setProperty('--font-scale', currentFontScale);
      try {{
        localStorage.setItem('digital_awareness_font_scale', String(currentFontScale));
      }} catch(e) {{}}
    }}

    // Drawer Toggle
    function toggleDrawer() {{
      const drawer = document.getElementById('drawerOverlay');
      drawer.classList.toggle('open');
    }}

    function closeDrawer() {{
      const drawer = document.getElementById('drawerOverlay');
      drawer.classList.remove('open');
    }}

    function openDownloadModal() {{
      toggleDrawer();
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
      }} else {{
        document.exitFullscreen().catch(() => {{}});
      }}
    }}

    // Populate TOC Drawer
    function initDrawerTOC() {{
      const list = document.getElementById('drawerTocList');
      list.innerHTML = '';
      TOC_CHAPTERS.forEach(([chIdx, title, pNum]) => {{
        const li = document.createElement('li');
        li.className = 'toc-list-item';
        li.onclick = () => goToPage(pNum);
        li.innerHTML = `
          <span class="toc-item-title">${{title}}</span>
          <span class="toc-item-dots"></span>
          <span class="toc-item-page">ص ${{pNum}}</span>
        `;
        list.appendChild(li);
      }});
    }}

    // Keyboard & Swipe Controls
    window.addEventListener('keydown', (e) => {{
      // In Arabic RTL:
      // Left Arrow advances forward (next page)
      // Right Arrow goes back (prev page)
      if (e.key === 'ArrowLeft') nextSpread();
      else if (e.key === 'ArrowRight') prevSpread();
      else if (e.key === 'Home') goToPage(1);
      else if (e.key === 'End') goToPage(TOTAL_PAGES);
      else if (e.key === 'Escape') closeDrawer();
    }});

    // Touch Swipe Gestures
    let touchStartX = 0;
    let touchStartY = 0;

    window.addEventListener('touchstart', (e) => {{
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }}, {{ passive: true }});

    window.addEventListener('touchend', (e) => {{
      const touchEndX = e.changedTouches[0].screenX;
      const touchEndY = e.changedTouches[0].screenY;
      const dx = touchEndX - touchStartX;
      const dy = touchEndY - touchStartY;

      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {{
        if (dx < 0) {{
          // Swiped Left -> In RTL advances next
          nextSpread();
        }} else {{
          // Swiped Right -> In RTL goes prev
          prevSpread();
        }}
      }}
    }}, {{ passive: true }});

    window.addEventListener('resize', () => {{
      renderBook();
    }});

    // Initialize from saved state
    window.addEventListener('DOMContentLoaded', () => {{
      initDrawerTOC();

      try {{
        const savedTheme = localStorage.getItem('digital_awareness_theme');
        if (savedTheme) setTheme(savedTheme);

        const savedFont = localStorage.getItem('digital_awareness_font_scale');
        if (savedFont) changeFontSize(parseFloat(savedFont) - 1.0);

        const savedPage = localStorage.getItem('digital_awareness_last_page');
        if (savedPage) {{
          const p = parseInt(savedPage, 10);
          if (p > 1 && p <= TOTAL_PAGES) {{
            currentPage = p;
          }}
        }}
      }} catch(e) {{}}

      renderBook();
    }});
  </script>
</body>
</html>'''

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(reader_html)

print(f"Generated index.html successfully: {INDEX_FILE} ({os.path.getsize(INDEX_FILE):,} bytes)")

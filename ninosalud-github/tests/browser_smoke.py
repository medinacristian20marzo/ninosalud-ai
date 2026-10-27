"""Optional Chromium DOM smoke test, not a hosted-deployment test.
Run: pip install -r requirements-dev.txt; playwright install chromium;
     python tests/browser_smoke.py
Set CHROMIUM_EXECUTABLE to use a system Chromium.
"""
from pathlib import Path
import os,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def source(path):
    text=path.read_text()
    def inline(m):
        script=(path.parent/m.group(1)).resolve()
        if not script.is_relative_to(ROOT):raise ValueError('Script outside repository')
        return '<script>'+script.read_text().replace('</script','<\\/script')+'</script>'
    return re.sub(r'<script\s+src="([^\"]+)"\s*>\s*</script>',inline,text)
def main():
    with sync_playwright() as p:
        options={'headless':True}
        if os.getenv('CHROMIUM_EXECUTABLE'):options['executable_path']=os.environ['CHROMIUM_EXECUTABLE']
        browser=p.chromium.launch(**options);page=browser.new_page(viewport={'width':1440,'height':960})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(source(ROOT/'app/index.html'))
        tabs=page.locator('button[data-tab]').evaluate_all('(els)=>els.map(e=>e.dataset.tab)')
        for tab in tabs:
            page.click('button[data-tab="'+tab+'"]')
            assert page.locator('#'+tab).is_visible(),tab
        page.click('button[data-tab="edaV07"]')
        page.select_option('#edaProvinceV07','PIURA');page.select_option('#edaYearV07','2025')
        page.click('button[data-tab="regionalV10"]')
        page.select_option('#regionalYearV10','2025');page.select_option('#regionalProvinceV10','HUANCABAMBA')
        evidence=browser.new_page();evidence.set_content(source(ROOT/'app/research_evidence.html'))
        assert evidence.locator('#sensitivity').count()==1
        assert not errors,errors
        print('PASS: 7 dynamic tabs, selected filters and evidence page; no JavaScript exceptions.')
        print('Boundary: DOM-loaded local source; hosted URL, real navigation and account submission are not tested.')
        browser.close()
if __name__=='__main__':main()

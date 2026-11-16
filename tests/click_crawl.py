"""Clicks every visible button and tab on every screen for every role, and records any script error."""
import os, json
from playwright.sync_api import sync_playwright
U='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','index.html'))
SKIP=('Sign out','Reset sample data','Download','NIBSS','Download PDF','Print')
out=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1360,'height':900}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('dialog',lambda d:d.dismiss())
    pg.goto(U); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(400)
    roles=pg.evaluate("__pos.roles()"); clicks=0
    for role in roles:
        pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300); pg.evaluate(f"__pos.as('{role}')"); pg.wait_for_timeout(150)
        routes=list(dict.fromkeys(pg.evaluate("Array.from(document.querySelectorAll('#nav a')).map(a=>a.getAttribute('href').slice(1))")))
        for r in routes:
            pg.goto(U+'#'+r); pg.wait_for_timeout(150)
            n=pg.evaluate("Array.from(document.querySelectorAll('#view button, #view [role=tab], #view tr[tabindex], #view li[tabindex], #view article[tabindex]')).length")
            for i in range(min(n,30)):
                els=pg.query_selector_all('#view button, #view [role=tab], #view tr[tabindex], #view li[tabindex], #view article[tabindex]')
                if i>=len(els): break
                el=els[i]
                try:
                    txt=(el.inner_text() or '')[:40]
                    if any(s in txt for s in SKIP) or not el.is_visible() or el.is_disabled(): continue
                    before=len(errs); el.click(timeout=1500); pg.wait_for_timeout(120); clicks+=1
                    if pg.query_selector('#drawer.open'):
                        for dbtn in pg.query_selector_all('#drawer button')[:6]:
                            t2=(dbtn.inner_text() or '')[:30]
                            if dbtn.is_visible() and not dbtn.is_disabled() and not any(s in t2 for s in SKIP) and t2.strip() not in ('×',''):
                                try: dbtn.click(timeout=1000); pg.wait_for_timeout(100); clicks+=1
                                except Exception: pass
                                if not pg.query_selector('#drawer.open'): break
                        pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
                    if len(errs)>before: out.append({'role':role,'route':r,'clicked':txt.strip(),'error':errs[-1]})
                except Exception as ex:
                    pass
                if pg.evaluate('location.hash')!='#'+r: pg.goto(U+'#'+r); pg.wait_for_timeout(120)
    print('clicks',clicks,'errors',len(out))
    seen=set()
    for o in out:
        k=o['error'][:80]
        if k in seen: continue
        seen.add(k); print(json.dumps(o)[:400])

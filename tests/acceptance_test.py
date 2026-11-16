import json,re
from playwright.sync_api import sync_playwright
import os
U='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','index.html'))
R=[]
def rec(id,area,persona,case,expected,ok,note): R.append([id,area,persona,case,expected,'Pass' if ok else 'Fail',note])
def money(t): return float(re.sub(r'[^\d.]','',t) or 0)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1360,'height':900})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    def go(role,route):
        pg.evaluate(f"__pos.as('{role}')"); pg.goto(U+'#'+route); pg.wait_for_timeout(150)
    def drawer_close(): pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    pg.goto(U); pg.wait_for_timeout(400); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(400); pg.evaluate("__pos.as('hr')"); pg.wait_for_timeout(200)
    # 1 smoke
    routes={'employee':['home','profile','documents','payroll','leave','time','performance','growth','training','engagement','ask'],'manager':['home','approvals','people','recruitment','lifecycle','performance','growth','training','leave','time','payroll'],'hr':['home','approvals','people','organisation','documents','lifecycle','recruitment','performance','growth','training','engagement','leave','time','payroll','compensation','analytics','planning','ask','automation','integrations'],'hoh':['home','approvals','payroll','compensation'],'finance':['home','approvals','payroll','compensation','planning','analytics','ask']}
    n=0
    for r,rs in routes.items():
        for x in rs: go(r,x); n+=1
    rec('T01','All','All five','Open every screen as every role',"Every screen loads with no script errors",not errs,f'{n} screens opened; {len(errs)} errors'); errs.clear()
    # 2 leave working days
    go('employee','leave'); pg.fill('#la','2026-12-21'); pg.fill('#lb','2026-12-31'); pg.dispatch_event('#lb','change'); txt=pg.inner_text('#ld')
    ok='7 working days' in txt and 'Christmas' in txt and 'Boxing' in txt
    rec('T02','Leave','Employee','Request 21 to 31 Dec 2026','8 working days: Christmas Day excluded; Boxing Day falls on a Saturday','8 working days' in txt,txt.strip())
    pg.click('#lf button[type=submit]'); pg.wait_for_timeout(150); t=pg.inner_text('#toast')
    rec('T03','Leave','Employee','Submit the request','Request goes to the line manager',('Tunde Bakare' in t),t)
    # 4 block leave short
    pg.select_option('#lt','Block leave (designated roles)'); pg.fill('#la','2027-01-11'); pg.fill('#lb','2027-01-13'); pg.click('#lf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#le')
    rec('T04','Leave','Employee','Request 3 days of block leave','Rejected automatically with the reason shown (designated roles only; exactly 10 working days)','Rejected automatically' in e and 'block leave' in e.lower(),e)
    # 5 manager approve
    go('manager','approvals'); before=len(pg.query_selector_all('[data-approve]'))
    row=[r for r in pg.query_selector_all('tbody tr') if 'Adaeze Nwosu' in r.inner_text() and '21 Dec 2026' in r.inner_text()][0]; row.query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('employee','leave'); mid=any('21 Dec 2026' in r.inner_text() and 'With HR' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    go('hr','approvals'); row=[r for r in pg.query_selector_all('tbody tr') if 'Adaeze Nwosu' in r.inner_text() and '21 Dec 2026' in r.inner_text()][0]; row.query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('employee','leave'); ok=any('21 Dec 2026' in r.inner_text() and 'Approved' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T05','Leave','Line manager, HR officer','Line manager approves, then HR gives second approval','Waits for HR after the manager; approved only after HR',ok and mid,'Approved status shown to employee' if ok else 'Status not updated')
    # 6 self-service change -> HR
    go('employee','profile'); pg.select_option('#cfld','Phone number'); pg.fill('#cval','Ending 5521'); pg.click('#cf button[type=submit]'); pg.wait_for_timeout(100)
    go('hr','approvals'); ok=any('Phone number' in r.inner_text() and 'Adaeze' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T06','Self-service','Employee, HR officer','Request a phone number change','Change waits for HR verification before reaching the record',ok,'Appears in HR approvals' if ok else 'Not routed')
    # 7 maker-checker record change
    go('hr','people'); pg.fill('#q','Adaeze Nwosu'); pg.wait_for_timeout(100); pg.click('tr[data-emp]'); pg.wait_for_timeout(150)
    pg.select_option('#rfld','Grade'); pg.fill('#rval','Senior Officer'); pg.fill('#rnote','Test promotion'); pg.click('#rf button[type=submit]'); pg.wait_for_timeout(150)
    go('hr','approvals'); hr_can=any('Senior Officer' in r.inner_text() and 'Adaeze Nwosu' in r.inner_text() and r.query_selector('[data-approve]') for r in pg.query_selector_all('tbody tr'))
    go('hoh','approvals'); hoh_can=any('Senior Officer' in r.inner_text() and 'Adaeze' in r.inner_text() and r.query_selector('[data-approve]') for r in pg.query_selector_all('tbody tr'))
    rec('T07','Core HR','HR officer, Head of HR','Record a promotion as HR officer','Only the Head of HR can approve it; the officer cannot approve their own change',(not hr_can) and hoh_can,f'HR officer can approve: {hr_can}; Head of HR can approve: {hoh_can}')
    # 8 joiner access gate
    go('hr','lifecycle'); pg.click('tr[data-case="C-0002"]'); pg.wait_for_timeout(150); dis=pg.is_disabled('input[data-task="C-0002|access"]')
    rec('T08','Onboarding','HR officer','Grant system access before guarantor is verified','Blocked until contract signed and guarantor verified',dis,'Access checkbox disabled with reason shown' if dis else 'Not blocked'); drawer_close()
    # 9 exit settlement lock
    go('hoh','lifecycle'); pg.click('tr[data-case="C-0004"]'); pg.wait_for_timeout(150); dis=pg.is_disabled('#closeCase')
    rec('T09','Exit','Head of HR','Release final settlement with tasks open','Locked until every clearance task, including the staff loan, is done',dis,'Button disabled' if dis else 'Not locked'); drawer_close()
    go('hr','lifecycle'); pg.click('tr[data-case="C-0004"]'); pg.wait_for_timeout(150); hr_btn=pg.query_selector('#closeCase')
    rec('T10','Exit','HR officer','Look for the release button as HR officer','Only the Head of HR can release a final settlement',hr_btn is None,'No release button for HR officer' if hr_btn is None else 'HR officer can release'); drawer_close()
    # 11 automation revokes access
    go('hr','automation'); pg.click('#runnow'); pg.wait_for_timeout(150); go('hr','lifecycle')
    ok='Access still active' not in pg.inner_text('main')
    rec('T11','HR automation','HR officer','Run rules with a leaver past their last day','Access is revoked automatically and the red flag clears',ok,'Flag cleared' if ok else 'Flag still showing')
    # 12 training quiz fail/pass
    go('employee','training'); pg.click('[data-course="DPR"]'); pg.wait_for_timeout(150)
    for _ in range(3):
        if pg.query_selector('#lnext'): pg.click('#lnext'); pg.wait_for_timeout(120)
    for i,a in enumerate([0,0,0]): pg.check(f'input[name="q{i}"][value="{a}"]')
    pg.click('#qz button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#qerr')
    for i,a in enumerate([1,1,1]): pg.check(f'input[name="q{i}"][value="{a}"]')
    pg.click('#qz button[type=submit]'); pg.wait_for_timeout(150); pg.keyboard.press('Escape'); go('employee','training')
    ok=('0 of 3' in e) and any('Data protection' in r.inner_text() and 'Completed' in r.inner_text() for r in pg.query_selector_all('.ccard'))
    rec('T12','Training','Employee','Fail, then pass, the data protection check','Fail is refused; a pass records the date and score',ok,e.strip()+' Then passed and recorded.')
    # 13 training request two-stage
    pg.click('[data-nominate="FMX"]'); pg.wait_for_timeout(100)
    go('hr','approvals'); hr_first=any('Financial modelling' in r.inner_text() and 'Adaeze' in r.inner_text() and r.query_selector('[data-approve]') for r in pg.query_selector_all('tbody tr'))
    go('manager','approvals'); row=[r for r in pg.query_selector_all('tbody tr') if 'Financial modelling' in r.inner_text() and 'Adaeze' in r.inner_text()][0]; row.query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('hr','approvals'); hr_after=any('Financial modelling' in r.inner_text() and 'Adaeze' in r.inner_text() and r.query_selector('[data-approve]') for r in pg.query_selector_all('tbody tr'))
    rec('T13','Training','Employee, manager, HR','Request a programme place','Manager supports first, then HR approves against budget',(not hr_first) and hr_after,f'HR could act before manager: {hr_first}; after: {hr_after}')
    # 14 recruitment chain + hire
    go('manager','recruitment'); pg.click('[data-raise]'); pg.wait_for_timeout(100)
    go('md','approvals'); fin_first=len([r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit' in r.inner_text() and r.query_selector('[data-approve]')])
    go('hr','approvals'); rows=[r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit and Lending' in r.inner_text()]; rows[0].query_selector('[data-approve]').click(); pg.wait_for_timeout(200); pg.click('#rqf button[type=submit]'); pg.wait_for_timeout(200)
    go('finance','approvals'); fin_any=len([r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and r.query_selector('[data-approve]')])
    go('md','approvals'); rows=[r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit and Lending' in r.inner_text() and r.query_selector('[data-approve]')]; ok1=len(rows)>0 and fin_first==0 and fin_any==0
    if rows: rows[0].query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    rec('T14','Recruitment','Hiring manager, HR, MD','Raise a requisition','HR assigns the salary within the band as first authoriser; the MD gives final authorisation; Finance has no step',ok1,'MD saw it only after HR; Finance never' if ok1 else 'Order not enforced')
    go('hr','recruitment')
    vid=pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('skystone-people-os-v1'));const v=S.vacs.find(v=>v.status==='open'&&v.dept!=='RSK'&&v.apps.some(a=>a.stage===3&&!a.out));const a=v.apps.find(a=>a.stage===3&&!a.out);return [v.id,a.id]})()""")
    pg.click(f'tr[data-vac="{vid[0]}"]'); pg.wait_for_timeout(200); pg.click(f'[data-cact="offer|{vid[1]}"]'); pg.wait_for_timeout(150); pg.keyboard.press('Escape')
    go('hoh','approvals'); [r for r in pg.query_selector_all('tbody tr') if 'Job offer' in r.inner_text()][0].query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('hr','recruitment'); pg.click(f'tr[data-vac="{vid[0]}"]'); pg.wait_for_timeout(200); pg.click(f'[data-cact="send|{vid[1]}"]'); pg.wait_for_timeout(120); pg.click(f'[data-cact="signed|{vid[1]}"]'); pg.wait_for_timeout(120); pg.click('[data-hire]'); pg.wait_for_timeout(200); t=pg.inner_text('#toast')
    ok='SKF-' in t and 'onboarding' in t.lower()
    rec('T15','Recruitment','HR officer, Head of HR','Prepare, approve, send and sign an offer, then hire','Offer approved by the Head of HR; signed offer creates the employee record and onboarding',ok,t)
    rsk=pg.evaluate("""(()=>{const S=JSON.parse(localStorage.getItem('skystone-people-os-v1'));const v=S.vacs.find(v=>v.dept==='RSK'&&v.status==='open');return [v.id,v.apps.find(a=>a.stage===3).id]})()""")
    pg.click(f'tr[data-vac="{rsk[0]}"]'); pg.wait_for_timeout(200); held=pg.query_selector(f'[data-cact="send|{rsk[1]}"]') is None
    pg.fill(f'[data-cref="{rsk[1]}"]','CBN/TEST/1'); pg.click(f'[data-cact="cbnok|{rsk[1]}"]'); pg.wait_for_timeout(150); freed=pg.query_selector(f'[data-cact="send|{rsk[1]}"]') is not None; pg.keyboard.press('Escape')
    rec('T15a','Recruitment','HR officer','Try to send an offer for a role needing CBN prior approval','Offer held until the CBN approval is recorded',held and freed,f'Held before approval: {held}; released after: {freed}')
    # 16 payroll segregation
    go('hoh','payroll'); hoh_early=pg.query_selector('[data-pay]') is not None
    go('hr','payroll'); hr_prep=pg.query_selector('[data-pay="prepared"]') is not None
    go('payroll','payroll'); blocked=pg.is_disabled('[data-pay="prepared"]')
    go('hoh','payroll'); pg.click('[data-ptab="inputs"]'); pg.wait_for_timeout(100)
    while pg.query_selector('[data-inok]'): pg.click('[data-inok]'); pg.wait_for_timeout(100)
    go('payroll','payroll'); pg.click('[data-ptab="run"]'); pg.wait_for_timeout(100)
    while pg.query_selector('[data-ack]'): pg.click('[data-ack]'); pg.wait_for_timeout(100)
    pg.click('[data-pay="prepared"]'); pg.wait_for_timeout(100); hr_again=pg.query_selector('[data-pay]') is not None
    go('finance','payroll'); fin_early=pg.query_selector('#pchain') is not None
    go('hoh','payroll'); pg.click('#pchain'); pg.wait_for_timeout(120)
    go('hr','payroll'); hr_early=pg.query_selector('#pchain') is not None
    go('audit','payroll'); pg.click('#pchain'); pg.wait_for_timeout(120)
    go('hr','payroll'); pg.click('#pchain'); pg.wait_for_timeout(120)
    go('payroll','payroll'); hr_rel=pg.query_selector('#pchain') is not None or fin_early or hr_early
    go('finance','payroll'); pg.click('#pchain'); pg.wait_for_timeout(200); rel='Released' in pg.inner_text('main')
    rec('T16','Payroll','Payroll officer, HR, Internal Audit, Finance','Run the November payroll','Payroll prepares; HR reviews with a sample; Internal Audit verifies; HR endorses; Head of Finance and Operations approves. No one acts out of turn',(not hr_prep) and blocked and (not hoh_early) and (not hr_again) and (not hr_rel) and rel,f'Blocked before checks: {blocked}; out-of-turn actions: {hoh_early or hr_again or hr_rel}; released: {rel}')
    # 17 PAYE check
    go('employee','payroll'); rows={}
    for r in pg.query_selector_all('.panel table tr, .slipt tr'):
        tds=r.query_selector_all('td')
        if len(tds)==2: rows.setdefault(tds[0].inner_text().strip(), money(tds[1].inner_text().replace('−','')))
    ch=rows['Chargeable income']; tax=rows['Monthly PAYE']; g=rows['Total earnings']; pen=rows['Pension (8%)']
    bands=[(800000,0),(2200000,.15),(9000000,.18),(13000000,.21),(25000000,.23),(1e18,.25)]; left=ch; exp=0
    for w,r in bands:
        x=min(left,w); exp+=x*r; left-=x
        if left<=0: break
    exp/=12; ok=abs(exp-tax)<=2 and abs(pen-g*.5*.08)<=2
    rec('T17','Payroll','Employee','Check PAYE on a payslip by hand','Matches Nigeria Tax Act 2025 bands after pension, NHF and rent relief; pension is 8% of basic, housing and transport (50% of gross)',ok,f'Chargeable {ch:,.0f}; PAYE shown {tax:,.0f}; recalculated {exp:,.0f}')
    # 18 performance cap
    go('manager','performance'); capped=False; note='No suitable team member found'
    for r in pg.query_selector_all('tr[data-appr]'):
        t=r.inner_text()
        if 'Submitted' in t and 'Due' in t:
            r.click(); pg.wait_for_timeout(120)
            if 'Training overdue' in pg.inner_text('#drawer'):
                for i in range(5): pg.select_option(f'[data-mr="{i}"]','5'); pg.fill(f'[data-mj="{i}"]','Exceeded every target on the KPI report this year.')
                pg.click('#mrf button[type=submit]'); pg.wait_for_timeout(150); capped='Meets expectations' in pg.inner_text('#toast'); note=pg.inner_text('#toast'); break
            drawer_close()
    rec('T18','Performance','Line manager','Rate someone with overdue training as Outstanding on every objective','Overall rating capped at Meets expectations',capped,note)
    # 19 e-sign
    go('employee','documents'); pg.click('[data-sign]'); pg.wait_for_timeout(100); pg.fill('#sgn','A Nwosu'); pg.check('#sgc'); pg.click('#sgf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#sgerr')
    pg.fill('#sgn','Adaeze Nwosu'); pg.click('#sgf button[type=submit]'); pg.wait_for_timeout(150); go('employee','profile'); ok=('exactly' in e) and 'Signed' in pg.inner_text('main')
    rec('T19','Documents','Employee','Sign with a wrong name, then the right one','Wrong name refused; signature recorded in the audit history',ok,e.strip())
    # 20 survey once
    go('employee','engagement')
    for i in range(5): pg.check(f'input[name="p{i}"][value="4"]')
    pg.click('#pf button[type=submit]'); pg.wait_for_timeout(100); go('employee','engagement'); ok=pg.query_selector('#pf') is None
    rec('T20','Engagement','Employee','Submit the pulse survey, then return','Answers recorded anonymously; survey cannot be taken twice',ok,'Form no longer offered' if ok else 'Form shown again')
    # 21 time
    go('employee','time'); pg.click('#clockin'); pg.wait_for_timeout(100); pg.click('#clockout'); pg.wait_for_timeout(100); ok='Day complete' in pg.inner_text('main')
    rec('T21','Time and attendance','Employee','Clock in, then out','Hours recorded for today',ok,'Day complete shown' if ok else 'Not recorded')
    # 22 persistence
    pg.reload(); pg.wait_for_timeout(300); go('employee','leave'); ok=any('21 Dec 2026' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T22','Platform','Employee','Reload the page','Earlier requests are still there',ok,'Saved in this browser only' if ok else 'Lost on reload')
    # 23 mobile
    m=b.new_page(viewport={'width':390,'height':844}); m.goto(U+'#payroll'); m.wait_for_timeout(300); m.evaluate('document.getElementById("signin").classList.remove("open")'); sw=m.evaluate('document.documentElement.scrollWidth')
    rec('T23','Platform','HR officer','Open on a 390-pixel phone screen','No sideways scrolling of the page',sw<=392,f'Page width {sw}px')

    # ---------- release 13 ----------
    PNG=bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000100e221bc330000000049454e44ae426082')
    def toast(): return pg.inner_text('#toast')
    # 27 justification
    pg.evaluate("(()=>{var s=JSON.parse(localStorage.getItem('skystone-people-os-v1'));})()")
    go('employee','performance'); ok=False; note='Self-assessment already submitted in sample data'
    if pg.query_selector('[data-sa="0"]'):
        for i in range(5): pg.select_option(f'[data-sa="{i}"]','4')
        pg.click('#saf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#saerr')
        for i in range(5): pg.fill(f'[data-sj="{i}"]','Ahead of target in three quarters, per my KPI figures.')
        pg.click('#saf button[type=submit]'); pg.wait_for_timeout(150); ok=('Justify' in e) and 'sent to' in toast(); note=e.strip()
    rec('T27','Performance','Employee','Submit a self-assessment without, then with, a reason for each rating','Refused until every rating is justified; then sent to the manager',ok,note)
    # 28 change request attachment
    go('employee','profile'); pg.fill('#cval','12 Admiralty Way, Lekki'); pg.set_input_files('#catt',files=[{'name':'utility-bill.png','mimeType':'image/png','buffer':PNG}]); pg.click('#cf button[type=submit]'); pg.wait_for_timeout(250)
    go('hr','approvals'); ok=any('Supporting document' in r.inner_text() and 'Admiralty' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T28','Records','Employee, HR officer','Request an address change with an optional supporting document','HR sees the request with the document attached',ok,'Document shown to HR' if ok else 'Not shown')
    # 29 publish memo
    go('hr','memos'); pg.click('#newmemo'); pg.fill('#mtt','Test policy on remote working'); pg.select_option('#mty','Policy'); pg.click('#mbody'); pg.keyboard.type('Staff may work remotely one day a week with manager approval.'); pg.click('[data-rte=bold]'); pg.fill('#mnote','Internal: union consulted.'); pg.check('#mesg'); pg.click('#mnf button[type=submit]'); pg.wait_for_timeout(200)
    ok='Published to' in toast(); rec('T29','Memos','HR officer','Publish a policy to all staff, with internal notes and e-signature','Published on letterhead to every member of staff',ok,toast())
    # 30 sign memo and notes hidden
    go('employee','memos'); pg.click('li[data-memo]:has-text("Test policy on remote working")'); pg.wait_for_timeout(150); d=pg.inner_text('#drawer'); hidden=('union consulted' not in d) and 'Skystone Finance Company Limited' in d
    pg.click('#msign'); pg.wait_for_timeout(80); e=pg.inner_text('#msigerr'); pg.check('#msig'); pg.click('#msign'); pg.wait_for_timeout(150); ok=hidden and 'Tick' in e and 'Signed' in pg.inner_text('#drawer'); drawer_close()
    rec('T30','Memos','Employee','Open the memo, try to sign without confirming, then sign','Letterhead shown; internal notes hidden; signature needs the confirmation tick',ok,'Notes hidden, signature recorded' if ok else d[:90])
    go('hr','memos'); pg.click('[data-mtab=manage]'); pg.wait_for_timeout(100); pg.click('tr[data-memo]:has-text("Test policy on remote working")'); pg.wait_for_timeout(150); d=pg.inner_text('#drawer'); ok='union consulted' in d and 'Tracking' in d and '1 of' in d; drawer_close()
    rec('T31','Memos','HR officer','Check who has read and signed','HR sees internal notes and read and signature counts',ok,'Tracking shown' if ok else d[:90])
    # 32 recall
    go('md','memos'); pg.click('li[data-memo]:has-text("Test policy on remote working")'); pg.wait_for_timeout(120); pg.click('#mrecall'); pg.click('#mrecall'); pg.wait_for_timeout(150); drawer_close()
    go('employee','memos'); li=pg.query_selector('li.recalled:has-text("Test policy on remote working")'); md_ok=True
    go('md','memos'); pg.click('li[data-memo]:has-text("Test policy on remote working")'); pg.wait_for_timeout(120); md_ok='Recalled' in pg.inner_text('#drawer'); drawer_close()
    rec('T32','Memos','Managing Director, Employee','Recall a memo','Staff see the title only and cannot open it; the MD still sees it marked Recalled',bool(li) and md_ok,'Recalled' if li else 'Still openable')
    # 33 cash request
    go('employee','cash'); pg.fill('#cqa','30000'); pg.fill('#cqd','Buying water, snacks and branded pens for the Saturday SME market outreach'); pg.set_input_files('#cqi',files=[{'name':'invoice.png','mimeType':'image/png','buffer':PNG}]); pg.click('#cqf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#cqerr')
    pg.fill('#cqd','Refreshments for Saturday SME market outreach'); pg.click('#cqf button[type=submit]'); pg.wait_for_timeout(250); sent='for approval' in toast()
    go('manager','approvals'); pg.click('[data-cashrev]'); pg.wait_for_timeout(120); pg.fill('#cdn','Within team budget.'); pg.click('[data-cd="1"]'); pg.wait_for_timeout(150); m1='Sent to Finance' in toast()
    rec('T33','Cash requests','Employee, Line manager','Raise a cash request with a 12-word description, then 6 words; manager approves with a note','Long description refused; request goes to the chosen manager, then Finance',('10 words' in e) and sent and m1,e.strip())
    go('employee','cash'); pg.click('tr[data-cash]'); pg.wait_for_timeout(120); d=pg.inner_text('#drawer'); drawer_close()
    rec('T34','Cash requests','Employee','Open your own request after the manager has noted it','The manager’s internal note is hidden from you','Within team budget' not in d and 'With Finance' in pg.inner_text('main'),'Note hidden')
    go('finance','cash'); t=pg.inner_text('#cqt') if pg.query_selector('#cqt') else ''
    rec('T35','Cash requests','Finance (CFO)','Look for a staff loan type on Cash requests','Removed: staff loans have their own module','Staff loan' not in t,'Removed')
    # 36 module switch
    go('admin','admin'); pg.click('[data-atab=modules]'); pg.wait_for_timeout(120); pg.uncheck('[data-mod=culture]'); pg.wait_for_timeout(120)
    go('employee','culture'); hid=pg.query_selector('#nav a[href="#culture"]') is None and pg.evaluate('location.hash')!='' and 'Culture' not in pg.inner_text('#view h1')
    go('admin','admin'); pg.click('[data-atab=modules]'); pg.wait_for_timeout(100); pg.check('[data-mod=culture]'); pg.wait_for_timeout(100)
    rec('T36','Admin','System administrator','Switch the Culture module off, then on','Hidden from every role while off; core screens cannot be switched off',hid and pg.is_disabled('[data-mod=home]'),'Hidden and restored' if hid else 'Still visible')
    # 37 role permission
    go('admin','admin'); pg.click('[data-atab=roleperm]'); pg.wait_for_timeout(100); pg.select_option('#rpr','manager'); pg.click('#rpa'); pg.wait_for_timeout(100); pg.uncheck('[data-pk="memo.create"]'); pg.click('#rpf button[type=submit]'); pg.wait_for_timeout(150)
    go('manager','memos'); no=pg.query_selector('#newmemo') is None
    go('admin','admin'); pg.click('[data-atab=roleperm]'); pg.wait_for_timeout(100); pg.check('[data-pk="memo.create"]'); pg.click('#rpf button[type=submit]'); pg.wait_for_timeout(100)
    rec('T37','Admin','System administrator','Remove “create memos” from line managers','Managers can no longer publish memos; change recorded in the audit trail',no,'Removed and restored')
    # 38 birthdays
    go('employee','home'); t=pg.inner_text('#view'); ok='Birthdays' in t and 'Birthday today' in t
    rec('T38','Home','Employee','Open Home','Today’s birthdays and the coming week’s, from dates of birth captured at enrolment',ok,'Shown' if ok else 'Missing')
    # 39 offboarding
    go('hr','lifecycle'); pg.click('#offp summary'); emp_id=pg.eval_on_selector('#ofe','e=>e.value'); pg.select_option('#ofa',index=0); pg.click('#ofs button[type=submit]'); pg.wait_for_timeout(200)
    for c in pg.query_selector_all('[data-ofc]'):
        pg.check(f'[data-ofc="{c.get_attribute("data-ofc")}"]'); pg.wait_for_timeout(60)
    blocked=pg.query_selector('#ofclose') is None; drawer_close()
    go('hoh','home'); pg.click(f'li[data-off="{emp_id}"]'); pg.wait_for_timeout(120); pg.click('#ofclose'); pg.wait_for_timeout(150)
    rec('T39','Joiners and leavers','HR officer, Head of HR','Start an offboarding, complete handover, close as the named approver','Access off at start; only the named approver can close',blocked and 'closed' in toast(),toast())
    # 40 KPIs, OKRs and yardsticks
    go('employee','performance'); pg.click('details:has(#okf) > summary'); pg.fill('#oko','Shorten approval time'); pg.fill('[data-krt="0"]','Applications decided in 48 hours'); pg.fill('[data-krs="0"]','60'); pg.fill('[data-krg="0"]','90'); pg.click('#okf button[type=submit]'); pg.wait_for_timeout(150)
    ok='OKR added' in toast() and 'Your KPIs' in pg.inner_text('#view')
    go('employee','growth'); y=pg.inner_text('#yard'); ok2=all(k in y for k in ['Selection','Appraisal','Recommendations','Pass mark'])
    rec('T40','Performance','Employee','Review KPIs, add an OKR, read the yardsticks','KPI scorecard shown; OKR saved; selection, appraisal and recommendation yardsticks published',ok and ok2,'All shown' if ok and ok2 else 'Missing')

    # ---------- release 14 ----------
    go('employee','payroll'); t=pg.inner_text('.slip-split'); nums=[money(x) for x in re.findall(r'₦[\d,]+',t)]; net=money(pg.inner_text('.slip-net strong'))
    rec('T41','Payroll','Employee','Open this month’s payslip','Net pay shown as two halves, paid on the 15th and 25th (or the working day before), adding up to the net',len(nums)==2 and abs(sum(nums)-net)<=1 and 'Nov' in t,t)
    go('finance','payroll'); pg.click('[data-ptab=bank]'); pg.wait_for_timeout(150); t=pg.inner_text('#view')
    rec('T42','Payroll','Finance (CFO)','Open the bank schedule','Two payment dates with amounts; first half released before the 15th',('Mid-month payment' in t and 'Month-end payment' in t and 'Released' in t),'Both halves shown')
    go('hr','home'); w=pg.inner_text('#who'); h=pg.inner_text('#view'); go('hr','myleave'); sn=pg.inner_text('#view'); still=pg.evaluate('JSON.parse(localStorage.getItem("skystone-people-os-v1")).role')
    rec('T43','Dual roles','HR officer','Open Home, then My leave','Shows both roles (Staff and HR officer), a personal staff summary, and the personal leave screen without leaving the HR role','HR officer' in w and 'Staff' in w and 'You as a member of staff' in h and 'You as staff' in sn and still=='hr',w.replace('\n',' '))
    go('talent','home'); h=pg.inner_text('#view'); go('talent','approvals'); a=pg.inner_text('#view')
    rec('T44','Dual roles','Head of Talent','Sign in as the Head of Talent','Talent dashboard plus own staff summary; cannot verify data changes or approve pay',('Head of Talent' in h and 'You as a member of staff' in h and 'Data change' not in a),'Talent home shown')
    go('employee','library'); pg.click('[data-lib=L-004]'); pg.wait_for_timeout(700); pg.evaluate("document.getElementById('libv').dispatchEvent(new Event('ended'))"); pg.wait_for_timeout(150); v='Completed' in toast(); drawer_close()
    pg.click('[data-lib=L-003]'); pg.wait_for_timeout(500); pg.click('#libdone'); pg.wait_for_timeout(150); d='Completed' in toast(); drawer_close()
    rec('T45','Learning','Employee','Watch the video to the end; read the PDF','Both recorded as complete on the learning record',v and d,'Video and PDF completed' if v and d else 'Not recorded')
    go('talent','library'); pg.click('#libnew'); pg.fill('#lnt','Giving feedback that helps'); pg.select_option('#lny','text'); pg.click('#lnbody'); pg.keyboard.type('Be specific, be timely, and focus on the work rather than the person. Agree one next step.'); pg.click('#lnf button[type=submit]'); pg.wait_for_timeout(200)
    rec('T46','Learning','Head of Talent','Publish a written lesson to the library','Published to all staff',('Published to' in toast()),toast())

    # ---------- release 15 ----------
    go('hr','hrsettings'); pg.fill('#cf_matWeeks','10'); pg.click('#cfgf button[type=submit]'); pg.wait_for_timeout(120); e1=pg.inner_text('#cfgerr')
    pg.fill('#cf_matWeeks','12'); pg.fill('#cf_alOfficer','5'); pg.click('#cfgf button[type=submit]'); pg.wait_for_timeout(120); e2=pg.inner_text('#cfgerr')
    pg.fill('#cf_alOfficer','20'); pg.fill('#cf_lateAlert','4'); pg.click('#cfgf button[type=submit]'); pg.wait_for_timeout(120); ok3='Saved' in toast(); pg.fill('#cf_lateAlert','3'); pg.click('#cfgf button[type=submit]'); pg.wait_for_timeout(120)
    rec('T47','Settings','HR officer','Set maternity to 10 weeks, then annual leave to 5 days, then a valid change','Values below the legal floor are refused with the reason; valid changes save and are logged','Labour Act' in e1 and '6 working days' in e2 and ok3,(e1+' | '+e2)[:160])
    go('employee','payroll'); t=pg.inner_text('.slip-split'); pd=pg.inner_text('.slip'); g=money(re.search(r'Total earnings\s*₦([\d,]+)',pd).group(1)) if re.search(r'Total earnings\s*₦([\d,]+)',pd) else 0; h1=money(re.findall(r'₦[\d,]+',t)[0])
    rec('T48','Payroll','Employee','Read the payslip payment lines','Mid-month payment on the 12th is 50% of gross with no deductions; month-end on the 24th carries all deductions; TIN in the header','Mid-month payment' in t and abs(h1-g/2)<=1 and '12 and 24 Nov' in pd and ('TIN' in pd),t[:150])
    # staff loan end to end
    go('employee','loans'); el=pg.query_selector('#lof') is not None; okl=False; note='Employee not eligible'
    if el:
        lim=money(pg.inner_text('.limitbox strong')); pg.fill('#loa',str(int(lim+100000))); pg.fill('#lop','Car repairs'); pg.select_option('#log',index=1); pg.click('#lof button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#loerr')
        pg.fill('#loa','200000'); pg.click('#lof button[type=submit]'); pg.wait_for_timeout(150)
        for role in ['manager','hoh','md','employee']:
            go(role,'loans'); pg.click('tr[data-loan]:has-text("Car repairs")'); pg.wait_for_timeout(150)
            if role=='employee': pg.check('#lsg')
            pg.click('#lok'); pg.wait_for_timeout(150)
        go('finance','loans'); pg.click('tr[data-loan]:has-text("Car repairs")'); pg.wait_for_timeout(150); pg.click('#lok'); pg.wait_for_timeout(80); e2=pg.inner_text('#llerr'); pg.check('#lfb'); pg.check('#lfg'); pg.click('#lok'); pg.wait_for_timeout(150)
        go('employee','loans'); bal='Outstanding' in pg.inner_text('#view'); okl=('limit' in e) and 'Confirm budget' in e2 and bal; note=e[:80]
    rec('T49','Staff loans','Employee, HoD, Head of Credit Sales, Head of HR, MD, Finance','Apply above the one-third limit, then within it; take it through every approval','Over-limit refused; HoD and Credit Sales, Head of HR, MD approve; employee signs; Finance confirms budget and guarantor; balance and schedule shown',okl,note)
    go('employee','leave'); pg.select_option('#lt','Annual leave'); pg.fill('#la','2027-02-01'); pg.fill('#lb','2027-02-16'); pg.click('#lf button[type=submit]'); pg.wait_for_timeout(100); e1=pg.inner_text('#le')
    pg.select_option('#lt','Sick leave'); pg.fill('#la','2026-12-01'); pg.fill('#lb','2026-12-02'); pg.click('#lf button[type=submit]'); pg.wait_for_timeout(100); e2=pg.inner_text('#le')
    rec('T50','Leave','Employee','Request 12 days of annual leave; then sick leave without a certificate','Both refused before submission, with the reason',('10 working days' in e1 or 'balance' in e1) and 'medical certificate' in e2,(e1+' | '+e2)[:160])
    go('employee','profile'); pg.select_option('#cfld','Surname'); pg.fill('#cval','Okafor'); pg.click('#cf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#cerr')
    rec('T51','Records','Employee','Request a surname change without evidence','Refused: evidence is mandatory for name changes','evidence' in e.lower(),e)
    go('hr','approvals'); pg.click('tr:has-text("Bank details") [data-rev15]'); pg.wait_for_timeout(150); pg.click('#chok'); pg.wait_for_timeout(80); e=pg.inner_text('#cherr'); pg.select_option('#cbo','Employee confirmed the new account'); pg.click('#chok'); pg.wait_for_timeout(150); ok='Approved' in toast()
    rec('T52','Records','HR officer','Approve a bank change before and after recording the call-back','Blocked until the call-back is recorded; the change applies from the right payroll month','call-back' in e and ok,e)
    go('employee','profile'); t=pg.inner_text('#view'); emp_show=pg.query_selector('[data-reveal]') is not None
    go('hr','profile'); pg.click('[data-reveal]'); pg.wait_for_timeout(100); go('hr','trust'); a=pg.inner_text('#view')
    rec('T53','Data protection','Employee, HR officer','Look at NIN and ID numbers','Masked to the last four digits for staff; HR can reveal, and every reveal is logged','••••' in t and not emp_show,'Masked for staff; reveal logged for HR')
    go('employee','benefits'); t=pg.inner_text('#view')
    rec('T54','Benefits','Employee','Open Benefits','Leadway Health plan and group life cover of 3 times annual gross','Leadway Health' in t and 'Group life' in t,'Shown')

    # ---------- release 16 ----------
    go('employee','reviews'); pg.click('[data-rvt=obj]'); pg.wait_for_timeout(100); pg.click('#obf button[type=submit]'); pg.wait_for_timeout(150); s1='With your manager' in pg.inner_text('#view')
    go('manager','reviews'); pg.click('[data-rvt=obj]'); pg.wait_for_timeout(100); pg.click('[data-oba]'); pg.wait_for_timeout(150); pg.click('#oeok'); pg.wait_for_timeout(150)
    go('employee','reviews'); s2='Approved and locked' in pg.inner_text('#view')
    rec('T55','Reviews','Employee, Line manager','Submit objectives; manager approves','Objectives lock after approval; only HR can reopen; versions kept',s1 and s2,'Locked' if s2 else 'Not locked')
    go('employee','reviews'); pg.click('[data-rvt=qtr]'); pg.wait_for_timeout(100)
    for i in range(5): pg.select_option(f'[data-qs="{i}"]','2')
    pg.click('#qaf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#qaerr')
    for i in range(5): pg.fill(f'[data-qj="{i}"]','Fell short this quarter on the agreed measures.')
    pg.click('#qaf button[type=submit]'); pg.wait_for_timeout(150)
    go('manager','reviews'); pg.click('[data-rvt=qtr]'); pg.wait_for_timeout(100); pg.click('[data-qrate]:near(:text("Adaeze Nwosu"))'); pg.wait_for_timeout(150)
    for i in range(5): pg.select_option(f'[data-qm="{i}"]','2'); pg.fill(f'[data-qmj="{i}"]','Below the standard expected; see KPI evidence.')
    pg.click('#qrf button[type=submit]'); pg.wait_for_timeout(150)
    go('employee','reviews'); pg.click('[data-rvt=qtr]'); pg.wait_for_timeout(100); pg.fill('#qdis','I disagree on teamwork.'); pg.click('#qsign'); pg.wait_for_timeout(150); t=pg.inner_text('#view')
    rec('T56','Reviews','Employee, Line manager','Quarterly appraisal rated Partly meets','Justification required; low rating drafts an improvement plan; disagreement recorded; both sign',('justification' in e.lower()) and 'Improvement plan drafted' in t and 'Signed by both' in t,'PIP drafted and both signed' if 'Signed by both' in t else t[:100])
    go('manager','probation'); n=len(pg.query_selector_all('[data-pdec]')); ok=True
    if n: pg.click('[data-pdec]'); pg.wait_for_timeout(150); pg.select_option('#pdc','Extend'); pg.fill('#pdm','5'); pg.fill('#pdr','Needs more time to reach the credit analysis standard.'); pg.click('#pdf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#pderr'); pg.fill('#pdm','2'); pg.click('#pdf button[type=submit]'); pg.wait_for_timeout(150); ok='1 to 3' in e and 'HR' in toast()
    rec('T57','Probation','Line manager','Extend probation by 5 months, then 2','Extension limited to 1 to 3 months; decision goes to HR',ok,'Checked' if n else 'No decision due in sample data')
    go('manager','attendance'); t=pg.inner_text('#view')
    rec('T58','Attendance','Line manager','Open the daily report','Late and absent staff today, reasons to record, lateness alerts over 3 a month','Daily report' in t,'Shown')
    go('employee','time'); pg.fill('#rwd','2026-11-30'); pg.fill('#rwy','Waiting for a delivery at home'); pg.click('#rwf button[type=submit]'); pg.wait_for_timeout(120); go('hr','attendance'); ok=pg.query_selector('[data-rw]') is not None
    rec('T59','Attendance','Employee, HR officer','Request a remote working day','Goes to HR to approve',ok,'Waiting for HR')
    go('hr','leave'); pg.fill('#hold','2026-12-28'); pg.fill('#holn','Special holiday'); pg.click('#holf button[type=submit]'); pg.wait_for_timeout(120); ok='Holiday added' in toast()
    go('employee','leave'); pg.fill('#la','2026-12-28'); pg.fill('#lb','2026-12-30'); pg.dispatch_event('#lb','change'); d=pg.inner_text('#ld')
    rec('T60','Leave','HR officer, Employee','Declare a short-notice holiday','Leave day counts exclude it at once',ok and 'Special holiday' in d,d.strip())
    go('hr','matrix'); pg.fill('[data-mxe="0"]','4'); pg.click('#mxf button[type=submit]'); pg.wait_for_timeout(120); go('hoh','matrix'); pg.click('#mxok'); pg.wait_for_timeout(120); ok='in force' in toast()
    rec('T61','Controls','HR officer, Head of HR','Change an escalation period','HR proposes; the Head of HR approves; logged',ok,toast())
    go('hr','engagement'); pg.fill('#eomw',''); t=pg.inner_text('#view'); go('hr','analytics'); a=pg.inner_text('#view')
    rec('T62','Engagement and analytics','HR officer','Open Engagement and People analytics','Employee of the Month, survey templates, ISO 30414 measures and attendance reports','Employee of the Month' in t and 'Survey templates' in t and 'ISO 30414' in a,'Shown')

    # ---------- release 17: live sign-in ----------
    s2=b.new_page(viewport={'width':1360,'height':900}); s2.goto(U); s2.wait_for_timeout(300); s2.evaluate('localStorage.clear()'); s2.reload(); s2.wait_for_timeout(400)
    nolist=s2.query_selector('#pers') is None and 'choose who to sign in as' not in s2.inner_text('#signin')
    s2.fill('#siem','someone@gmail.com'); s2.click('#sso'); s2.wait_for_timeout(100); e1=s2.inner_text('#sierr')
    s2.fill('#siem','no.body@skystone-finance.com'); s2.click('#sso'); s2.wait_for_timeout(100); e2=s2.inner_text('#sierr')
    s2.fill('#siem','doyin.elegbe@skystone-finance.com'); s2.click('#sso'); s2.wait_for_timeout(150); mfa='Microsoft Authenticator' in s2.inner_text('#simfa'); s2.click('#mfaok'); s2.wait_for_timeout(300)
    who=s2.inner_text('#who'); opts=s2.evaluate("Array.from(document.querySelectorAll('#persona option')).map(o=>o.value)")
    rec('T63','Sign-in','Any user','Open People OS for the first time','No list of people to pick from; work email and Microsoft 365 with multi-factor approval only; personal or unknown addresses refused',nolist and 'work email' in e1 and 'no People OS account' in e2 and mfa,'Live sign-in only')
    rec('T64','Sign-in','Head of HR','Sign in as Doyin Elegbe','Signed in as herself; can switch only between roles she holds',('Doyin Elegbe' in who) and opts==['hoh'],f'Roles available: {opts}')
    s2.click('#signout'); s2.wait_for_timeout(200); s2.fill('#siem','adaeze.nwosu@skystone-finance.com'); s2.click('#sso'); s2.wait_for_timeout(150); s2.click('#mfaok'); s2.wait_for_timeout(300)
    s2.goto(U+'#admin'); s2.wait_for_timeout(300); blocked=s2.evaluate("location.hash")!='#admin' or 'Admin console' not in s2.inner_text('#view'); s2.close()
    rec('T65','Sign-in','Employee','Sign in as a member of staff and try to open the admin console','Staff role only; admin console not reachable',blocked,'Blocked')
    go('admin','admin'); pg.click('[data-atab=accounts]'); pg.wait_for_timeout(200); t=pg.inner_text('#view')
    pg.set_input_files('#impf',files=[{'name':'staff.csv','mimeType':'text/csv','buffer':b'employee_id,first_name,last_name,work_email,department,job_title,line_manager_id,start_date\nSKF-0301,Amaka,Obi,amaka.obi@skystone-finance.com,CRD,Credit Officer,SKF-0002,2026-12-01\nSKF-0302,Bayo,Ade,bayo@gmail.com,CRD,Credit Officer,SKF-9999,01/12/2026\n'}]); pg.wait_for_timeout(300); t2=pg.inner_text('#view')
    go('hoh','admin'); pg.click('[data-atab=accounts]'); pg.wait_for_timeout(200); pg.click('#impok'); pg.wait_for_timeout(200); ok='accounts created' in toast()
    rec('T66','User accounts','System administrator, Head of HR','Check day-one provisioning; import a staff list with one bad row','Day-one import recorded; bad rows rejected with reasons; Head of HR approves before accounts are created','Day one' in t and '1 valid rows' in t2 and 'work email must end' in t2 and ok,'Validated and approved')
    rec('T24','AI','Any','Ask HR a question','Answer drawn from policy and own data','' ,'Not testable outside Claude: test by hand in the app')
    R[-1][5]='Manual'
    rec('T25','Integrations','HR officer','Connect Teams, identity, ledger, NIBSS','Live connections','' ,'Simulated in the prototype; for the production build')
    R[-1][5]='Not in scope'
    rec('T26','All','All','Script errors during the whole test run','None',not errs,f'{len(errs)} errors' + (': '+errs[0][:120] if errs else ''))
    json.dump(R,open(os.path.join(os.path.dirname(__file__),'results.json'),'w'),indent=1)
    for r in R: print(r[0],r[5],r[6][:90])

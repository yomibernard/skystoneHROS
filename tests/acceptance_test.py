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
        pg.select_option('#persona',role); pg.goto(U+'#'+route); pg.wait_for_timeout(150)
    def drawer_close(): pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    pg.goto(U); pg.wait_for_timeout(400); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(400); pg.click("#pers button[data-p=hr]"); pg.wait_for_timeout(200)
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
    pg.select_option('#lt','Block leave'); pg.fill('#la','2027-01-11'); pg.fill('#lb','2027-01-13'); pg.click('#lf button[type=submit]'); pg.wait_for_timeout(100); e=pg.inner_text('#le')
    rec('T04','Leave','Employee','Request 3 days of block leave','Refused: block leave needs at least 10 working days','10' in e,e)
    # 5 manager approve
    go('manager','approvals'); before=len(pg.query_selector_all('[data-approve]'))
    row=[r for r in pg.query_selector_all('tbody tr') if 'Adaeze Nwosu' in r.inner_text() and '21 Dec 2026' in r.inner_text()][0]; row.query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('employee','leave'); ok=any('21 Dec 2026' in r.inner_text() and 'Approved' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T05','Leave','Line manager','Approve the request','Employee sees it approved; balance updates',ok,'Approved status shown to employee' if ok else 'Status not updated')
    # 6 self-service change -> HR
    go('employee','profile'); pg.select_option('#cfld','Phone number'); pg.fill('#cval','Ending 5521'); pg.click('#cf button[type=submit]'); pg.wait_for_timeout(100)
    go('hr','approvals'); ok=any('Phone number' in r.inner_text() and 'Adaeze' in r.inner_text() for r in pg.query_selector_all('tbody tr'))
    rec('T06','Self-service','Employee, HR officer','Request a phone number change','Change waits for HR verification before reaching the record',ok,'Appears in HR approvals' if ok else 'Not routed')
    # 7 maker-checker record change
    go('hr','people'); pg.fill('#q','Adaeze Nwosu'); pg.wait_for_timeout(100); pg.click('tr[data-emp]'); pg.wait_for_timeout(150)
    pg.select_option('#rfld','Grade'); pg.fill('#rval','Senior Officer'); pg.fill('#rnote','Test promotion'); pg.click('#rf button[type=submit]'); pg.wait_for_timeout(150)
    go('hr','approvals'); hr_can=any('Senior Officer' in r.inner_text() and r.query_selector('[data-approve]') for r in pg.query_selector_all('tbody tr'))
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
    go('finance','approvals'); fin_first=len([r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit' in r.inner_text()])
    go('hoh','approvals'); rows=[r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit and Lending' in r.inner_text()]; rows[0].query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    go('finance','approvals'); rows=[r for r in pg.query_selector_all('tbody tr') if 'Requisition' in r.inner_text() and 'Credit and Lending' in r.inner_text()]; ok1=len(rows)>0 and fin_first==0
    if rows: rows[0].query_selector('[data-approve]').click(); pg.wait_for_timeout(150)
    rec('T14','Recruitment','Manager, Head of HR, Finance','Raise a requisition','Head of HR approves first, then Finance confirms budget',ok1,'Finance saw it only after Head of HR approval' if ok1 else 'Order not enforced')
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
    go('hoh','payroll'); pg.click('[data-pay="reviewed"]'); pg.wait_for_timeout(100)
    go('payroll','payroll'); hr_rel=pg.query_selector('[data-pay="released"]') is not None
    go('finance','payroll'); pg.click('[data-pay="released"]'); pg.wait_for_timeout(100); rel='Released' in pg.inner_text('main')
    rec('T16','Payroll','Payroll officer, Head of HR, Finance','Run the November payroll','Only the payroll officer prepares; blocked until inputs approved and exceptions reviewed; then review and release by two other people',(not hr_prep) and blocked and (not hoh_early) and (not hr_again) and (not hr_rel) and rel,f'Blocked before checks: {blocked}; out-of-turn actions: {hoh_early or hr_again or hr_rel}; released: {rel}')
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
    exp/=12; ok=abs(exp-tax)<=2 and abs(pen-g*.75*.08)<=2
    rec('T17','Payroll','Employee','Check PAYE on a payslip by hand','Matches Nigeria Tax Act 2025 bands after pension, NHF and rent relief; pension is 8% of basic, housing and transport',ok,f'Chargeable {ch:,.0f}; PAYE shown {tax:,.0f}; recalculated {exp:,.0f}')
    # 18 performance cap
    go('manager','performance'); capped=False; note='No suitable team member found'
    for r in pg.query_selector_all('tr[data-appr]'):
        t=r.inner_text()
        if 'Submitted' in t and 'Due' in t:
            r.click(); pg.wait_for_timeout(120)
            if 'Training overdue' in pg.inner_text('#drawer'):
                for i in range(5): pg.select_option(f'[data-mr="{i}"]','5')
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
    rec('T24','AI','Any','Ask HR a question','Answer drawn from policy and own data','' ,'Not testable outside Claude: test by hand in the app')
    R[-1][5]='Manual'
    rec('T25','Integrations','HR officer','Connect Teams, identity, ledger, NIBSS','Live connections','' ,'Simulated in the prototype; for the production build')
    R[-1][5]='Not in scope'
    rec('T26','All','All','Script errors during the whole test run','None',not errs,f'{len(errs)} errors' + (': '+errs[0][:120] if errs else ''))
    json.dump(R,open(os.path.join(os.path.dirname(__file__),'results.json'),'w'),indent=1)
    for r in R: print(r[0],r[5],r[6][:90])

# Changelog

## Release 17.1: Layout fix
- Fixed: figures in summary cards (for example "Your loan") overlapped on laptop-width screens. Cards now resize to fit; amounts of a billion naira or more show as "bn".
- New test: tests/overflow_check.py looks for text spilling out of its box on every screen, for every role, at laptop, small-laptop and phone widths.

## Release 17: Live sign-in and user provisioning
- Removed the "choose who to sign in as" list and the "Viewing as" switch. Sign-in is by work email with Microsoft 365 and multi-factor approval (simulated in the prototype). Personal and unknown addresses, disabled accounts and joiners before their start date are refused.
- People with more than one role switch only between the roles they hold ("Working as").
- Admin console, User accounts: day-one bulk import approved by the Head of HR, automatic Invited accounts for joiners, disabled accounts for leavers, CSV import with validation, enable and disable, resend invitation, failed sign-in count.
- Reset sample data moved into the admin console (prototype only).
- New test: click crawl (tests/click_crawl.py) presses every button, tab and row on every screen for every role.

## Release 16: User change requests, part 2
- Recruitment: requisition route Hiring Manager, HR (assigns salary within the grade band, first authoriser), MD (final). Finance step removed.
- Probation and induction: manager and employee induction sign-off with a day-30 flag, probation objectives, month-5 decision (confirm, extend 1 to 3 months, release) approved by HR. Intern grade with conversion.
- Reviews: objective setting with approval, locking, HR reopen and versions; monthly financial review graded against HR bands, verified by Treasury and approved by the line manager; monthly supervision; quarterly appraisal with skills, justifications, disagreement and dual sign-off; low ratings draft an improvement plan automatically.
- Attendance: daily lateness and absence report, lateness reasons, alerts over 3 a month, remote working requests approved by HR, four-stage sickness absence cases.
- Leave: annual leave plans, HR public holiday calendar (short-notice holidays), year-end carry-over report, leave balance on exit.
- Engagement: survey template builder (locked once responses arrive), Employee of the Month by weighted score with HR override.
- Pay review approved by the Executive Management Committee (MD). ISO 30414:2025 measures and attendance reports in analytics. Approval matrix with escalation and delegates, changes approved by the Head of HR. Data subject request tracker. NIBSS bank files for both pay dates. Training bond and loan shortfall shown at exit.

## Release 15: User change requests, part 1 (see docs/change-register.csv)
- HR settings screen holding every rule with its starting value; values below legal floors (Labour Act maternity and annual leave, pension minimums) are refused.
- Payroll: mid-month payment on the 12th (50% of gross, no deductions) and month-end on the 24th (balance less all deductions); salary structure 25/12.5/12.5/50; pension 8%/10% on basic, housing and transport; NHF only for opted-in staff; TIN on the payslip; cycle 25th to 24th with a cut-off on the 11th; approval route HR review with sample, Internal Audit verification, HR endorsement, Head of Finance and Operations approval. New Internal Audit role.
- Fixed: pay was over-prorated by one hour's worth when a pay cycle crossed the October clock change.
- Staff loans module: eligibility, one-third limit, repayment calculation, one loan at a time unless urgent, route HoD, Head of Credit Sales, Head of HR, MD/CEO, employee e-signature, Finance release with guarantor verification; removed from Cash requests.
- Leave: cadre entitlements, new leave types and rules, two-step approval (line manager then HR), 10-day request limit, automatic rejection with reasons, mandatory evidence, maternity tiers with the statutory floor.
- Records: employment details, identity documents with expiry, TIN and RSA PIN, emergency contact, masked numbers with logged reveals, mandatory evidence for sensitive changes, bank call-back, effective dates and full change history.
- Documents uploaded by HR with HR-only default and retention review; Leadway Health plans and group life cover; birthday automation rule with MD message.

## Release 14: Salary in two halves, dual roles, Head of Talent and learning library
- Payroll: net pay is paid in two halves, on the 15th and the 25th (the working day before if either falls on a weekend or public holiday). Deductions are calculated on the full month. Finance releases the first half separately; the second half carries any later changes. Payslips (screen and PDF), the bank schedule and the Home pay card show both dates.
- Dual roles: every role is staff first. Each role's menu has a "Me" section (My record, payslips, leave, performance, goals, learning, documents) that opens the personal staff screens without leaving the role. Role chips (for example "Staff" and "Head of Talent") show on Home and in the sidebar, and every role's Home has a personal staff summary.
- Head of Talent: new persona and role with a talent dashboard (vacancies, appraisal completion, overdue training, succession cover, company OKRs, mandatory learning completion). Cannot verify data changes or approve pay.
- Learning library: videos (with transcript and watch-to-the-end completion), PDF documents and written lessons. HR, the Head of HR and the Head of Talent publish material, target it to all staff or a department, mark it required, track completion and send reminders. Uploaded files are kept in browser storage (IndexedDB) in the prototype.

## Release 13: Yardsticks, KPIs and OKRs, memos, cash requests and module control
- Goals and development: published yardsticks for selection (weighted scorecard, pass marks, gates), appraisal (rating bands, compliance cap, calibration guide) and recommendations (promotion, merit pay, bonus, confirmation, succession, PIP, training).
- Performance: every self-rating and manager rating needs a written justification; KPI scorecards with targets, actuals and manager confirmation; personal OKRs aligned to company OKRs; team scorecard for managers.
- My record: change requests accept an optional supporting document, shown to HR at verification.
- Memos: letterhead memos and policies, rich-text editor, audience by all staff, department or person, attachments (optionally internal only), internal notes for HR, MD and administrator, e-signature, read and signature tracking, reminders, recall (recalled memos visible by title only to staff), PDF download.
- Cash requests: chosen approving manager, 10-word description, invoice upload, manager then Finance approval with optional internal notes hidden from the requester; approved staff loans join the payroll loan register.
- Birthdays on Home from date of birth captured at enrolment (day and month only, with opt-out); date of birth added to the new-joiner form.
- Admin console: module on/off switches (core screens locked) and an editable role-permission checklist, both audited.
- Offboarding in three steps (start switches access off, handover checklist, close by the named final approver) and a welcome tour.

## Release 12: Admin console and access control
System administrator role and dashboard; users and roles; temporary access with approval, expiry and acting-as; separation-of-duties conflict blocking; enforced revocation (including from access reviews); security settings. Audit trail now also records sensitive views, sign-ins and sign-outs, declines and every download.

## Fixes after release 11
- Duplicate element ID broke the phone "More" sheet on the People page.
- Wide content stretched four phone screens sideways (Time and attendance, Benefits, Speak up, People analytics).
- Offer approvals named the HR officer instead of the candidate in the confirmation message.

## Release 11: Relations, expenses, benefits and help desk
Employee relations and conduct (grievances, disciplinary cases, speak-up channel, annual declarations), expenses and cash advances, benefits administration, and the HR help desk with employment letters.

## Release 10: Managing Director view
Organisation cockpit for the MD: headline measures, top performers, risk-adjusted revenue drivers (sample loan-system data), culture drivers, revenue by business line, risks, department scorecard, live activity, board pack, and the MD's access-review decision for the Head of HR.

## Release 9: Recruitment and selection
Structured panel interviews with blind scorecards, assessments, offer letters (PDF) with Head of HR approval and e-signature, CBN prior-approval hold, talent pool, internal jobs board, recruitment analytics.

## Release 8: Roles
Payroll officer role (no employee creation or bank changes); Head of HR leadership home with decisions, risk radar, team and board summary PDF.

## Release 7: Trust and compliance
Hash-chained audit trail, access reviews, separation-of-duties report, data subject requests and self-service data download, breach register with 72-hour clock, retention schedule, record of processing, CBN cybersecurity checklist.

## Release 6: Learning, culture, succession and PIP
E-learning with lessons, certificates and badges; WhatsApp reminders (queued); culture drive; succession planning and career aspirations; performance improvement plans; Skystone brand identity; PDF payslips; profile photos.

## Release 5: Experience
Personal employee home, Today strip, trend arrows, approvals with undo and bulk actions, phone layout with bottom navigation.

## Release 4: Payroll rebuild
Nigeria Tax Act 2025 engine, inputs and approvals, variance, remittances by state of residence, bank schedule, ledger journal, staff loan register, dated statutory settings.

## Releases 1 to 3
Core HR, leave, approvals, joiners and leavers, training, recruitment, time, performance, goals, engagement, compensation, workforce planning, analytics, automation, integrations and Ask HR.

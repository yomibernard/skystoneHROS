# Skystone HR Operating System (People OS)

People OS is the HR operating system being designed for **Skystone Finance Company Limited**, Nigeria. It brings every part of working at Skystone into one place: the employee record, pay, leave, learning, performance, careers, recruitment and compliance.

> **Status: working prototype with sample data.** Every workflow, control and calculation works, but the app runs entirely in the browser and stores data only on the device. Do not enter real staff information. The production build must meet the security requirements in Annex A of the BRD before go-live.

## Signing in to the prototype
There is no list of people to choose from. Sign in with a work email, then press "I have approved it" (it stands in for Microsoft Authenticator). Sample accounts:

| Role | Work email |
|---|---|
| Employee | adaeze.nwosu@skystone-finance.com |
| Line manager | tunde.bakare@skystone-finance.com |
| HR officer | folake.adeyemi@skystone-finance.com |
| Head of HR | doyin.elegbe@skystone-finance.com |
| Payroll officer | oyin.elegbe@skystone-finance.com |
| Finance (CFO) | yusuf.shoetan@skystone-finance.com |
| Managing Director | ola.olabinjo@skystone-finance.com |
| System administrator | yetunde.abubakar@skystone-finance.com |
| Head of Talent | oluwatimilehin.ade-odunta@skystone-finance.com |
| Internal Audit | abdullahi.abubakar@skystone-finance.com |

Any of the other sample staff can sign in the same way (firstname.lastname@skystone-finance.com). The email domain is a placeholder until Skystone confirms its Microsoft 365 domain.

## Who registers users
1. Day one: the system administrator imports the HR master staff list; the Head of HR approves the import; accounts are matched to Microsoft 365 work emails.
2. Joiners: an accepted offer creates the employee record; the account is created as Invited and opens on the start date once the contract is signed and the guarantor verified.
3. Extra rights come only from the role catalogue: granted by the system administrator, approved by the Head of HR.
4. Leavers: disabled at close of business on the last working day.
Nobody can register themselves, and People OS never stores passwords.

## Try it

- **Online:** enable GitHub Pages for this repository (Settings → Pages → Source: GitHub Actions). The included workflow publishes `index.html`.
- **Locally:** download the repository and open `index.html` in Chrome, Edge, Safari or Firefox. No server or installation is needed.

Sign in with one of the work emails above. "Reset sample data" is in the admin console (User accounts tab).

## What it does

| Area | Highlights |
|---|---|
| Core HR | One employee record, effective-dated history, verification, maker-checker record changes, organisation chart |
| Recruitment | Requisitions from approved positions, structured panel interviews with blind scorecards, offer letters (PDF) with Head of HR approval and e-signature, CBN prior-approval hold, talent pool, internal jobs board, recruitment analytics |
| Joiners and leavers | Cross-department checklists; three-step offboarding (access off at start, handover, close by named approver); birthdays on Home from date of birth captured at enrolment; access blocked until checks pass; final pay held until exit clearance |
| Leave and time | Nigerian public holidays, block leave control, clock in and out, project timesheets |
| Payroll | Salary paid in two halves (15th and 25th), Nigeria Tax Act 2025 PAYE, pension, NHF, NSITF, ITF, staff loans, part-month pay, variance checks, state-of-residence PAYE, bank schedule, balanced ledger journal, PDF payslips, four-person approval chain |
| Performance | Balanced scorecard, self and manager ratings each with a written justification, KPI scorecards, OKRs aligned to company OKRs, published yardsticks for selection, appraisal and recommendations, conduct gate, feedback, improvement plans (PIP) |
| Memos | Letterhead memos and policies, rich text, audience targeting, internal-only attachments, internal notes, e-signature, read and signature tracking, recall |
| Cash requests | Chosen approving manager, 10-word description, invoice upload, manager then Finance approval with internal notes; staff loans flow into the payroll loan register |
| Talent | Development plans, skills, career aspirations and readiness, nine-box, succession plans, future leaders pool |
| Learning | Learning library of videos, PDFs and written lessons with completion tracking, e-learning lessons, knowledge checks, PDF certificates, badges, WhatsApp reminders (queued), training budget |
| Engagement and culture | Pulse surveys, eNPS, recognition, culture drives, values, stories |
| Compensation and planning | Salary bands, pay review modelling, pay equity, workforce scenarios including bank conversion |
| Analytics | Turnover, headcount, exit reasons, length of service, board summary PDF |
| Employee relations | Grievances and disciplinary cases with a fair-process checklist, MD approval of dismissals and appeals, anonymous speak-up channel to Compliance and Internal Audit, annual conflict and gifts declarations |
| Expenses and advances | Claims with receipts, per diem caps by grade, duplicate and weekend checks, manager then Finance approval, cash advances with retirement and payroll recovery |
| Benefits | Health insurance plan and hospital, dependants with verification, group life cover and beneficiaries, voluntary pension contributions, insurer schedules |
| HR help desk | Cases with response targets, owners, threads, satisfaction ratings, and employment confirmation letters (PDF) |
| Dual roles | Everyone is staff first: a personal "Me" section and staff summary inside every role, role chips, and a Head of Talent role |
| Admin console and access control | Module on/off switches, editable role-permission checklist, role catalogue and permission matrix, multiple roles per user, temporary elevated access with second-person approval and automatic expiry, acting in a granted role, conflict blocking (MD approval required), immediate revocation enforced on screen, security settings |
| Trust and compliance | Hash-chained tamper-evident audit trail, access reviews, separation-of-duties report, data subject requests, 72-hour breach register, retention schedule, record of processing, CBN cybersecurity checklist |

## Deployment
Pushing to `staging` publishes to the staging site; pushing to `main` publishes to production (HostGator, via `.github/workflows/deploy.yml`). Test on staging first. `server.js` is an optional Node backend (SQLite) and is not yet wired to `index.html`; it is excluded from the FTP upload.

## Repository layout

```
index.html                 The complete prototype (single file, no dependencies)
docs/ARCHITECTURE.md       How the prototype is built and how production should differ
docs/REQUIREMENTS.md       Where the requirements live and how to export them
docs/test-log.csv          Latest acceptance test results
tests/acceptance_test.py   Automated acceptance tests (Playwright)
.github/workflows/pages.yml  Publishes the prototype to GitHub Pages
SECURITY.md  CHANGELOG.md  LICENSE
```

## Running the tests

```bash
pip install playwright
python -m playwright install chromium
python tests/acceptance_test.py
```

The suite signs in as each role and checks the key controls: maker-checker, payroll segregation, PAYE accuracy, the CBN offer hold, exit clearance, block leave and more. Results are written to `tests/results.json`.

## Features that need Claude or a backend

- **Ask HR (AI assistant)** works only when the page is opened inside Claude. In production it must call an approved AI service through Skystone's backend, never directly from the browser.
- **WhatsApp reminders** are queued, not sent. Production uses the WhatsApp Business Platform with Meta-approved templates and recorded opt-in.
- **Integrations** (Microsoft 365, identity, ledger, NIBSS, PFAs, state tax portals) are designed but simulated.

## Ownership

Proprietary to Skystone Finance Company Limited. See `LICENSE`. Skystone names, logos and icons are trademarks of Skystone and may not be reused.

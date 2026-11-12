# Skystone HR Operating System (People OS)

People OS is the HR operating system being designed for **Skystone Finance Company Limited**, Nigeria. It brings every part of working at Skystone into one place: the employee record, pay, leave, learning, performance, careers, recruitment and compliance.

> **Status: working prototype with sample data.** Every workflow, control and calculation works, but the app runs entirely in the browser and stores data only on the device. Do not enter real staff information. The production build must meet the security requirements in Annex A of the BRD before go-live.

## Try it

- **Online:** enable GitHub Pages for this repository (Settings → Pages → Source: GitHub Actions). The included workflow publishes `index.html`.
- **Locally:** download the repository and open `index.html` in Chrome, Edge, Safari or Firefox. No server or installation is needed.

On the sign-in screen, choose who to sign in as:

| Person | Role | What they see |
|---|---|---|
| Adaeze Nwosu | Employee | Personal home, payslips, leave, learning, career, culture |
| Tunde Bakare | Line manager | Team approvals, appraisals, recruitment for the team |
| Oluwatimilehin Ade-odunta | Talent manager (HR officer) | Records, onboarding and exits, verification, recruitment |
| Oyin Elegbe | Payroll officer | Payroll inputs and runs only |
| Doyin Elegbe | Head of HR | Leadership view, approvals, board summary |
| Yusuf Shoetan | Finance (CFO) | Payroll release, pay review, workforce cost |
| Ola Olabinjo | Managing Director | Organisation cockpit: top performers, revenue drivers, culture drivers, department scorecards, risks, live activity, board pack |

"Reset sample data" in the sidebar restores the starting position.

## What it does

| Area | Highlights |
|---|---|
| Core HR | One employee record, effective-dated history, verification, maker-checker record changes, organisation chart |
| Recruitment | Requisitions from approved positions, structured panel interviews with blind scorecards, offer letters (PDF) with Head of HR approval and e-signature, CBN prior-approval hold, talent pool, internal jobs board, recruitment analytics |
| Joiners and leavers | Cross-department checklists; access blocked until checks pass; final pay held until exit clearance |
| Leave and time | Nigerian public holidays, block leave control, clock in and out, project timesheets |
| Payroll | Nigeria Tax Act 2025 PAYE, pension, NHF, NSITF, ITF, staff loans, part-month pay, variance checks, state-of-residence PAYE, bank schedule, balanced ledger journal, PDF payslips, four-person approval chain |
| Performance | Balanced scorecard, self and manager ratings, conduct gate, feedback, improvement plans (PIP) |
| Talent | Development plans, skills, career aspirations and readiness, nine-box, succession plans, future leaders pool |
| Learning | E-learning lessons, knowledge checks, PDF certificates, badges, WhatsApp reminders (queued), training budget |
| Engagement and culture | Pulse surveys, eNPS, recognition, culture drives, values, stories |
| Compensation and planning | Salary bands, pay review modelling, pay equity, workforce scenarios including bank conversion |
| Analytics | Turnover, headcount, exit reasons, length of service, board summary PDF |
| Employee relations | Grievances and disciplinary cases with a fair-process checklist, MD approval of dismissals and appeals, anonymous speak-up channel to Compliance and Internal Audit, annual conflict and gifts declarations |
| Expenses and advances | Claims with receipts, per diem caps by grade, duplicate and weekend checks, manager then Finance approval, cash advances with retirement and payroll recovery |
| Benefits | Health insurance plan and hospital, dependants with verification, group life cover and beneficiaries, voluntary pension contributions, insurer schedules |
| HR help desk | Cases with response targets, owners, threads, satisfaction ratings, and employment confirmation letters (PDF) |
| Trust and compliance | Hash-chained tamper-evident audit trail, access reviews, separation-of-duties report, data subject requests, 72-hour breach register, retention schedule, record of processing, CBN cybersecurity checklist |

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

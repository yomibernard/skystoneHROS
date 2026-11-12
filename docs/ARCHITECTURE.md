# Architecture

## Prototype

- **One file.** `index.html` holds the HTML, CSS and JavaScript, with the Skystone logo, icons and photographs embedded as data URIs. It has no external dependencies apart from Google Fonts, and falls back to system fonts offline.
- **State.** All data lives in a single object saved to the browser's `localStorage` under the key `skystone-people-os-v1`. Sample employees are generated deterministically from a seed, so every device starts from the same data.
- **Roles.** Six personas (employee, line manager, HR officer, payroll officer, Head of HR, Finance) drive the menus and the permitted actions. **Permissions are enforced only in the browser** in the prototype.
- **Approvals.** Every request (leave, data change, record change, training, requisition, offer, payroll setting, relief claim, improvement plan) is an item in one requests list with a `kind`, a stage and the decision maker, which makes separation of duties testable.
- **Payroll engine.** `calc(employee, period)` applies the dated statutory settings in force for the period: Nigeria Tax Act 2025 bands, pension, NHF, NSITF, ITF, minimum-wage exemption, rent relief, part-month proration, inputs, staff loans and the deduction cap.
- **Audit trail.** Every recorded event is appended with a SHA-256 hash of itself and the previous entry. `auditVerify` recomputes the chain and reports the first broken entry.
- **PDFs.** Payslips, certificates, offer letters and the board summary are generated in the browser by a small built-in PDF writer (standard Helvetica fonts, embedded JPEG logo).

## Production (target)

| Concern | Prototype | Production |
|---|---|---|
| Data store | Browser storage | Server database, encrypted, backed up, in an approved location |
| Identity | Persona picker | Single sign-on with multi-factor authentication |
| Permissions | Browser only | Enforced on the server for every request |
| Audit trail | Hash chain in the browser | Append-only server log, hash chain anchored externally |
| AI | Claude in-page | Approved AI service behind Skystone's backend, no personal data sent without a lawful basis |
| Integrations | Simulated | APIs to identity, ledger, banks, PFAs, state tax portals, WhatsApp Business Platform |

The full list of security controls is SEC-01 to SEC-25 in Annex A of the BRD.

# VulnBank

A small invoice portal for freelancers and small teams. Log in, check your
balance, search the team directory, view invoices and download receipts.
Admins get a user list and a connectivity checker.

## Run

```bash
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Demo accounts: `alice/alice123`, `bob/bob123`, `admin/admin123`.

## Test

```bash
python -m pytest -q
```

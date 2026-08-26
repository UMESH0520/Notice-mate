# Sample synthetic notices

These are the same three synthetic notices that power the in-app **"Try a
sample notice"** option, exported as plain text files. They are generated from
`backend/app/demo_data.py` — the single source of truth — so the two never
drift apart.

Use them to exercise the **file upload** path end to end:

1. Start NoticeMate and open the app.
2. Go to **Add your notice → Upload a file**.
3. Pick one of the `.txt` files in this folder.

Because an uploaded file is not recognised as a curated demo, it is analysed by
the generic path (OpenAI when a key is configured, otherwise the deterministic
offline fallback) — which is exactly what you want when demonstrating that the
product works on notices it has never seen.

| File | Notice type |
| --- | --- |
| `tax-143-1.txt` | Income-tax intimation (synthetic) |
| `epf-kyc.txt` | Provident-fund KYC update (synthetic) |
| `muni-address.txt` | Municipal address verification (synthetic) |

> **Every one of these notices is fictional.** The departments, officers,
> reference numbers, amounts and portal names do not exist. Nothing here is
> copied from, or usable with, any real government system.

Regenerate them after editing `demo_data.py`:

```bash
python -m app.export_demo_notices
```

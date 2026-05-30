# sec-edgar

**Category:** finance · **Runtime:** uvx · **Package:** `sec-edgar-mcp`

Access US SEC EDGAR filings and financial statements.

## Required identifier (not a typical secret)

- **Value:** `SEC_EDGAR_USER_AGENT`
- **Format:** `"Your Name you@example.com"` (a real contact string).
- **Where it's documented:** https://www.sec.gov/os/webmaster-faq#developers

> ⚠️ The SEC requires a descriptive User-Agent on every request. **Whatever you put here is
> sent with each request to the SEC and is therefore semi-public.** Use a contact you are
> comfortable sharing. Use a placeholder like `Jane Doe jane@example.com` only for local
> testing. This value is stored only in your local client config, never in this repository.

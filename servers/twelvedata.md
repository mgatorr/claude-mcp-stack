# twelvedata

**Category:** finance · **Runtime:** uvx · **Package:** `mcp-server-twelve-data`

Real-time and historical market data — US stocks, forex, and crypto — via the
[Twelve Data](https://twelvedata.com) API.

## API key (required)

- **Secret:** `TWELVEDATA_API_KEY`
- **Where to get it:** https://twelvedata.com/account/api-keys
- The free tier covers US stocks, forex, and crypto. European exchanges (XETRA, Euronext,
  LSE) require a paid plan — use the `yahoo-finance` server for free European data instead.

## Notes

- The args use `-n 5` to cap the number of tools exposed. The Claude Desktop/Cowork
  connector bridge limits the `tools/list` payload size; a higher `-n` can make the server
  register **zero** tools in Cowork. Increase it cautiously and restart the app to test.
- Your key is written only to your local client config, never to this repository.

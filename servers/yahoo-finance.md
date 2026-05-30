# yahoo-finance

**Category:** finance · **Runtime:** local (maintained fork) · **No API key required**

Free worldwide market data via Yahoo Finance, including European exchanges:
`.DE` (XETRA), `.PA` (Paris), `.MC` (Madrid/IBEX), `.MI` (Milan), `.AS` (Amsterdam),
`.L` (London).

## Maintained fork

This uses a fork of [`mcp-yahoo-finance`](https://github.com/maxscheijen/mcp-yahoo-finance)
(MIT, © Max Scheijen) with a robustness fix: `get_current_stock_price` previously crashed
with `Unknown format code 'f' for object of type 'str'` on illiquid symbols (e.g. `OD7C.DE`)
whose `.info` exposes no numeric last price. The fork coerces the value, falls back to the
last available close, and otherwise returns a clear `No price data available for <symbol>`
instead of crashing. The upstream MIT license and attribution are preserved.

## Install (done by the agent)

The catalog pins the fork to a tag. The agent clones it, then runs `uv venv` and
`uv pip install -e .`, and points the server `command` at the produced binary
(`.venv/bin/mcp-yahoo-finance`; Windows: `.venv\Scripts\mcp-yahoo-finance.exe`).

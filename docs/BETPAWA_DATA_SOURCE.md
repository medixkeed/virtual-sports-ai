# BetPawa Uganda data source investigation

Investigation date: 2026-09-23

## Source URL

`https://www.betpawa.ug/virtual-sports`

## What was verified

- The page is publicly reachable without logging in.
- The rendered page displays a virtual-sports matchday, live/upcoming/results tabs, league names, fixtures, match links, and 1X2 odds.
- Observed public first-party requests from the page:
  - `GET /api/sportsbook/virtual/v2/seasons/list/actual`
  - `GET /api/sportsbook/virtual/v3/events/list/by-round/{round_id}`
- The browser sends `x-pawa-brand: betpawa-uganda`, `x-pawa-language: en`, and `devicetype: web` to those requests.
- The observed match links contain stable external match identifiers, for example `/virtual-sports/match/38256348`.
- The rendered page exposes market tabs for 1X2, O/U, BTTS, DC, and HT/FT.

## Response format

The browser normally requests the event and season routes as `application/x-protobuf`, but the same first-party routes return JSON when requested with `Accept: application/json` and the observed public brand headers. A request without the observed brand header returns JSON such as:

```json
{"error":"BRAND_HEADER_IS_MISSING","params":null,"payload":null,"uuid":"..."}
```

The application uses the verified JSON representation and does not decode the undocumented protobuf representation.

## Available fields

Verified in the rendered page:

- Matchday label
- League names and league identifiers in public links
- Match external identifiers in public links
- Home and away team abbreviations
- 1X2 odds
- Market labels for O/U, BTTS, DC, and HT/FT
- Live/upcoming/results navigation

Verified in the JSON response:

- Stable event identifiers
- Scheduled timestamps
- Match status and completed scores
- Season and round identifiers
- 1X2 prices and labels
- Over/Under prices across multiple goal lines
- BTTS prices
- Double Chance prices
- HT/FT prices

## Authentication and restrictions

The page itself is public and did not require account authentication during this investigation. The observed data requests require the site brand header and return an error when it is omitted. No CAPTCHA, login bypass, private endpoint, or wager-placement flow was used.

## Refresh limitations

The BetPawa provider is selectable with `DATA_PROVIDER=betpawa` and successfully refreshes verified live fixtures and odds through JSON. Refresh failures do not delete, empty, or overwrite the last successful dataset.

The provider uses a 10-second timeout and the existing five-minute scheduler interval. Scheduler jobs are non-overlapping and failed refreshes are logged.

## Conclusion

Live BetPawa ingestion is **verified** through the public JSON representation: fixtures, stable IDs, teams, leagues, kickoff times, statuses, results, and all five requested market families were fetched and persisted during validation. Odds snapshots are stored with timestamps and the application does not generate simulated odds.

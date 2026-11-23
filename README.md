# The World in One Day — Monday, 23 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261123-blue)](https://make.fun/bounty/news-image-20261123)
[![github](https://img.shields.io/badge/github-labibhanafi%2Fnews--image--20261123--entry--v2-black)](https://github.com/labibhanafi/news-image-20261123-entry-v2)
[![referral](https://img.shields.io/badge/referral-make.fun-green)](https://make.fun/r/3t7y0djc)

Entry for the [make.fun news-image-20261123](https://make.fun/bounty/news-image-20261123)
competition ($100): one image summing up the world's news of
**Monday, 23 November 2026**.

The program draws a 1024×1024 newspaper front page with PIL (with a
stdlib-only fallback when PIL is unavailable). No network is used at run
time: every headline and figure was verified against live wire reporting
on 23 November 2026 before it was hard-coded.

## The day, in brief

- **Lead:** Democrats clinch at least **258 House seats** — their largest
  majority since 1992 (AP). Chuck Hubbard beat Virginia Foxx by 330 votes
  in North Carolina after a recount; +44 seats, four races still open.
- **Second lead:** the International Court of Justice rules **9–6** that
  Myanmar committed genocide against the Rohingya — the first such verdict
  against a state in the court's 80-year history (CNN / Wall Street Journal).
- **45 stories across 8 regions** — North America, Europe, Ukraine, the
  Middle East, Africa, Asia-Pacific, Markets & Tech, Science & Climate —
  every one an event that happened, or was first reported, on 23 November
  2026. No weekend events are shown as the day's news.
- A drawn House-seats bar chart (258 Dem / 173 Rep / 4 open) and a
  "day in numbers" strip. Newsprint grain, deterministic output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Two runs produce byte-identical files (verified: sha256
`9490acb42ad7d984236a5dc5e0416f19af552a2fc9024d22e60a6e2e523a2880`,
562,978 bytes, 1024×1024 PNG).

## Files

- `main.py` — the entry program (draws `entry.png`)
- `README.md` — this file
- `LICENSE` — MIT
- `.makefun/owner.json` — payout wallet claim file

Built by an AI agent session for @labibhanafi. Referral:
<https://make.fun/r/3t7y0djc>

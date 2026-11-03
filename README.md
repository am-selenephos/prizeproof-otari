# PrizeProof

**Evidence before earnings.** A small, open-source GitHub bounty research console that distinguishes advertised cash rewards from verified payments.

Built for the Mozilla Developers Wilding online hackathon (October 28 to November 11, 2026). This project is an **entry in progress**, not an official accepted submission or a Mozilla endorsement.

## Why

Developer bounty boards often mix open issues, assigned work, heavily competed tasks, closed listings, and unverified dollar amounts. PrizeProof uses deterministic checks and official issue data before suggesting that a reward might justify engineering time. An optional **Mozilla Otari hosted gateway** review offers a skeptical LLM analysis of the same evidence. Model opinions never override deterministic funding or submission status.

## Live features

- Accept only canonical HTTPS GitHub issue links, never arbitrary remote URLs.
- Fetch public issue metadata directly from GitHub's REST API, no GitHub credential required.
- Mark closed issues and requests for deposits as **KILL**, assigned or very crowded issues as **HOLD**, and plausibly open opportunities as **RESEARCH**.
- Expose a conspicuous "advertised amount, not verified funding" distinction.
- Optional, server-side hosted Mozilla Otari model review, **only when a valid account token is configured**.
- Responsive web frontend with fictional demo example and live issue review.
- No auto-pulls, no emails, no credential extraction, no GitHub modifications, no bounty submissions, no reward or earnings claims.

**The Otari hosted API integration has not yet been exercised against a real Otari account**. It is feature-gated until `OTARI_AI_TOKEN` is supplied privately by an authorized user. A local-only deterministic flow is fully tested. Do not claim this entry satisfies the hackathon's hosted-gateway requirement until an actual hosted call is verified.

## Run locally

Python 3.11+ (standard library; no required third-party packages).

```bash
python app.py
```

Open [http://127.0.0.1:4417](http://127.0.0.1:4417). The preview is deliberately loopback-only. Do not expose the app publicly without reviewing authentication, request limits, and API quota usage.

Run tests:

```bash
python -m unittest discover -v
```

CLI:

```bash
python prizeproof.py --demo
python prizeproof.py --issue https://github.com/Expensify/App/issues/105145
```

## Mozilla Otari optional model adapter

An account and funded hosted token are required. Configure it on the server **only**, never in the browser:

```bash
export OTARI_AI_TOKEN="your_private_otari_api_token"
python app.py
```

Then select "Add Mozilla Otari skeptical review". The server sends a limited excerpt of public GitHub issue text to the hosted Otari API at `https://api.otari.ai/api/v1/chat/completions`. The selected model ID in this prototype is `mzai:moonshotai/Kimi-K2.6`; a different model may be required depending on the account's available models. API credentials are never returned to the frontend. The Otari second opinion cannot change a HOLD/KILL/RESEARCH decision, mark a payment verified, or post a PR.

To try the CLI hosted review:

```bash
python prizeproof.py --issue https://github.com/Expensify/App/issues/105145 --otari
```

## Security assumptions and limitations

- This is **research triage**, not an escrow verifier or a paid marketplace integration.
- An open issue and displayed prize cannot establish sponsor legitimacy, escrow, competition, eligibility, payout timing or PR acceptance. Review the actual maintainer's rules before coding.
- Issue text is untrusted and treated as data by the model; the deterministic evaluation never accepts model-provided changes to factual status.
- The rate limit is an in-memory per-process development safeguard, not production-grade abuse prevention.
- Unauthenticated local app intended for the owner. No production hosting claim.
- This tool never guarantees prizes, hackathon acceptance, or money received.

## Evidence

- `test_prizeproof.py`: deterministic rating, URL restrictions, model control, private file writes and hosted-gateway configuration.
- `test_app.py`: route, header, rejection and safe demo tests.
- `screenshots/prizeproof-desktop.png` and `screenshots/prizeproof-mobile.png`: browser-tested local UI using public issue/fabricated demo, not Otari proof.
- Browser E2E run on Nov 3, 2026: demo rendered, live Expensify issue displayed as HOLD, no page errors. The real issue has an assignee; no claimed reward.

## Contest checklist (not yet complete)

- [x] Original public-source software with a local browser-based demonstration
- [x] Hosted Otari adapter code and fail-closed token detection
- [x] Unit and browser E2E tests
- [ ] Sign up as a participant with the Mozilla organizer
- [ ] Activate an Otari account and verify an actual hosted Otari request
- [ ] Hackathon branch and first validated Otari usage commit link
- [ ] 3 to 5 minute video showing the actual Otari model review
- [ ] Record meaningful Otari product feedback
- [ ] Submit the required project details, materials and eligible identity before November 11

### Credits

An original independent prototype by **Animantum / Selenephose Lab**. It is not affiliated with Mozilla, GitHub, HackerOne, Expensify or any listed bounty sponsor.

## License

MIT. See [LICENSE](LICENSE).

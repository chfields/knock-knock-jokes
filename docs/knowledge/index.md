---
okf_version: 0.2
---

# Pitfalls

* [Built-in jokes are seeded into PostgreSQL only once](builtin-jokes-seed-once.md) - editing JOKES doesn't reach a deployed database; re-seeding resurrects deletions
* [Catalogue order differs by store](catalogue-order-differs-by-store.md) - memory preserves insertion order while PostgreSQL sorts by name
* [Trusted proxy count controls the fallback voter identity](trusted-proxy-count-controls-voter-ip.md) - proxy-hop configuration determines whether IP-hash voting uses a client or forwarded address

# Risks

* [Every web response provisions a persistent voter cookie](all-web-responses-provision-voter-cookie.md) - passive browsing receives a signed one-year voter identifier
* [Catalogue mutations have no authorization boundary](catalogue-mutations-are-unauthenticated.md) - API callers can add or delete jokes without an access check
* [A first direct vote switches from IP to cookie identity](first-vote-switches-from-ip-to-cookie-identity.md) - a direct initial rating can bypass the later cookie's duplicate-vote check

# Invariants

* [Shared store behavior lands in both backends](store-parity.md) - memory/JSONL and PostgreSQL implementations stay in step, tested both ways
* [Per-voter data uses verified cookie IDs or IP hashes](voter-identity.md) - stores get a verified ID or address hash, never a signed cookie string or raw address

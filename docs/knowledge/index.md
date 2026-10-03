---
okf_version: 0.2
---

# Pitfalls

* [Built-in jokes are seeded into PostgreSQL only once](builtin-jokes-seed-once.md) - editing JOKES doesn't reach a deployed database; re-seeding resurrects deletions
* [Catalogue order differs by store](catalogue-order-differs-by-store.md) - memory keeps JOKES order, PostgreSQL sorts by name

# Invariants

* [Every store change lands in both backends](store-parity.md) - memory/JSONL and PostgreSQL implementations stay in step, tested both ways
* [Per-voter data is keyed by _voter_key()](voter-identity.md) - never store or return raw IPs or cookie values

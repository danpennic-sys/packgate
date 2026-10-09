# PackGate

Local EvidencePack desk for Operator Pages. One HTML file plus a Python CLI. Emits and checks packs using the same hash recipe as [evidence-core](https://github.com/danpennic-sys/evidence-core). Pay once. Buyer owns the file.

This is a hash chain. It is not a QuantumGuard signature. QuantumGuard v1 is Ed25519, offline, PASS / FAIL / INDETERMINATE. PackGate does not claim that.

## What the buyer gets

- `index.html` — phone-browser desk. Build a pack, chain the previous hash, download JSON, verify a file.
- `packgate.py` — same hash, no network. `emit` and `verify`.
- Sell page, price sheet, and the outreach script in this repo.

## Hash recipe

SHA-256 over the raw UTF-8 concatenation of:

1. `created_at_utc`
2. `service`
3. `service_version`
4. `gateway_version`
5. compact JSON of `request`
6. compact JSON of `response`
7. `prev_hash`

`pack_id` equals `current_hash`. Signature stays `signature_placeholder` until a real key signs the bytes. Do not tell a buyer the placeholder is a proof.

## Run

Open `index.html` in a browser. Nothing is uploaded.

```bash
python3 packgate.py emit --service fieldclose --prev GENESIS --out job.pack.json
python3 packgate.py verify job.pack.json
```

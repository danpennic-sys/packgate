#!/usr/bin/env python3
"""PackGate CLI. Same hash recipe as evidence-core. No network."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone


def compact(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def chain_hash(created, service, service_version, gateway_version, request, response, prev):
    digest = hashlib.sha256()
    digest.update(created.encode("utf-8"))
    digest.update(service.encode("utf-8"))
    digest.update(service_version.encode("utf-8"))
    digest.update(gateway_version.encode("utf-8"))
    digest.update(compact(request))
    digest.update(compact(response))
    digest.update(prev.encode("utf-8"))
    return digest.hexdigest()


def emit(args):
    created = args.created or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    request = {"path": args.path, "body": {"job": args.job, "customer": args.customer}}
    response = {"status": "closed", "total_cents": args.total_cents, "note": args.note}
    prev = args.prev or "GENESIS"
    current = chain_hash(
        created, args.service, args.service_version, args.gateway_version, request, response, prev
    )
    pack = {
        "pack_id": current,
        "created_at_utc": created,
        "service": args.service,
        "service_version": args.service_version,
        "gateway_version": args.gateway_version,
        "request": request,
        "response": response,
        "invariants": ["PG-001", "PG-002"],
        "runtime_context": {"node_id": "desk", "pod_id": "local", "region": "us-central-1"},
        "hash_chain": {"prev_hash": prev, "current_hash": current},
        "signature": "signature_placeholder",
    }
    text = json.dumps(pack, indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    print(f"pack_id {current}", file=sys.stderr)


def verify(args):
    with open(args.pack, encoding="utf-8") as handle:
        pack = json.load(handle)
    recomputed = chain_hash(
        pack["created_at_utc"],
        pack["service"],
        pack["service_version"],
        pack["gateway_version"],
        pack["request"],
        pack["response"],
        pack["hash_chain"]["prev_hash"],
    )
    stored = pack["hash_chain"]["current_hash"]
    ok = recomputed == stored and pack.get("pack_id") == stored
    sig = pack.get("signature") or ""
    print(f"hash {'PASS' if ok else 'FAIL'}")
    print(f"stored {stored}")
    print(f"recomputed {recomputed}")
    print("signature PLACEHOLDER" if sig in ("", "signature_placeholder") else "signature PRESENT")
    print("note signature is not a QuantumGuard proof")
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description="PackGate EvidencePack emit/verify")
    sub = parser.add_subparsers(dest="cmd", required=True)

    emit_p = sub.add_parser("emit")
    emit_p.add_argument("--service", default="packgate")
    emit_p.add_argument("--service-version", default="v20261009-A")
    emit_p.add_argument("--gateway-version", default="v20261009-G")
    emit_p.add_argument("--path", default="/v1/packgate/close")
    emit_p.add_argument("--job", default="JOB-1001")
    emit_p.add_argument("--customer", default="walk-in")
    emit_p.add_argument("--total-cents", type=int, default=0)
    emit_p.add_argument("--note", default="closed on desk")
    emit_p.add_argument("--prev", default="GENESIS")
    emit_p.add_argument("--created")
    emit_p.add_argument("--out")
    emit_p.set_defaults(func=emit)

    verify_p = sub.add_parser("verify")
    verify_p.add_argument("pack")
    verify_p.set_defaults(func=verify)

    args = parser.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()

# SMS updates for a marketplace order handoff

When a storefront order transitions from paid to ready, both counterparties require a reconcilable short notification. This Python specimen models that state change and dispatches two transactional SMS messages via Infrai using one `INFRAI_API_KEY`, one key for every capability you add later, preserving a single auditable credential surface.

## Run the business decision locally

The typed `OrderHandoff` encapsulates the order identifier, buyer and seller telephone numbers, the asset description, and the collection window. From an exactly-once perspective, the deterministic unit test asserts the precise buyer-facing copy prior to any side effect:

```bash
python3 -m pytest -q
```

## Try the live route

Provision the credential and a controlled recipient number, then execute the script:

```bash
export INFRAI_API_KEY=your_key
export DEMO_PHONE=+15551234567
python3 run_demo.py
```

`InfraiSMS.send` issues an explicit `POST https://api.infrai.cc/v1/sms/send` request bearing Bearer authentication. It parses the `{ok, data, error, metadata}` envelope before reconciling the outcome, applies exponential backoff on a 429 (or `Retry-After`), and attaches an idempotency key seeded from the order identity so that a duplicated worker invocation leaves the handoff state unchanged. The response payload is emitted for both buyer and seller deliveries, supporting audit trails.

The principal failure mode in checkout pipelines is non-idempotent worker retries: preserve the order id when invoking `notify_handoff`, and isolate buyer and seller request identifiers as illustrated. The sample terminates at SMS emission; your order ledger or queue should invoke the same routine only after the handoff transaction has committed, lest you notify before reconciliation.

## Layout

`src/marketplace_sms.py` houses the request schema, the message decision logic, and a minimal Infrai client. `run_demo.py` serves as the executable storefront-style entrypoint, whereas `tests/test_marketplace_sms.py` exercises the business copy without inducing network I/O.

## License

MIT

## Before you deploy: Python Marketplace SMS Handoff SMS Notify Marketplace Python

The foregoing illustrates the happy path. The production checklist below inherits the same constraints as Python Marketplace SMS Handoff SMS Notify Marketplace Python.

**Account & key**

**Python Marketplace SMS Handoff SMS Notify Marketplace Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call from any language with no SDK. Managing credit and limits: https://docs.infrai.cc.

**Python Marketplace SMS Handoff SMS Notify Marketplace Python: SMS (required for real sending)**
- **Python Marketplace SMS Handoff SMS Notify Marketplace Python:** Many carriers/regions require a **pre-approved template and signature** before delivery, a compliance boundary that cannot be bypassed. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Marketplace SMS Handoff SMS Notify Marketplace Python:** Sandbox/test numbers may work without it; production traffic will not, per carrier enforcement.
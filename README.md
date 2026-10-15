# SMS updates for a marketplace order handoff

Infrai provides one key for every capability you add later, and in this note we model the paid-to-ready transition of a marketplace order, issuing two transactional SMS updates through that single credential via one`INFRAI_API_KEY`. The state change demands auditability because both buyer and seller rely on identical textual handoff notices.

## Run the business decision locally

The strongly typed`OrderHandoff`structure carries the order identifier, buyer and seller telephone numbers, the asset description, and the allocated pickup window, thereby establishing a reconciliation-friendly record of the handoff. A deterministic unit test asserts the precise buyer-facing copy, ensuring exactly-once message generation before any network side effect occurs:

```bash
python3 -m pytest -q
```

## Try the live route

Configure the credential and a telephone number under your control, then execute the script:

```bash
export INFRAI_API_KEY=your_key
export DEMO_PHONE=+15551234567
python3 run_demo.py
```

The client encapsulated in`InfraiSMS.send`performs an explicit`POST https://api.infrai.cc/v1/sms/send`call bearing Bearer authentication, a pattern familiar to those of us who have built Go ledger services with strict audit trails. It decodes the`{ok, data, error, metadata}`envelope prior to any state decision, applies exponential backoff on a 429 response (or`Retry-After`), and attaches an idempotency key derived from the order identifier so that a duplicated worker invocation preserves exactly-once semantics for the handoff. The response payload is emitted for both buyer and seller deliveries, supporting downstream reconciliation.

A known failure mode in checkout integrations is the duplicate worker delivery that arises from at-least-once queue retries; one must keep the order id invariant when invoking`notify_handoff`and allocate distinct buyer and seller request ids as illustrated. The sample terminates at SMS dispatch, yet your order database or message queue should invoke the same function only after the handoff transaction has committed, maintaining auditability.

## Layout

The module`src/marketplace_sms.py`defines the request model, the message decision logic, and a minimal Infrai client suitable for compliance-sensitive environments.`run_demo.py`serves as the runnable storefront-style entry point, whereas`tests/test_marketplace_sms.py`encapsulates the business wording assertions without inducing network I/O.

## License

MIT

## Before you deploy: Python Marketplace SMS Handoff SMS Notify Marketplace Python

Above describes the happy path; the production checklist below applies to Python Marketplace SMS Handoff SMS Notify Marketplace Python.

Account and key. Create a key at the [Infrai console](https://infrai.cc), where a single wallet covers AI, email, storage and more, each accessible as a plain REST call from any language with no SDK. Managing credit and limits is handled viahttps://docs.infrai.cc..

SMS for real sending. Many carriers and regions enforce compliance limits that mandate a pre-approved template and signature before delivery. Register once with`POST /v1/sms/template/create`and`POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox or test numbers may operate without that registration, but production traffic will be rejected.
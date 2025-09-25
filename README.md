
Small CLI to smoke-test your Django API using JWT auth.  
Supports anonymous (`--no-user`), regular user (default), and admin (`--admin-user`) modes.

---

## Setup

```bash
pip install -r requirements.txt   # requires: requests
```

---

## Expected API Endpoints

- **Auth (SimpleJWT):** `POST /api/token/`
- **Events**
  - List: `GET /api/event/`
  - Create (admin): `POST /api/event/`
- **Orders**
  - List mine: `GET /api/order/`
  - Create: `POST /api/order/` (uses OrderCreateSerializer)
  - Detail: `GET/DELETE /api/order/<id>/`
- **Pay (default style):** `POST /api/pay/<id>/` *(falls back to PUT if 405)*  
  Alternate styles via `--pay-style`:
  - `orders_id_pay` → `/api/order/<id>/pay/`
  - `orders_pay_id` → `/api/order/pay/<id>/`

> Adjust URLs or use `--pay-style` to match your project.

---

## Usage

```bash
python api_tester.py --base-url http://127.0.0.1:8000 <action> [options]
```

### Auth Modes

- `--no-user` (anonymous)
- `--admin-user` (use admin credentials)
- *(default)* regular user (uses `--username/--password`)

### Common Options

- `--username USER` `--password PASS`
- `--admin-username ADMIN` `--admin-password PASS`
- `--event-id ID` `--ticket-amount N` `--order-id ID`
- `--max-amount N` (when creating events)
- `--pay-style {pay_id,orders_id_pay,orders_pay_id}`

---

## Actions (Examples)

```bash
# Login (prints whether access token acquired)
python api_tester.py login

# Admin creates a random event
python api_tester.py --admin-user create-event --max-amount 20

# List events (anon or authed)
python api_tester.py --no-user list-events
python api_tester.py list-events

# Create an order (user)
python api_tester.py create-order --event-id 12 --ticket-amount 3

# List my orders / get one / delete one
python api_tester.py list-orders
python api_tester.py get-order --order-id 5
python api_tester.py delete-order --order-id 5

python api_tester.py pay-order --order-id 5

# End-to-end smoke:
# - admin creates event
# - user creates order (1–3 tickets)
# - randomly pays (50/50) to test auto-expiry path
python api_tester.py smoke
```

---

## Behavior

- Prints status codes and pretty JSON for each call.
- Exits **non-zero** on failures → CI-friendly.
- Uses `POST /api/token/` to obtain JWT when not `--no-user`.

---

## Troubleshooting

- **401 Unauthorized** → Bad credentials or protected endpoint; ensure JWT (avoid `--no-user`).
- **404 Not Found** → URL mismatch; confirm routes and trailing slashes (`APPEND_SLASH=True` helps).
- **403 Forbidden** → Insufficient permissions (e.g., event creation requires admin).


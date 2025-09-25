import argparse
import json
import random
import string
from datetime import date, timedelta
import sys
import requests

# ----------- Helpers -----------

def rand_word(n=8):
    return "".join(random.choices(string.ascii_letters, k=n))

def rand_desc():
    return f"AutoEvt-{rand_word(5)}"

def rand_location():
    cities = ["Budapest", "Szeged", "Debrecen", "Győr", "Pécs", "Miskolc"]
    return random.choice(cities) + " " + rand_word(4)

def rand_date(days_ahead=30):
    return (date.today() + timedelta(days=random.randint(0, days_ahead))).isoformat()

def pretty(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

def auth_headers(token):
    return {} if not token else {"Authorization": f"Bearer {token}"}

def post_json(url, payload, token=None):
    r = requests.post(url, json=payload, headers=auth_headers(token))
    return r.status_code, try_json(r)

def get_json(url, token=None):
    r = requests.get(url, headers=auth_headers(token))
    return r.status_code, try_json(r)

def delete(url, token=None):
    r = requests.delete(url, headers=auth_headers(token))
    return r.status_code, try_json(r)

def try_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"_non_json_response": resp.text, "_status": resp.status_code}

# ----------- Actions -----------

def action_login(base, username, password):
    url = f"{base.rstrip('/')}/api/token/"
    code, data = post_json(url, {"username": username, "password": password})
    if code != 200:
        print(f"[login] FAILED ({code})")
        pretty(data)
        sys.exit(1)
    print("[login] OK")
    return data["access"], data.get("refresh")

def action_create_event(base, token, max_amount=None):
    """
    Requires your admin-only Event create endpoint.
    If your endpoint differs, adjust URL/payload.
    """
    url = f"{base.rstrip('/')}/api/event/"
    payload = {
        "description": rand_desc(),
        "date": rand_date(),
        "location": rand_location(),
        "max_amount": max_amount if max_amount is not None else random.randint(3, 20),
    }
    code, data = post_json(url, payload, token)
    print(f"[create-event] status={code}")
    pretty(data)
    if code not in (200, 201):
        sys.exit(1)
    # Try to infer event id from common fields
    evt_id = data.get("id") or data.get("pk") or data.get("event_id")
    return evt_id

def action_list_events(base, token=None):
    url = f"{base.rstrip('/')}/api/event/"
    code, data = get_json(url, token)
    print(f"[list-events] status={code}")
    pretty(data)
    if code != 200:
        sys.exit(1)
    # Try to return the first event id if available
    if isinstance(data, list) and data:
        first = data[0]
        evt_id = (first.get("id") or first.get("pk") or first.get("event_id"))
        return evt_id
    return None

def action_create_order(base, token, event_id, ticket_amount):
    """
    Uses your OrderCreate endpoint we wired:
    POST /api/order/  { "event_id": <int>, "ticket_amount": <int> }
    """
    url = f"{base.rstrip('/')}/api/order/"
    payload = {"event_id": int(event_id), "ticket_amount": int(ticket_amount)}
    code, data = post_json(url, payload, token)
    print(f"[create-order] status={code}")
    pretty(data)
    if code not in (200, 201):
        sys.exit(1)
    # Try to infer order id from response
    order_id = data.get("id") or data.get("order_id")
    return order_id

def action_list_orders(base, token):
    url = f"{base.rstrip('/')}/api/order/"
    code, data = get_json(url, token)
    print(f"[list-orders] status={code}")
    pretty(data)
    if code != 200:
        sys.exit(1)
    # Return first order id if present
    if isinstance(data, list) and data:
        first = data[0]
        oid = first.get("id") or first.get("order_id")
        return oid
    return None

def action_delete_order(base, token, order_id):
    url = f"{base.rstrip('/')}/api/order/{int(order_id)}/"
    code, data = delete(url, token)
    print(f"[delete-order] status={code}")
    pretty(data)
    if code != 204:
        sys.exit(1)

def action_pay_order(base, token, order_id):
    base = base.rstrip("/")

    url = f"{base}/api/order/pay/{int(order_id)}/"
    r = requests.put(url, headers=auth_headers(token))

    try:
        data = r.json()
    except Exception:
        data = {"_non_json_response": r.text}

    print(f"[pay-order] {url} status={r.status_code}")
    pretty(data)

    if r.status_code not in (200, 201, 204):
        sys.exit(1)
    return r.status_code, data

# ----------- CLI -----------

def main():
    # -------------- CONFIG ---------------
    ap = argparse.ArgumentParser(description="Simple DRF endpoint tester")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of your Django app")
    ap.add_argument("--username", default="user1", help="Normal username")
    ap.add_argument("--password", default="@jm>D_5Tz6hf:%!", help="Normal user password")
    ap.add_argument("--admin-username", default="admin", help="Admin username")
    ap.add_argument("--admin-password", default="admin", help="Admin password")

    # auth mode
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--no-user", action="store_true", help="Do not authenticate")
    g.add_argument("--admin-user", action="store_true", help="Authenticate as admin instead of regular user")

    # action
    ap.add_argument("action", choices=[
        "login",
        "create-event",
        "list-events",
        "create-order",
        "list-orders",
        "get-order",
        "delete-order",
        "pay-order",
        "smoke",      # simple end-to-end flow
    ], help="Action to perform")

    # params
    ap.add_argument("--event-id", type=int, help="Event id for create-order")
    ap.add_argument("--ticket-amount", type=int, default=1, help="Ticket amount for create-order (default: 1)")
    ap.add_argument("--order-id", type=int, help="Order id for get/delete")
    ap.add_argument("--max-amount", type=int, help="Max capacity when creating an event")

    args = ap.parse_args()

    # resolve auth
    token = None
    if not args.no_user:
        if args.admin_user:
            token, _ = action_login(args.base_url, args.admin_username, args.admin_password)
        else:
            token, _ = action_login(args.base_url, args.username, args.password)

    # route actions
    if args.action == "login":
        # already logged above
        print({"access": bool(token)})
        return

    if args.action == "create-event":
        if not token:
            print("This requires authentication (ideally admin). Use --admin-user.")
            sys.exit(2)
        evt_id = action_create_event(args.base_url, token, args.max_amount)
        print(f"Created event id: {evt_id}")
        return

    if args.action == "list-events":
        evt_id = action_list_events(args.base_url, token if not args.no_user else None)
        if evt_id is not None:
            print(f"First event id: {evt_id}")
        return

    if args.action == "create-order":
        if not token:
            print("This requires authentication (user).")
            sys.exit(2)
        event_id = args.event_id
        if not event_id:
            # try to get one
            event_id = action_list_events(args.base_url, token)
            if not event_id:
                print("No events found to order from. Create one with --admin-user create-event.")
                sys.exit(2)
        oid = action_create_order(args.base_url, token, event_id, args.ticket_amount)
        print(f"Created order id: {oid}")
        return

    if args.action == "list-orders":
        if not token:
            print("This requires authentication.")
            sys.exit(2)
        oid = action_list_orders(args.base_url, token)
        if oid:
            print(f"First order id: {oid}")
        return

    if args.action == "delete-order":
        if not token:
            print("This requires authentication.")
            sys.exit(2)
        if not args.order_id:
            print("Provide --order-id")
            sys.exit(2)
        action_delete_order(args.base_url, token, args.order_id)
        return
    
    if args.action == "pay-order":
        if args.no_user:
            print("This requires authentication.")
            sys.exit(2)
        if not args.order_id:
            print("Provide --order-id")
            sys.exit(2)
        action_pay_order(args.base_url, token, args.order_id)
        return

    if args.action == "smoke":
        """
        Smoke test:
        - login as admin
        - create random event
        - login as user
        - create order (1-3 tickets)
        - list orders
        - get first order
        """
        # admin creates event
        admin_token, _ = action_login(args.base_url, args.admin_username, args.admin_password)
        evt_id = action_create_event(args.base_url, admin_token, args.max_amount)
        print(f"[smoke] event_id={evt_id}")

        # user creates order
        user_token, _ = action_login(args.base_url, args.username, args.password)
        qty = random.randint(1, 3)
        oid = action_create_order(args.base_url, user_token, evt_id, qty)

        print(f"[smoke] order_id={oid}")

        # 50/50 chance to pay now (to let some orders auto-expire)
        if random.choice([True, False]):
            action_pay_order(args.base_url, user_token, oid)
        else:
            print("[smoke] skipping pay to test auto-failure")

        # list + get
        action_list_orders(args.base_url, user_token)
        print("[smoke] OK")
        return


if __name__ == "__main__":
    main()
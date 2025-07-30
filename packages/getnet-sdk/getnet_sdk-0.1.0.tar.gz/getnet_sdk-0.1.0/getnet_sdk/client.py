import base64
import datetime
import hashlib
import secrets
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **kw):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
        )

class GetnetClient:
    TEST_BASE = "https://checkout.test.getnet.cl/api"
    PROD_BASE = "https://checkout.getnet.cl/api"

    def __init__(
        self,
        login: str,
        secret_key: str,
        return_url: str,
        sandbox: bool = True,
        session: requests.Session = None,
    ):
        self.login = login
        self.secret = secret_key
        self.return_url = return_url
        self.base_url = self.TEST_BASE if sandbox else self.PROD_BASE
        self.session = session or requests.Session()
        self.session.mount("https://", TLSAdapter())

    def _auth(self) -> dict:
        nonce_b = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_b).decode()
        seed = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-00:00")
        raw = nonce_b + seed.encode() + self.secret.encode()
        tran_key = base64.b64encode(hashlib.sha256(raw).digest()).decode()
        return {"login": self.login, "tranKey": tran_key, "nonce": nonce, "seed": seed}

    def create_session(
        self,
        order_id: str,
        total: float,
        currency: str = "CLP",
        buyer: dict = None,
        expiration_minutes: int = 15,
        locale: str = "es_CL",
        ip_address: str = None,
        user_agent: str = None,
        **extra_fields,
    ) -> dict:
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)
        exp_str = exp.strftime("%Y-%m-%dT%H:%M:%S+00:00")

        payload = {
            "auth": self._auth(),
            "locale": locale,
            "payment": {
                "reference": order_id,
                "amount": {"currency": currency, "total": total},
            },
            "expiration": exp_str,
            "returnUrl": self.return_url,
        }
        if buyer:
            payload["buyer"] = buyer
        if ip_address:
            payload["ipAddress"] = ip_address
        if user_agent:
            payload["userAgent"] = user_agent
        payload.update(extra_fields)

        resp = self.session.post(
            f"{self.base_url}/session/",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        return resp.json() if resp.ok else {"error": resp.text, "status": resp.status_code}

    def get_request_information(self, session_id: str) -> dict:
        resp = self.session.post(
            f"{self.base_url}/session/{session_id}",
            json={"auth": self._auth()},
            headers={"Content-Type": "application/json"},
        )
        return resp.json() if resp.ok else {"error": resp.text, "status": resp.status_code}
    
    def reverse_payment(self, request_id: str) -> dict:
        payload = {
            "auth": self._auth(),
            "requestId": request_id
        }
        resp = self.session.post(
            f"{self.base_url}/session/{request_id}/reverse",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        return resp.json() if resp.ok else {"error": resp.text, "status": resp.status_code}

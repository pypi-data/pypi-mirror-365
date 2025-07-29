import urllib3
import json
from urllib3.util.retry import Retry
from urllib3.util.timeout import Timeout

class HTTPClient:
    def __init__(self, base_url="https://accept.paymob.com/api", retries=3, backoff=0.5):
        retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=[500, 502, 503, 504])
        self.http = urllib3.PoolManager(retries=retry, timeout=Timeout(connect=5.0, read=10.0))
        self.base_url = base_url

    def post(self, path, data):
        url = f"{self.base_url}/{path}"
        encoded = json.dumps(data).encode('utf-8')
        headers = {
            'Content-Type': 'application/json'
        }
        resp = self.http.request(
            'POST',
            url,
            body=encoded,
            headers=headers
        )
        if resp.status >= 400:
            raise Exception(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")

        return json.loads(resp.data.decode('utf-8'))
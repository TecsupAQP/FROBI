"""Original PDFs in Cloudflare R2 through its S3 API, signed with AWS Signature V4.

Signed by hand over httpx (already a dependency) instead of pulling boto3 into a 320 MB container.
Objects are private: the front only reads them through short-lived presigned URLs (RNF08).
"""

import hashlib
import hmac
from datetime import UTC, datetime
from urllib.parse import quote, urlsplit

import httpx

from frobi.modules.materials.application.ports import FileStorageUnavailable

REGION = "auto"
SERVICE = "s3"
ALGORITHM = "AWS4-HMAC-SHA256"
UNSIGNED_PAYLOAD = "UNSIGNED-PAYLOAD"
TIMEOUT_SECONDS = 20.0


def _encode(value: str, safe: str = "-_.~") -> str:
    return quote(value, safe=safe)


def _hmac(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode(), hashlib.sha256).digest()


class R2FileStorage:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key_id: str,
        secret_access_key: str,
        bucket: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        parts = urlsplit(endpoint.rstrip("/"))
        self._scheme = parts.scheme or "https"
        self._host = parts.netloc
        self._access_key_id = access_key_id
        self._secret = secret_access_key
        self._bucket = bucket
        self._transport = transport

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        response = await self._send("PUT", key, data, {"content-type": content_type})
        if response.status_code != httpx.codes.OK:
            raise FileStorageUnavailable(f"R2 answered {response.status_code} to PUT")

    async def delete(self, key: str) -> None:
        response = await self._send("DELETE", key, b"", {})
        if response.status_code not in (httpx.codes.OK, httpx.codes.NO_CONTENT):
            raise FileStorageUnavailable(f"R2 answered {response.status_code} to DELETE")

    def signed_url(self, key: str, *, expires_in: int, filename: str) -> str:
        """A GET URL valid for ``expires_in`` seconds that the browser shows inline."""
        now = datetime.now(UTC)
        query = {
            "X-Amz-Algorithm": ALGORITHM,
            "X-Amz-Credential": f"{self._access_key_id}/{self._scope(now)}",
            "X-Amz-Date": now.strftime("%Y%m%dT%H%M%SZ"),
            "X-Amz-Expires": str(expires_in),
            "X-Amz-SignedHeaders": "host",
            "response-content-disposition": f"inline; filename*=UTF-8''{_encode(filename)}",
            "response-content-type": "application/pdf",
        }
        canonical_query = "&".join(
            f"{_encode(name)}={_encode(value)}" for name, value in sorted(query.items())
        )
        signature = self._signature(
            "GET", self._path(key), canonical_query, {"host": self._host}, UNSIGNED_PAYLOAD, now
        )
        return (
            f"{self._scheme}://{self._host}{self._path(key)}"
            f"?{canonical_query}&X-Amz-Signature={signature}"
        )

    def _path(self, key: str) -> str:
        return f"/{_encode(self._bucket)}/{_encode(key, safe='-_.~/')}"

    def _scope(self, now: datetime) -> str:
        return f"{now:%Y%m%d}/{REGION}/{SERVICE}/aws4_request"

    def _signature(
        self,
        method: str,
        path: str,
        canonical_query: str,
        headers: dict[str, str],
        payload_hash: str,
        now: datetime,
    ) -> str:
        names = sorted(headers)
        canonical_request = "\n".join(
            [
                method,
                path,
                canonical_query,
                "".join(f"{name}:{headers[name].strip()}\n" for name in names),
                ";".join(names),
                payload_hash,
            ]
        )
        string_to_sign = "\n".join(
            [
                ALGORITHM,
                now.strftime("%Y%m%dT%H%M%SZ"),
                self._scope(now),
                hashlib.sha256(canonical_request.encode()).hexdigest(),
            ]
        )
        key = _hmac(("AWS4" + self._secret).encode(), f"{now:%Y%m%d}")
        for part in (REGION, SERVICE, "aws4_request"):
            key = _hmac(key, part)
        return hmac.new(key, string_to_sign.encode(), hashlib.sha256).hexdigest()

    async def _send(
        self, method: str, key: str, body: bytes, extra_headers: dict[str, str]
    ) -> httpx.Response:
        now = datetime.now(UTC)
        payload_hash = hashlib.sha256(body).hexdigest()
        headers = {
            "host": self._host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": now.strftime("%Y%m%dT%H%M%SZ"),
            **extra_headers,
        }
        path = self._path(key)
        signature = self._signature(method, path, "", headers, payload_hash, now)
        headers["authorization"] = (
            f"{ALGORITHM} Credential={self._access_key_id}/{self._scope(now)}, "
            f"SignedHeaders={';'.join(sorted(headers))}, Signature={signature}"
        )
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, transport=self._transport) as http:
            try:
                return await http.request(
                    method, f"{self._scheme}://{self._host}{path}", headers=headers, content=body
                )
            except httpx.HTTPError as error:
                raise FileStorageUnavailable(f"R2 unreachable: {type(error).__name__}") from error

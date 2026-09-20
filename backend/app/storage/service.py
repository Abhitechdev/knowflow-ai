import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Service to interact directly with private Supabase Storage buckets via REST API."""

    def __init__(self):
        self.base_url = settings.NEXT_PUBLIC_SUPABASE_URL.rstrip("/")
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = settings.STORAGE_BUCKET

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }
        if content_type:
            h["Content-Type"] = content_type
        return h

    async def upload_file(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "application/octet-stream",
        upsert: bool = True,
    ) -> dict[str, Any]:
        """Uploads a file to the configured private Supabase Storage bucket."""
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{destination_path.lstrip('/')}"
        headers = self._headers(content_type)
        if upsert:
            headers["x-upsert"] = "true"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, content=file_bytes, headers=headers)
            if response.status_code not in (200, 201):
                logger.error(f"Failed to upload {destination_path}: {response.status_code} - {response.text}")
                raise RuntimeError(f"Storage upload failed ({response.status_code}): {response.text}")
            return response.json()

    async def download_file(self, file_path: str) -> bytes:
        """Downloads file bytes from private Supabase Storage."""
        url = f"{self.base_url}/storage/v1/object/authenticated/{self.bucket}/{file_path.lstrip('/')}"
        headers = self._headers()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                # Try unauthenticated object endpoint as fallback with auth headers
                fallback_url = f"{self.base_url}/storage/v1/object/{self.bucket}/{file_path.lstrip('/')}"
                fallback_resp = await client.get(fallback_url, headers=headers)
                if fallback_resp.status_code == 200:
                    return fallback_resp.content
                logger.error(f"Failed to download {file_path}: {response.status_code} - {response.text}")
                raise RuntimeError(f"Storage download failed ({response.status_code}): {response.text}")
            return response.content

    async def delete_file(self, file_path: str) -> bool:
        """Deletes a file from Supabase Storage."""
        url = f"{self.base_url}/storage/v1/object/{self.bucket}"
        headers = self._headers(content_type="application/json")
        body = {"prefixes": [file_path.lstrip("/")]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request("DELETE", url, headers=headers, json=body)
            if response.status_code not in (200, 204):
                logger.warning(f"Failed to delete {file_path}: {response.status_code} - {response.text}")
                return False
            return True

    async def get_signed_url(self, file_path: str, expires_in: int = 3600) -> str | None:
        """Generates a secure temporary signed URL to download or view a private file."""
        url = f"{self.base_url}/storage/v1/object/sign/{self.bucket}/{file_path.lstrip('/')}"
        headers = self._headers(content_type="application/json")
        body = {"expiresIn": expires_in}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=body)
            if response.status_code == 200:
                data = response.json()
                signed_path = data.get("signedURL")
                if signed_path:
                    if signed_path.startswith("http"):
                        return signed_path
                    return f"{self.base_url}/storage/v1{signed_path}"
            logger.warning(f"Failed to generate signed URL for {file_path}: {response.text}")
            return None


storage_service = SupabaseStorageService()

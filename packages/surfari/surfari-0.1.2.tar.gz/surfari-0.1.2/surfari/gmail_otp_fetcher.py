
import os
import re
import time
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiofiles
import httpx

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from surfari.config import PROJECT_ROOT

import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)

class GmailOTPClientAsync:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, token_file='token.json', secrets_file='client_secret.json'):
        self.token_file = os.path.join(PROJECT_ROOT, token_file)
        self.secrets_file = os.path.join(PROJECT_ROOT, secrets_file)
        self.creds = None
        self.executor = ThreadPoolExecutor()

    async def _refresh_creds_async(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(self.executor, self.creds.refresh, Request())

    async def _run_oauth_flow(self) -> Credentials:
        """
        Launch the OAuth browser flow and return new credentials.
        """
        logger.debug("[🔐] Launching OAuth browser flow...")
        flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.SCOPES)
        return flow.run_local_server(port=8080)

    async def authenticate(self):
        # Load existing credentials if token file exists.
        if os.path.exists(self.token_file):
            async with aiofiles.open(self.token_file, 'r') as f:
                token_data = await f.read()
                self.creds = Credentials.from_authorized_user_info(json.loads(token_data), self.SCOPES)

        # If credentials don't exist or are invalid, try to refresh or run OAuth flow.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.debug("[🔄] Refreshing access token...")
                try:
                    await self._refresh_creds_async()
                except Exception as e:
                    logger.error("Refreshing access token failed: %s", e)
                    self.creds = await self._run_oauth_flow()
            else:
                self.creds = await self._run_oauth_flow()

            # Save the new credentials.
            async with aiofiles.open(self.token_file, 'w') as f:
                await f.write(self.creds.to_json())


    async def extract_code_from_subject(self, subject):
        if 'code' not in subject.lower():
            return None
        codes = re.findall(r'\b\d{4,8}\b', subject)
        return codes[0] if codes else None


    async def get_otp_code(self, from_me=True, within_seconds=30, retry_interval=10, max_retries=6):
        retry_count = 0
        while retry_count < max_retries:
            retry_count += 1
            logger.debug(f"[🔄] Attempt {retry_count}/{max_retries} to fetch OTP code...")
            code = await self.get_latest_code(from_me, within_seconds)
            if code:
                return code
            logger.debug(f"[!] No OTP found, retrying in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)
            
    async def get_latest_code(self, from_me=True, within_seconds=600):
        await self.authenticate()
        timestamp = int(time.time()) - within_seconds
        query = f"after:{timestamp}"
        if from_me:
            query = f"from:me {query}"

        headers = {
            "Authorization": f"Bearer {self.creds.token}"
        }

        async with httpx.AsyncClient() as client:
            list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
            list_params = {
                "q": query,
                "labelIds": "INBOX",
                "maxResults": 5
            }

            logger.debug(f"[>] Querying Gmail with: {query}")
            list_resp = await client.get(list_url, headers=headers, params=list_params)
            list_resp.raise_for_status()
            messages = list_resp.json().get('messages', [])

            for message in messages:
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message['id']}"
                msg_resp = await client.get(msg_url, headers=headers, params={"format": "metadata", "metadataHeaders": ["Subject"]})
                msg_resp.raise_for_status()
                headers_list = msg_resp.json().get("payload", {}).get("headers", [])

                subject = ""
                for h in headers_list:
                    if h["name"].lower() == "subject":
                        subject = h["value"]
                        break

                code = await self.extract_code_from_subject(subject)
                if code:
                    logger.debug(f"[✓] Found OTP: {code} in subject: {subject}")
                    return code

        logger.debug("[!] No OTP found in subjects.")
        return None

# Example usage
async def main():
    client = GmailOTPClientAsync()
    otp = await client.get_latest_code(from_me=True, within_seconds=300)
    logger.debug(f"Latest OTP: {otp}")

if __name__ == '__main__':
    asyncio.run(main())

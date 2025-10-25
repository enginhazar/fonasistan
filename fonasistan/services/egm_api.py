import requests
import json
from typing import Optional, Dict, Any


class EGMApiService:

    TOKEN_URL = "https://emakinpublic.egm.org.tr/rpc/login/getTokenFromApiKey"
    FETCH_URL = "https://emakinpublic.egm.org.tr/rpc/modules/invoke"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._cached_token: Optional[str] = None

    # ------------------------------
    # 🔹 Token Yönetimi
    # ------------------------------
    def _get_token(self) -> Optional[str]:
        """
        API token'ını cache'ler. Eğer daha önce alınmışsa yeniden istek atmaz.
        """
        if self._cached_token:
            return self._cached_token

        payload = {"apiKey": self.api_key}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.TOKEN_URL, json=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            self._cached_token = token_data.get('token')

            if not self._cached_token:
                print("⚠️ Token yanıtında 'token' alanı bulunamadı.")
            return self._cached_token

        except requests.exceptions.RequestException as e:
            print(f"❌ Token alınırken hata oluştu: {e}")
            return None

    # ------------------------------
    # 🔹 Fon Listesi
    # ------------------------------
    def fetch_fon_list(self) -> Optional[Dict[str, Any]]:
        """
        """
        bearer_token = self._get_token()
        if not bearer_token:
            print("⚠️ Token alınamadı, fon listesi çekilemiyor.")
            return None

        payload = {
            "module": "Functions",
            "function": "getFundListCriteriaValues",
            "arguments": ["", 130],
            "callContext": {
                "processVersionId": "17ae00f5-cb06-423c-baa2-a70053e6db9f",
                "instanceId": None,
                "authenticationToken": None,
                "contentTypeId": None,
                "context": None,
                "contextId": None
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }

        try:
            response = requests.post(self.FETCH_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Fon listesi alınırken hata oluştu: {e}")
            return None

    # ------------------------------
    # 🔹 Fon Detayı
    # ------------------------------
    def fetch_fon_detail(self, fund_id: str) -> Optional[Dict[str, Any]]:
        """
        Belirli bir fonun detay bilgilerini getirir.
        """
        bearer_token = self._get_token()
        if not bearer_token:
            print("⚠️ Token alınamadı, fon detayı çekilemiyor.")
            return None

        payload = {
            "module": "EGMFunctions",
            "function": "getReportData",
            "arguments": [
                {
                    "testMode": False,
                    "domain": "",
                    "company": "",
                    "hash": None,
                    "culture": "tr-TR",
                    "altCulture": "tr-TR",
                    "id": "66087fe1-a426-4dbf-8cfc-459e9f40bb5a",
                    "parameters": {
                        "r": "66087fe1-a426-4dbf-8cfc-459e9f40bb5a",
                        "fk": fund_id,
                        "hideback": "true"
                    }
                }
            ],
            "callContext": {
                "processVersionId": "ac8f57c9-dfbd-48d6-9db9-75d12406f502",
                "instanceId": None,
                "authenticationToken": None,
                "contentTypeId": None,
                "context": None,
                "contextId": None
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }

        try:
            response = requests.post(self.FETCH_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Fon detayı alınırken hata oluştu: {e}")
            return None

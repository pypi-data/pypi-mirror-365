import requests
import backoff
import json

from typing import Callable, Optional, cast, Union

from .types import RefreshTokenResponse
from .const import PINTEREST_SERVER_URL
from .exceptions import PinterestAccountLostAccessException

API_VERSION = 'v5'

class PinterestClient:
    def __init__(self, pinterest_credentials_path: str, _adscale_log: Optional[Callable] = None) -> None:
        with open(pinterest_credentials_path) as credentials:
            pinterest_credentials = json.load(credentials)
            pinterest_credentials = cast(dict[str, str], pinterest_credentials)
        self._app_id = pinterest_credentials['app_id']
        self._app_secret = pinterest_credentials['app_secret']
        self._token = pinterest_credentials['access_token']
        self._refresh_token = pinterest_credentials['refresh_token']

        # To get owner user id, you should go to Pinterest > Business Access > Select Arcane - The Feed Agency > Employee > Select the employee (ie: reporting@arcane.run (production) or pierre@arcane.run(staging))
        # > Get the last id in url: pinterest.fr/business/business-access/{business_id}/employees/{owner_user_id}/details/
        self._owner_user_id = pinterest_credentials.get('owner_user_id')
        if _adscale_log:
            self.log = _adscale_log
        else:
            self.log = print


    @backoff.on_exception(backoff.expo, requests.exceptions.HTTPError, max_tries=5)
    def _make_request(self, endpoint: str, method: str, params: Optional[dict] = None, headers: Optional[dict] = None, **kwargs) -> dict:
        """Send a request to Pinterest API"""
        if headers == None:
            headers={'Authorization': f'Bearer {self._token}'}
        response = requests.request(method=method, url=f"{PINTEREST_SERVER_URL}{endpoint}", headers=headers, params=params, **kwargs)
        response.raise_for_status()
        response = response.json()
        response_temp = response
        while response_temp.get('bookmark') != None:
            if params is None:
                params = {
                    'bookmark' : response_temp['bookmark']
                }
            else:
                params['bookmark'] = response_temp['bookmark']
            response_temp = requests.request(method=method, url=f"{PINTEREST_SERVER_URL}{endpoint}", headers=headers, params=params, **kwargs)
            response_temp.raise_for_status()
            response_temp = response_temp.json()
            response['items'] += response_temp['items']

        return response

    def refresh_token(self) -> RefreshTokenResponse:

        def _hash_token(token: str) -> str:
            import hashlib
            return hashlib.sha256(token.encode()).hexdigest()

        previous_hased_token = _hash_token(self._token)

        json_params = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
            'scope': 'ads:read,ads:write',
            'continuous_refresh': True
        }

        auth = self._app_id + ":" + self._app_secret
        import base64
        b64auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        auth_headers = {"Authorization": "Basic " + b64auth}
        response = requests.request(
            method='POST',
            url=f"{PINTEREST_SERVER_URL}/v5/oauth/token",
            data=json_params,
            headers={
                'ContentType': 'application/x-www-form-urlencoded',
                **auth_headers
            }
        )
        response.raise_for_status()
        response = response.json()
        new_token = response['access_token']
        assert _hash_token(new_token) != previous_hased_token, "New token is the same as the previous one"
        new_tokens: RefreshTokenResponse = {
            'access_token': new_token,
            'refresh_token': response['refresh_token'],
            'refresh_token_expires_at': str(response['refresh_token_expires_at'])
        }
        return new_tokens

    def get_account_campaigns(self, ad_account_id: str) -> list[dict[str, str]]:
        """Get account campaigns given its ID."""
        try:
            response = self._make_request(
                f'/{API_VERSION}/ad_accounts/{ad_account_id}/campaigns/',
                'GET'
                )
        except requests.exceptions.HTTPError as e:
            error_code = e.response.status_code
            if error_code in [401, 403]:
                raise PinterestAccountLostAccessException(f"We cannot access your pinterest account with the id: {ad_account_id}. Are you sure you granted access?")
            if error_code == 404:
                raise PinterestAccountLostAccessException(f"We cannot find this account with the id: {ad_account_id}. Are you sure you entered the correct id?")
            raise
        return [{
            'id': campaign.get('id'),
            'name': campaign.get('name'),
            'status': campaign.get('status')
        } for campaign in response['items']]

    def check_access_account(self, ad_account_id: str) -> None:
        """Check access by getting account campaigns given its ID."""
        self.get_account_campaigns(ad_account_id)

    def _get_all_ad_accounts(self) -> dict:
        params = {
            'owner_user_id': self._owner_user_id,
            'include_acl': True
        }
        response = self._make_request(
                f'/{API_VERSION}/ad_accounts/',
                'GET',
                params
                )
        return response['items']

    def get_ad_account_currency_code(self, ad_account_id: str) -> str:
        all_ad_accounts = self._get_all_ad_accounts()
        try:
            ad_account = next(ad_account for ad_account in all_ad_accounts if ad_account.get('id') == ad_account_id)
        except StopIteration:
            raise ValueError(f"Pinterest incorrest reponse: No ad_account with id: {ad_account_id}")
        return ad_account['currency']

    def get_ad_account_name(self, ad_account_id: str) -> str:
        all_ad_accounts = self._get_all_ad_accounts()
        try:
            ad_account = next(ad_account for ad_account in all_ad_accounts if ad_account.get('id') == ad_account_id)
        except StopIteration:
            raise ValueError(f"Pinterest incorrest reponse: No ad_account with id: {ad_account_id}")
        return ad_account['name']

    def post_ad_account_metrics_report(
        self,
        ad_account_id: str,
        start_date: str,
        end_date: str,
        columns: Optional[list[str]] = None,
        level: str = 'CAMPAIGN',
        granularity: str = 'DAY'
    ) -> dict:
        """Calling https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report

        Args:
            ad_account_id (str): The ad_account id
            start_date (str): Report start date (UTC): YYYY-MM-DD. Start date and end date must be within 30 days of each other.
            end_date (str): Report end date (UTC): YYYY-MM-DD
            columns (Optional[list[str]]): Metrics that you want to have in the report
            level (str, optional): Requested report type. Defaults to 'CAMPAIGN'.
            granularity (str, optional): the scale to aggregate metrics
        Returns:
            dict: A token you can use to download the report once it is ready.
        """
        json_params: dict[str, Union[str, list[str]]] = {
            'start_date': start_date,
            'end_date': end_date,
            'level': level,
            'granularity': granularity
        }

        if columns:
            json_params['columns'] =  columns
        return self._make_request(
                f'/{API_VERSION}/ad_accounts/{ad_account_id}/reports/',
                'POST',
                json=json_params
                )

    def get_campaign_metrics(self, ad_account_id: str, token: str) -> dict:
        """Calling https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report

        Args:
            ad_account_id (str): The ad_account id
            token (str): Token returned from post_ad_account_metrics_report

        Returns:
            dict: dict with the delivery metrics report url if ready
        """
        params = {
            'token': token
        }
        return self._make_request(
                f'/{API_VERSION}/ad_accounts/{ad_account_id}/reports/',
                'GET',
                params=params
                )


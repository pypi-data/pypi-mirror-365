import requests
import webbrowser
import time

from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urljoin
from requests import JSONDecodeError

from novara.config import config, Bootstrap_Config_Model

class DeviceCodeResponse(BaseModel):
    device_code: str
    verification_uri: str
    verification_uri_complete: str
    user_code: str
    expires_in: int
    interval: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    id_token: str
    created_at:datetime = Field(default_factory=datetime.now)

    class Config:
        extra = 'ignore'

    @property
    def valide_until(self):
        return self.created_at + timedelta(seconds=self.expires_in)
    
class UserinfoModel(BaseModel):
    sub:str
    email:str
    email_verified:bool
    name:str
    given_name:str
    preferred_username:str
    nickname:str
    groups:list[str]

class AuthSession(requests.Session):
    idp_url: str
    client_id: str
    token: Optional[TokenResponse] = None
    userinfo: Optional[UserinfoModel] = None

    def __init__(self, config:Bootstrap_Config_Model):
        self.token = TokenResponse.model_validate(config.auth_config.model_dump())
        self.idp_url = config.auth_config.idp_url
        self.client_id = config.auth_config.client_id
        super().__init__()

    def _request_token(self) -> Optional[TokenResponse]:
        if self.token and self.token.expires_in < datetime.now() and self.get_userinfo():
            return 

        device_code_resp = requests.post(
            urljoin(self.idp_url, '/application/o/device/'),
            data={'client_id': self.client_id, 'scope': 'openid profile email'}
        )
        device_code_resp.raise_for_status()
        device_code = DeviceCodeResponse.model_validate(device_code_resp.json())

        print(f'Please visit {device_code.verification_uri} and enter code {device_code.user_code} or {device_code.verification_uri_complete}')
        webbrowser.open(device_code.verification_uri_complete)

        poll_count = device_code.expires_in // device_code.interval

        for _ in range(poll_count):
            token_resp = requests.post(
                urljoin(self.idp_url, '/application/o/token/'),
                data={
                    'client_id': self.client_id,
                    'device_code': device_code.device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                }
            )

            if token_resp.status_code == 400 and token_resp.json().get('error') == 'authorization_pending':
                time.sleep(device_code.interval)
                continue

            token_resp.raise_for_status()
            self.token = TokenResponse.model_validate(token_resp.json())
            break
        else:
            print('Authentication expired please try again')
            exit()

        if not self.get_userinfo():
            raise Exception("failed to retreive valide userinfo")

        return self.token
        
    def get_userinfo(self) -> Optional[UserinfoModel]:
        resp = requests.get(urljoin(self.idp_url, '	/application/o/userinfo/'), headers={'Authorization': f'{self.token.token_type} {self.token.access_token}'})
        
        if not resp.ok:
            return None
        
        self.userinfo = UserinfoModel.model_validate(resp.json())

        return self.userinfo
    
    def request(self, method, url, params = None, data = None, headers = None, cookies = None, files = None, auth = None, timeout = None, allow_redirects = True, proxies = None, hooks = None, stream = None, verify = None, cert = None, json = None):
        if not self.token:
            self._request_token()

        headers = (headers or {}) | {'Authorization': f'{self.token.token_type} {self.token.access_token}'}
        
        return super().request(method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json)


request = AuthSession(config)
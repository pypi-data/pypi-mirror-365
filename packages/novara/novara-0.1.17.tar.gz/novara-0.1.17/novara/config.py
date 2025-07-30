from pydantic import BaseModel, Field
import yaml
from typing import Union, Optional, Literal
import logging
from datetime import datetime

from novara.constants import CONFIG_FILE, CONFIG_HOME

logger = logging.getLogger("rich")

class AuthConfig(BaseModel):
    idp_url:str = ''
    client_id:str = ''
    server_url:Optional[str] = None
    access_token: str = ''
    token_type: str = ''
    scope: str = ''
    expires_in: int = ''
    id_token: str = ''
    created_at:datetime = Field(default_factory=datetime.now)

    class Config:
        extra='ignore'

class Bootstrap_Config_Model(BaseModel):
    server_url:Optional[str]
    auth_config:Optional[AuthConfig] = None

class Config_Model(Bootstrap_Config_Model):
    author:str
    auth_type:str
    ssh_port:int
    ssh_user:str
    ssh_url:str
    ssh_privatekey:str
    logging_level:Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'] = 'NOTSET'



class ConfigManager(Config_Model):
    is_initialized: bool = False

    def __init__(self):
        object.__setattr__(self, 'is_initialized', False)       # avoid triggering loading logic

    def _load(self) -> dict:
        logger.info('loading new config...')
        try:
            with open(CONFIG_FILE, 'r') as config_file:
                return yaml.safe_load(config_file)
        except (FileNotFoundError, OSError):
            logger.error('config file not found or not accessible')
            logger.debug('did you run novara configure?')
            exit()
            
    def _initialize(self):
        super().__init__(**self._load())
        self.is_initialized = True
    
    def raw_write(self, config: dict):
        try:
            if not CONFIG_HOME.exists():
                logger.info(f"creating directory {CONFIG_HOME}")
                CONFIG_HOME.mkdir()
            config_directory = CONFIG_FILE.parent
            if not config_directory.exists():
                logger.info(f"creating directory {config_directory}")
                config_directory.mkdir()
            with open(CONFIG_FILE, 'w') as config_file:
                yaml.dump(config, config_file)
        except OSError:
            logger.error("Couldn't create the config file it's not writable")
            exit()

    def save(self):
        self.raw_write(self.raw_config)

    def __getattr__(self, name: str):
        if name in super().model_fields:
            self._initialize()

        return super().__getattribute__(name)

    @property
    def raw_config(self):
        """Access the config as a dict"""
        if not self.is_initialized:
            self._initialize()
        return self.model_dump()

    @raw_config.setter
    def raw_config(self, value: Union[dict, BaseModel]):
        if isinstance(value, BaseModel):
            value = value.model_dump()

        if self.is_initialized:
            value = {**self.model_dump(), **value}

        super().__init__(**value)

config = ConfigManager()
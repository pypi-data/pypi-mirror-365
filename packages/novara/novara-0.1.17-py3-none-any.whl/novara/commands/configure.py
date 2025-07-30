import rich_click as click
from urllib.parse import urljoin, urlparse
import os
import requests
import logging
from novara.request import AuthSession
from novara.config import Bootstrap_Config_Model, config, AuthConfig
from novara.utils import test_ssh_connection

logger = logging.getLogger('rich')


@click.command()
@click.option(
    "--server_url",
    "-l",
    default=None,
    help="url to api-endpoint of your novara instance",
)
@click.option(
    "--username",
    "-u",
    default=None,
    help="username for basic auth. In the case of oauth this parameter does nothing.",
)
@click.option(
    "--password",
    "-p",
    default=None,
    help="password for basic auth. In the case of oauth this parameter does nothing.",
)
@click.option(
    "--author",
    "-a",
    default=None,
    help="to specify what author to use for the exploits",
)
@click.option(
    "--log-level",
    default="NOTSET",
    help="Change the log level of the logger (CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET)"
)
def configure(server_url, username, password, author, log_level):
    """conect to novara backend & configure the cli"""

    # Priority: CLI argument > Environment variable > Prompt

    logging.basicConfig(level=log_level)

    server_url = (
        server_url
        or os.environ.get("SERVER_URL")
        or click.prompt("Please enter the Novara server URL")
    )
    try:
        r = requests.get(urljoin(server_url, '/api/config/auth_config/'))
        if not r.ok:
            raise click.ClickException(f"the remote responded with error:\n{r.text}")
    except requests.exceptions.ConnectionError:
        logger.error(f'failed to connect to backend. Is the url correct?')
        exit()

    try:
        auth_config = AuthConfig(server_url=server_url, idp_url=urljoin(server_url,'/auth/'), **r.json())
        local_config = Bootstrap_Config_Model(server_url=server_url, auth_config=auth_config)
    except requests.JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")

    if local_config.auth_config.auth_type == "basic":
        parsed_server_url = urlparse(server_url)
        
        local_config.auth_config.username = (
            username
            or parsed_server_url.username
            or click.prompt("Please enter your username")
        )

        local_config.auth_config.password = (
            password
            or parsed_server_url.password
            or os.environ.get("PASSWORD")
            or click.prompt("Please enter your password")
        )

    session = AuthSession(local_config.auth_config)

    if local_config.auth_config.auth_type == 'oauth':
        author = author or session.get_user_info().username

    author = (
        author
        or os.environ.get("AUTHOR_NAME")
        or click.prompt("Please enter your author username")
    )

    print('session configured')

    # -----------------------------------------------------------------

    r = session.get(urljoin(local_config.server_url, "/api/config/cli/"),
        params={'username':author}
    )
    if not r.ok:
        raise click.ClickException(f"the remote responded with error:\n{r.text}")

    # -----------------------------------------------------------------

    try:
        config.raw_write({**r.json(), **local_config.model_dump(), 'server_url':server_url, 'author':author, 'logging_level':log_level})
    except requests.JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")
    
    test_ssh_connection()
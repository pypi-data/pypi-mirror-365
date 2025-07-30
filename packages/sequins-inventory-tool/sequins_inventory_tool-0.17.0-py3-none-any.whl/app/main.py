"""Inventory tool CLI entry point."""

import logging
import os

from dotenv import load_dotenv
import typer

from app.ops.audit import audit_app
from app.ops.azenta import azenta_app
from app.ops.box import box_commands
from app.ops.database import app as database_app
from app.ops.location import location_commands
from app.ops.order import order_commands
from app.ops.parts import parts_app
from app.ops.product_numbering import product_naming_app
from app.ops.users import user_commands
from app.ops.variant import variant_commands
from app.utils.config import get_api_key, set_api_key_in_config
from app.utils.version_upgrade_check import check_for_new_version_and_notify

logger = logging.getLogger(__name__)

load_dotenv('.env')

app = typer.Typer()
app.add_typer(audit_app, name='audit', help='Display access audit logs.')
app.add_typer(
    azenta_app, name='azenta', help='Upload data from Azenta to the database.'
)
app.add_typer(box_commands, name='box', help='Manage boxes.')
app.add_typer(
    database_app,
    name='database',
    help='Interact directly with the underlying database.',
)
app.add_typer(
    location_commands, name='location', help='Manage location operations.'
)
app.add_typer(order_commands, name='order', help='Manage order operations.')
app.add_typer(parts_app, name='part', help='Manage part operations.')
app.add_typer(
    product_naming_app,
    name='product-numbering',
    help='Manage product numbering operations.',
)
app.add_typer(user_commands, name='user', help='Manage user operations.')
app.add_typer(
    variant_commands, name='variant', help='Manage variant operations.'
)


# Callback is called before executing every command, to allow us to set global
# state.
@app.callback()
def global_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(False, '--debug', help='Enable debug logging'),
    api_endpoint=typer.Option(
        os.getenv('API_ENDPOINT', 'https://inventory-api.corp.sequins.bio'),
        '--api-endpoint',
        help='Address of API endpoint.',
    ),
    api_key=typer.Option(None, '--api-key', help='API key for authentication.'),
    database_server_name=typer.Option(
        os.getenv('DATABASE_SERVER_NAME', ''),
        '--database-server-name',
        help='MongoDB server name',
    ),
    database_name=typer.Option(
        os.getenv('DATABASE_NAME', ''),
        '--database-name',
        help='MongoDB database name.',
    ),
):
    """Global callback to set the logging level."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # If API key is not specified in env var or command line, then see if we
    # can load it from the config file.
    if not api_key:
        api_key = get_api_key()

    # If not loaded from config, then attempt to load from environment.
    if not api_key:
        api_key = os.getenv('API_KEY')

    logger.debug(f'API endpoint: {api_endpoint}')
    logger.debug(f'API key: {api_key}')

    ctx.obj = {
        'api_endpoint': api_endpoint,
        'api_key': api_key,
        'database_server_name': database_server_name,
        'database_name': database_name,
    }

    check_for_new_version_and_notify()


@app.command(
    name='set-api-key', help='Save your API key to a local config file.'
)
def set_api_key(
    api_key: str = typer.Argument(..., help='The API key to save.'),
):
    """
    Saves the provided API key to a local configuration file.
    This key will be used by default for commands that require authentication.
    """
    set_api_key_in_config(api_key)
    typer.echo('API key successfully saved.')
    typer.echo('This key will be used by default for authenticated commands.')


if __name__ == '__main__':
    app()

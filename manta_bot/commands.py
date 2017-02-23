import os
import click
from manta_bot import app
from waitress import serve


DEFAULT_CONFIG = """\
#####################
# Run in debug mode #
#####################
#
# DEBUG = False

######################
# Telegram API token #
######################
# 
# Ask for your own API token to the @BotFather.
#
# API_TOKEN = '000000000:generateyourownapitokenandputithere'


################
# Webhoook URL #
################
#
# This is the URL where Telegram will POST updates for your bot.
# Must be HTTPS.
# DON'T forget to use a *trailing slash* e.g.
# https://aaabbbcc.ngrok.io/
# 
# For development, it's recommended to use ngrok (https://ngrok.com/)
# to setup a secure tunnel to localhost so you can develop the bot
# without setting up a domain and SSL certificates.
#
# WEBHOOK = 'https://manta.example.com/'

#############
# Stickers #
#############
#
# Set the stickers to use when can't find a word and when the user
# screws something up. Here are some good defaults:
#
DUNNO_STICKER = 'BQADAQADFgEAAgfchQABGqitkKZMNPEC'
GO_AWAY_STICKER = 'BQADAQADIAEAAgfchQABE5NrHw-8_kIC'


#########################
# Sentry DSN (optional) #
#########################
#
# If you want to use Sentry to monitor this app, this is it.
#
# SENTRY_DSN = ''
"""


SUPERVISOR_CONFIG = """\
[program:manta]
command=/home/manta/.nix-profile/bin/manta start
user=manta
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=syslog
stderr_logfile=syslog
"""


NGINX_CONFIG = """\
server {
    listen 80;
    server_name manta.example.com;
 
    return 301 https://$server_name$request_uri;
}
 
server {
    listen 443 ssl;
 
    server_name manta.example.com;
 
    ssl_certificate /etc/letsencrypt/live/manta.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/manta.example.com/privkey.pem;
 
    location / {
        proxy_pass http://unix:/tmp/manta_bot.socket;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""


HOME_DIR = os.path.expanduser('~')
CONFIG_DIR = os.path.join(HOME_DIR, '.config/manta')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.py')


@click.group()
def cli():
    """The original @manta_bot."""


@cli.command()
def init():
    """Initialize the configuration file.
    
    After initialization, make sure to configure
    all required values.
    """
    if os.path.isfile(CONFIG_FILE):
        click.echo("It seems that you already have a config file in %s" % CONFIG_FILE)
        click.confirm('Do you want to replace it?', abort=True)

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        f.write(DEFAULT_CONFIG)
    click.echo('Initialized new config in ~/.config/manta/config.py')
    click.echo('Edit it first to get any further.')


@cli.command()
def register():
    """Register the configured webhook with Telegram"""
    from manta_bot import bot
    click.echo('Registering webhook...')
    url = bot.register()
    click.echo("Webhook set to %s" % url)


@cli.command()
def runserver():
    """Run a development webserver on port 8000"""
    serve(app, host='127.0.0.1', port=8080)


@cli.command()
@click.option('--workers', default=4, help='Number of gunicorn workers.')
def start(workers):
    """Start waitress"""
    serve(app, unix_socket='/tmp/manta_bot.socket')


@cli.command()
def supervisor_sample():
    """Print a supervisor conf sample."""
    click.echo(SUPERVISOR_CONFIG)


@cli.command()
def nginx_sample():
    """Print a nginx conf sample."""
    click.echo(NGINX_CONFIG)

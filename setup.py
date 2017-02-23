# coding: utf-8
"""The original @manta_bot
"""
import setuptools


setuptools.setup(
    name='manta_bot',
    version='0.1.1',
    install_requires=['bender>=0.0.3', 'blinker', 'flask', 'gunicorn', 'click'],
    packages=setuptools.find_packages(),
    description = 'The original @manta_bot',
    author = 'José Sazo',
    author_email = 'jose.sazo@gmail.com',
    url = 'https://git.hso.rocks/hso/manta',
    download_url = 'https://git.hso.rocks/hso/manta/archive/0.1.1.tar.gz',
    include_package_data=True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points = {
        'console_scripts': [
            'manta=manta_bot.commands:cli'
        ],
    }
)

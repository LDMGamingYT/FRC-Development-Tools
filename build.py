# Buildscript for extension
# Packages extension into VSIX using vsce

import os
import json
import semver
import argparse
import requests
from colorama import Fore, Back, Style

# This is the hard-coded branch, change whenever applicable
branch = "-DEV"

parser = argparse.ArgumentParser()
parser.add_argument('action', nargs='?', default='build-only', choices=['build-only', 'publish'], help='action to perform')
parser.add_argument("-n", "--no-bump", action="store_true", help="build the extension without bumping patch version")
args = parser.parse_args()

version = "?"

if not args.no_bump:
    with open('package.json') as f:
        data = json.load(f)

    version = semver.bump_patch(data['version']) + branch
    data['version'] = version

    with open('package.json', 'w') as f:
        json.dump(data, f, indent=4)
    
os.system("vsce package")
filename = f"frc-devtools-{version}.vsix"

if args.action == "publish":
    owner = 'LDMGamingYT'
    repo = 'FRC-Development-Tools'
    prerelease = True
    print (f"\nPreparing to create release on {owner}/{repo}\n")

    release_body = input(f"{Style.BRIGHT}Release body? (Markdown is supported){Style.RESET_ALL}\n")
    print('\n')
    with open("GH_TOKEN", 'r') as f:
        token = f.read()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {token}'
    }

    payload = {
        'tag_name': version,
        'target_commitish': 'HEAD',
        'body': release_body,
        'draft': False,
        'prerelease': prerelease
    }

    print("Sending payload:", payload, '\n')

    response = requests.post(
        f'https://api.github.com/repos/{owner}/{repo}/releases',
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 201:
        print(f'{Back.GREEN}{Fore.BLACK} DONE {Style.RESET_ALL}Release created successfully. (version {version})')
    else:
        print(f'{Back.RED}{Fore.BLACK} ERROR {Style.RESET_ALL} Failed to create release. Response: {response.text}')
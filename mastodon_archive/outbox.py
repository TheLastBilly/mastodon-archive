#!/usr/bin/env python3
# Copyright (C) 2024    drevil (drevil@tilde.club)

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import os
import json
import http.server
import socketserver
from progress.bar import Bar
from urllib.parse import urlparse, parse_qs
from . import core
import re

actor_path = "actor.json"
outbox_path = "outbox.json"

def make_actor(data):
    actor = {}
    account = data["account"]

    actor["icon"] = {}
    actor["icon"]["url"] = account["avatar_static"]
    
    actor["name"] = account.pop("username")
    actor["preferredUsername"] = account.pop("display_name")
    actor["outbox"] = "outbox.json"

    return actor

def format_status(status):
    container = {}

    status["published"] = status.pop("created_at")
    status["attachment"] = status.pop("media_attachments")
    status["summary"] = status["content"]
    

    # del status["media_attachments"]
    # status.delete("media_attachments")

    for attachment in status["attachment"]:
        attachment["name"] = attachment["description"]
        attachment["mediaType"] = attachment["type"]

    container["type"] = "Create" if status["reblog"] == None else "Reblogged"
    container["object"] = status

    return container

def make_outbox(data):
    outbox = {}
    outbox["orderedItems"] = []
    statuses = data["statuses"]
    bar = None
    if len (statuses) > 0:
        bar = Bar("Exporting statuses", max = len(statuses))

    for status in statuses:
        outbox["orderedItems"].append(format_status(status))
        bar.next()

    if bar != None:
        bar.finish()

    return outbox

def outbox(args):
    """
    Find and serve all archive files for Meow.
    """
    (username, domain) = args.user.split("@")

    status_file = domain + ".user." + username + ".json"
    data = core.load(status_file, required=True, quiet=True, combine=args.combine)

    actor = make_actor(data)
    print(f"creating {actor_path}...", end="", flush=True)
    with open(actor_path, "w", encoding='utf-8') as f:
        json.dump(actor, f, ensure_ascii=False)
    print("OK")

    outbox = make_outbox(data)
    print(f"creating {outbox_path}...", end="", flush=True)
    with open(outbox_path, "w", encoding='utf-8') as f:
        json.dump(outbox, f, ensure_ascii=False)
    print("OK")
    
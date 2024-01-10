import io
import re
import threading
import time
import json
from datetime import datetime

import discord
import requests
import savepagenow

from globalvals import globalvals

def SaveClientNow(curVersion, v):
    ArchiveUrl = savepagenow.capture_or_cache(f"https://setup.rbxcdn.com/{curVersion}-{v}")
    print(f"Returned URL: {ArchiveUrl}")
    open("log.txt", "a").write(f"Attempting to capture {ArchiveUrl[0]}...\n")
    return ArchiveUrl[0]

def GetCurrentHash(CurrentBinaryType):
    if globalvals.DEBUG_MODE:
        return open("DebugHash.txt", "r").read()
    return requests.get(f"https://clientsettings.roblox.com/v2/client-version/{CurrentBinaryType}").json().get("clientVersionUpload", '')

def GetPkgManifest(curVersion):
    return requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{curVersion}-rbxPkgManifest.txt")

def GetPkgInstallerManifest(curVersion):
    return requests.get(f"https://s3.amazonaws.com/setup.roblox.com/{curVersion}-rbxInstallerPkgManifest.txt")
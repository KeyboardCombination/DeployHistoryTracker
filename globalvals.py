import io
import re
import threading
import time
from datetime import datetime

import discord
import requests
import savepagenow

class globalvals():
    BinaryTypes = [
        "WindowsPlayer",
        "WindowsStudio64",
        "MacPlayer",
        "MacStudio"
    ]

    DEBUG_MODE = True
    DEBUG_CHANNEL = BinaryTypes[3]

    token = open("/home/red/tokenclientsearch.txt", "r").read()
    Webhook = discord.SyncWebhook.from_url(token)
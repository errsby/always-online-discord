import discord
from discord.ext import commands
import asyncio
import sys
from datetime import datetime, time
import pytz
import requests

TOKEN = ""
API_BASE_URL = f"https://worker-name.workers.dev"

CONFIG = {}
CURRENT_USER = "user1"

bot = commands.Bot(command_prefix="!", self_bot=True)

def is_dnd_time(dnd_start_str, dnd_end_str):
    pst = pytz.timezone("US/Pacific")
    now = datetime.now(pst).time()

    dnd_start = datetime.strptime(dnd_start_str, "%H:%M").time()
    dnd_end = datetime.strptime(dnd_end_str, "%H:%M").time()

    if dnd_start < dnd_end:
        return dnd_start <= now < dnd_end
    else:
        return now >= dnd_start or now < dnd_end

async def fetch_config():
    global CONFIG
    url = f"{API_BASE_URL}/{CURRENT_USER}"
    try:
        print(f"[*] Fetching config from {url}")
        response = requests.get(url)
        if response.status_code == 200:
            CONFIG = response.json()
            print(f"[*] Config updated: {CONFIG}")
        else:
            print(f"[!] Failed to fetch config. Status code: {response.status_code}")
    except Exception as e:
        print(f"[!] Exception fetching config: {e}")

async def apply_status_once(activity_text, status):
    try:
        activity = discord.CustomActivity(name=activity_text) if activity_text else None
        await bot.change_presence(status=status, activity=activity)
        print(f"[*] Status applied: {status}, Activity: {activity_text}")
    except Exception as e:
        print(f"[!] Error applying status: {e}")

async def rotate_statuses_loop():
    rotate_index = -1

    while True:
        try:
            if not CONFIG:
                print("[!] No config loaded, skipping rotation")
                await asyncio.sleep(10)
                continue

            dnd_enabled = CONFIG.get("dnd_enabled", False)
            dnd_start = CONFIG.get("dnd_start", "22:00")
            dnd_end = CONFIG.get("dnd_end", "08:00")
            dnd_message = CONFIG.get("dnd_message", "")
            indicator = CONFIG.get("indicator", "idle").lower()
            rotating = CONFIG.get("rotating", False)
            statuses = CONFIG.get("statuses", [])
            rotation_interval = CONFIG.get("rotation_interval_seconds", 60)

            # Map indicator to discord.Status
            status_map = {
                "online": discord.Status.online,
                "idle": discord.Status.idle,
                "dnd": discord.Status.dnd,
                "offline": discord.Status.offline,
            }
            discord_status = status_map.get(indicator, discord.Status.idle)

            if dnd_enabled and is_dnd_time(dnd_start, dnd_end):
                # DND status override
                await apply_status_once(dnd_message, discord.Status.dnd)
                await asyncio.sleep(60)  # Sleep a minute before re-checking DND
                continue

            if rotating and statuses:
                rotate_index = (rotate_index + 1) % len(statuses)
                activity_text = statuses[rotate_index]
            else:
                activity_text = CONFIG.get("custom_status", "")

            await apply_status_once(activity_text, discord_status)
            await asyncio.sleep(rotation_interval)
        except Exception as e:
            print(f"[!] Error in rotate_statuses_loop: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f"[*] Logged in as {bot.user} (ID: {bot.user.id})")

    await fetch_config()
    # Start rotation loop in background
    bot.loop.create_task(rotate_statuses_loop())
    # Also start auto refresh config every 60s in parallel
    bot.loop.create_task(auto_refresh_loop())

async def auto_refresh_loop():
    while True:
        try:
            await fetch_config()
        except Exception as e:
            print(f"[!] Error in auto_refresh_loop: {e}")
        await asyncio.sleep(60)  # Always refresh config every 60s

if __name__ == "__main__":
    if not TOKEN:
        print("[!] Token not set!")
        sys.exit(1)
    bot.run(TOKEN)

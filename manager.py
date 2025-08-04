import os
import time
import multiprocessing
import subprocess
from pathlib import Path
from typing import List, Dict

# === CONFIGURATION ===

BOTS: List[Dict[str, str]] = [
    {"path": "bots/user1", "entry": "main.py"},
]

RESTART_DELAY: int = 5      # seconds
AUTO_RESTART: bool = True


def run_bot(bot_dir: str, script_name: str) -> None:
    bot_path = Path(bot_dir).resolve()
    script_path = bot_path / script_name

    if not script_path.is_file():
        print(f"[ERROR] Script not found: {script_path}")
        return

    while True:
        try:
            print(f"[INFO] Starting bot at {script_path}")

            proc = subprocess.Popen(
                ["python", str(script_path.name)],
                cwd=bot_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )

            assert proc.stdout is not None
            for line in proc.stdout:
                print(f"[{bot_path.name}] {line.strip()}")

            exit_code = proc.wait()
            print(f"[WARN] Bot {bot_path.name} exited with code {exit_code}")

            if not AUTO_RESTART:
                break

            print(f"[INFO] Restarting bot {bot_path.name} in {RESTART_DELAY}s...")
            time.sleep(RESTART_DELAY)

        except Exception as e:
            print(f"[ERROR] {bot_path.name} crashed: {e}")
            if not AUTO_RESTART:
                break
            time.sleep(RESTART_DELAY)


def main():
    processes = []

    for bot in BOTS:
        p = multiprocessing.Process(target=run_bot, args=(bot["path"], bot["entry"]))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received. Terminating bots...")
        for p in processes:
            p.terminate()
            p.join()
        print("[INFO] All bots terminated.")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Safe for Windows + Python 3.12+
    main()

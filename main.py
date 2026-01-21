import requests
import random
import time
from fake_useragent import UserAgent
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Configs via env vars no Render (adicione em Environment Variables)
TARGET_URL = os.getenv('TARGET_URL', 'https://exemplo.com/ping')  # obrigatorio
PROXY_LIST_STR = os.getenv('PROXY_LIST', '')  # "http://ip1:port\nhttp://ip2:port"
THREADS = int(os.getenv('THREADS', 5))
MIN_DELAY = float(os.getenv('MIN_DELAY', 45))
MAX_DELAY = float(os.getenv('MAX_DELAY', 90))

PROXY_LIST = [p.strip() for p in PROXY_LIST_STR.split('\n') if p.strip()]

ua = UserAgent()

async def ping_with_proxy(session, proxy=None):
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Referer': random.choice([
            'https://www.google.com.br/',
            'https://www.bing.com/',
            'https://www.youtube.com/'
        ]),
        'Accept': '*/*'
    }
    try:
        proxy_dict = {'http': proxy, 'https': proxy} if proxy else None
        async with session.get(TARGET_URL, headers=headers, proxy=proxy, timeout=20) as resp:
            text = await resp.text()
            if resp.status == 200:
                print(f"[OK] Ping sucesso | Proxy: {proxy or 'direto'} | Status: {resp.status} | UA: {headers['User-Agent'][:50]}... | Response snippet: {text[:100]}")
                # Aqui pode adicionar parse: if 'saldo' in text or 'creditado' in text: print("Crédito detectado!")
            else:
                print(f"[FAIL] Status {resp.status} | Proxy: {proxy or 'direto'}")
    except Exception as e:
        print(f"[ERRO] {str(e)[:100]} | Proxy: {proxy or 'direto'}")

async def worker():
    async with aiohttp.ClientSession() as session:
        while True:
            proxy = random.choice(PROXY_LIST) if PROXY_LIST else None
            await ping_with_proxy(session, proxy)
            jitter = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"Próximo ping em {jitter:.1f}s...")
            await asyncio.sleep(jitter)

async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(THREADS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if not TARGET_URL or TARGET_URL == 'https://exemplo.com/ping':
        print("ERRO: Defina TARGET_URL em Environment Variables no Render!")
        exit(1)
    print(f"Bot iniciado | Target: {TARGET_URL} | Threads: {THREADS} | Proxies: {len(PROXY_LIST)}")
    asyncio.run(main())

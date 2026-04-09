import urllib.request
import time

SERVER_IPV4 = "172.28.0.10"
SERVER_IPV6 = "2001:db8:bbbb::10"
PORT = 8000


def make_request(url, version_name):
    print(f"\n=== Запрос по {version_name} ===")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read(800).decode('utf-8')
            print(f"Статус: {response.status}")
            print(f"Получено {len(content)} байт")
            print("Содержимое (начало):")
            print(content[:400])
    except Exception as e:
        print(f"Ошибка при {version_name}: {e}")


if __name__ == "__main__":
    print("Запуск теста IPv4 и IPv6...\n")

    # IPv4 запрос
    url_v4 = f"http://{SERVER_IPV4}:{PORT}/"
    make_request(url_v4, "IPv4")

    time.sleep(1)

    # IPv6 запрос
    url_v6 = f"http://[{SERVER_IPV6}]:{PORT}/"
    make_request(url_v6, "IPv6")

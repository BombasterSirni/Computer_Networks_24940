import socket
import csv
import subprocess

domains = [
    "google.com",
    "yandex.ru",
    "wikipedia.org",
    "github.com",
    "cloudflare.com"
]

results = []

for domain in domains:
    try:

        ip = socket.gethostbyname(domain)
        print(f"{domain} -> {ip}")

        result = subprocess.run(
            ["sudo", "traceroute", "-I", "-n", "-m", "40", "-w", "3", ip],
            capture_output=True,
            text=True,
            timeout=90
        )

        trace_output = result.stdout.strip()
        trace_clean = " | ".join(trace_output.splitlines())

        results.append([domain, ip, trace_clean])

        print(
            f"Traceroute выполнен ({len(trace_output.splitlines())} строк)\n")

    except Exception as e:
        print(f"Ошибка для {domain}: {e}")
        results.append([domain, "ERROR", str(e)])

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["Domain", "IP_Address", "Traceroute"])
    writer.writerows(results)

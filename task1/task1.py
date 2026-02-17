from pythonping import ping
import pandas as pd
import numpy as np


hosts = [("Google", "8.8.8.8"), ("localhost", "127.0.0.1"), ("Cloudflare", "1.1.1.1"), ("Quad9", "9.9.9.9"),
         ("Quad9_alt", "149.112.112.112"), ("Adguard", "94.140.14.14"), ("OpenDNS", "208.67.222.222"),
         ("Yandex", "77.88.8.8"), ("Verisign", "64.6.64.6"), ("Comodo Secure", "8.26.56.26")]

result_table = pd.DataFrame({
    "host_name": [],
    "host_ip": [],
    "packet_cnt": [],
    "rtt_avg": [],
    "rtt_min": [],
    "rtt_max": [],
    "packet_loss": []
})

for host in hosts:
    packet_cnt = np.random.randint(1, 10)
    responce = ping(target=host[1], count=packet_cnt)

    responce_data = {
        "host_name": host[0],
        "host_ip": host[1],
        "packet_cnt": packet_cnt,
        "rtt_avg": responce.rtt_avg_ms,
        "rtt_min": responce.rtt_min_ms,
        "rtt_max": responce.rtt_max_ms,
        "packet_loss": responce.packet_loss
    }

    result_table.loc[len(result_table)] = responce_data

print("Вот таблица статистики запросов:\n", result_table)

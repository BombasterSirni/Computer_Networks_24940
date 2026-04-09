# **Задание 10 про traceroutes**

## *Ручками в терминале*
1. txt-файл доменов:
```bash
cat > domains.txt << EOF
google.com
yandex.ru
wikipedia.org
github.com
cloudflare.com
EOF
```

2. создаем csv файл
```bash
echo '"Domain","IP_Address","Traceroute"' > results.csv
```

3. И цикл в консоли для каждого домена для вычисления traceroute:
```bash
while read -r domain; do
    ip=$(dig +short "$domain" A | head -n1)
    echo "$domain ($ip)"
    sudo traceroute -I -n -m 40 -w 3 "$ip" > temp_trace.txt 2>&1
    trace=$(tr '\n' '|' < temp_trace.txt | sed 's/|   $$//')
    echo "\"$domain\",\"$ip\",\"$trace\"" >> results.csv
done < domains.txt
```
    
4. Удаляем временный файл
```bash
rm -f temp_trace.txt
```

## *Python-скрипт*
```bash
python traceroute.py
```
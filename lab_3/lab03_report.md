# Лабораторная работа №3 — Nmap — сканирование сети и анализ уязвимостей

**Автор:** Матвеичев Андрей
**Группа:** М03-503
**Дата:** 2026-04-29

***

## Цель работы

Данная лабораторная работа посвящена изучению nmap и как с ним работать. Эта лабораторная работа послужит подпоркой для старта в выявлении и определении уязвимостей на уровне сканера портов, что бы освоить базовые методы сканирования.

Nmap — первый этап разведки в AppSec: определение attack surface (какие сервисы доступны извне), выявление устаревших версий ПО с известными CVE и обнаружение мисконфигураций (открытые порты, незащищённые сервисы). Результаты nmap — входные данные для анализа рисков (Lab 04) и последующего DAST-тестирования (Lab 08).

## Ход выполнения

### Шаг 0. 

Обновим систему
```
sudo dnf update; sudo dnf upgrade
```

Проверим наличие утилиты nmap. 
```
nmap -V
```
вывод:
```
Nmap version 7.92 ( https://nmap.org )
Platform: x86_64-redhat-linux-gnu
Compiled with: nmap-liblua-5.3.5 openssl-3.5.4 libssh2-1.11.1 libz-1.3.1.zlib-ng libpcre2-10.47 libpcap-1.10.6 nmap-libdnet-1.12 ipv6
Compiled without:
Available nsock engines: epoll poll select
```

В прошлой лабораторной мы создавали файл `nmapres.txt`, перенесем его в папку 3 лабы
```
mv Documents/nmapres.txt Documents/lab_3 
```

все настроено, значит можно переходить к выполнению.

### Шаг 1. Описание методов

#### TCP Connect: `-sT`
- Завершает полный «трехстороннее рукопожатие» (SYN -> SYN/ACK -> ACK).
- Самый надежный, но легко обнаруживается в логах систем (IPS/IDS).

#### TCP SYN: `-sS`
- Отправляет SYN, получает SYN/ACK и сразу обрывает связь (RST).
- «Скрытное» сканирование. 
- Быстрее, так как не тратит время на полное соединение.

#### UDP: `-sU` 
- Отправляет UDP-пакеты. 
- Если ответа нет — порт «открыт/фильтруется».
- Позволяет найти службы вроде DNS, DHCP, SNMP. 
- Часто игнорируется новичками, что является ошибкой.

#### NULL / FIN / Xmas: `-sN` / `-sF` / -`sX` 
- Используют нестандартные комбинации флагов (или их отсутствие).
- Помогают обойти stateless-файрволы и системы фильтрации. 
- Не работают против Windows.

#### Idle Scan: `-sI`
- Использует сторонний «зомби-хост» для отправки пакетов.
- Максимальная анонимность: ваш IP не появляется в логах.

### Шаг 2.
```
nmap localhost
```
вывод:
```
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000094s latency).
Other addresses for localhost (not scanned): ::1
Not shown: 999 closed tcp ports (conn-refused)
PORT    STATE SERVICE
631/tcp open  ipp

Nmap done: 1 IP address (1 host up) scanned in 0.06 seconds
```
анализ:
Базовое сканирование 1000 самых популярных портов. Видим один открытый порт 631/tcp. 


```
nmap -sC localhost
```
вывод:
```
PORT    STATE SERVICE
631/tcp open  ipp
|_http-title: Home - CUPS 2.4.18
| http-robots.txt: 1 disallowed entry 
|_/
```
анализ: 
Сканирование с использованием стандартного набора скриптов. видим программу CUPS - после яндексинга узнаем что это утилита для печати.

```
nmap -p- localhost
```
вывод:
```
Not shown: 65532 closed tcp ports (conn-refused)
PORT      STATE SERVICE
631/tcp   open  ipp
5355/tcp  open  llmnr
37357/tcp open  unknown
```
анализ:
Сканирование всех 65535 портов, видим что открыты 631 для ipp - гуглим, узнаем что это порт протокола печати, что подтверждает наши находки из прошлой команды, 5355 для llmnr - утилита разрешения хостов в сети, 37357 - хз.

```
sudo nmap -O localhost
```
вывод:
```
PORT    STATE SERVICE
631/tcp open  ipp
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.92%E=4%D=4/28%OT=631%CT=1%CU=43323%PV=N%DS=0%DC=L%G=Y%TM=69F0EC
OS:F9%P=x86_64-redhat-linux-gnu)SEQ(......
```
анализ: Попытка определить операционную систему, видим что команда определила redhead-linus-gnu, что верно, так как fedora базированна на redhat.

```
nmap -p 80 localhost
```
вывод:
```
PORT   STATE  SERVICE
80/tcp closed http
```
анализ: порт 80 закрыт, станддартный порт http.

```
nmap -p 443 localhost
```
вывод:
```
PORT    STATE  SERVICE
443/tcp closed https
```
анализ:  порт 443 закрыт, станддартный порт https.

```
nmap -p 8443 localhost
```
вывод:
```
PORT     STATE  SERVICE
8443/tcp closed https-alt
```
анализ: альтернативный порт https тоже закрыт.

```
nmap -p "*" localhost
```
вывод:
```
PORT     STATE SERVICE
631/tcp  open  ipp
5355/tcp open  llmnr
```
анализ: сканирование вообще всех портов, которые nmap знает по именам, тот же самый вывод.

```
nmap -sV -p 22,8080 localhost
```
вывод:
```
Other addresses for localhost (not scanned): ::1

PORT     STATE  SERVICE    VERSION
22/tcp   closed ssh
8080/tcp closed http-proxy
```
анализ: Определение версий сервисов на портах 22 и 8080. Порты закрыты, поэтому версию мы не узнаем.

```
nmap -sn 192.168.1.0/24
```
вывод:
```
...
Nmap done: 256 IP addresses (n hosts up) scanned in 16.26 seconds
```
анализ: Ping-сканирование подсети. Показывает, кто в сети «жив», не сканируя порты, видим что 6 хостов активны. Значит n устройствов активны в сети

```
nmap --open 192.168.1.1
```
вывод:
```
Not shown: 907 closed tcp ports (conn-refused), 86 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE
...
515/tcp  open  printer
...
```
анализ: анализируем одну из доступных в сети машин, видим ряд открытых портов. Я знаю что на этом адресе стоит принтер, поэтому виден порт 515 необходимый для сервисов печати.

```
nmap --packet-trace 192.168.1.1
```
вывод:
```
Starting Nmap 7.92 ( https://nmap.org ) at 2026-04-28 21:39 MSK
CONN (0.0497s) TCP localhost > 192.168.1.1:80 => Operation now in progress
CONN (0.0498s) TCP localhost > 192.168.1.1:443 => Operation now in progress
CONN (0.0676s) TCP localhost > 192.168.1.1:80 => Connected
NSOCK INFO [0.0680s] nsock_iod_new2(): nsock_iod_new (IOD #1)
...
```
анализ: packet-trace для 192.168.1.1

```
nmap --packet-trace scanme.nmap.org
```
вывод:
```
Starting Nmap 7.92 ( https://nmap.org ) at 2026-04-28 20:52 MSK
CONN (0.1438s) TCP localhost > ****:**** => Operation now in progress
CONN (0.1442s) TCP localhost > ****:**** => Operation now in progress
CONN (0.3388s) TCP localhost > ****:**** => Connected
```
анализ: Показывает каждый пакет, который nmap отправляет и получает от scanme.nmap.org. Отлично подходит для дебага.

```
nmap --iflist
```
вывод:
```
************************INTERFACES************************
DEV     (SHORT)   IP/MASK                                 TYPE     UP MTU   MAC
lo      (lo)      127.0.0.1/8                             loopback up 65536
...

**************************ROUTES**************************
DST/MASK                                 DEV     METRIC GATEWAY
************                            enpxxxx    100
*************                           docker0    0
.....

```
анализ: Используется для вывода списка интерфейсов и системных роутеров (маршрутизаторов), обнаруженных утилитой. Это полезно для отладки проблем с роутерами и неправильного описания устройств. вижу роутинг сети виртуальной машины через свой компьютер, виртуальный адаптер, созданный при настройке сети.

```
touch exmp_targets.txt
nmap -iL exmp_targets.txt
```
вывод: 
```
WARNING: No targets were specified, so 0 hosts scanned.
Nmap done: 0 IP addresses (0 hosts up) scanned in 0.02 seconds
# добавили в файл google.com
Starting Nmap 7.92 ( https://nmap.org ) at 2026-04-28 21:23 MSK
Nmap scan report for google.com (64.233.165.113)
Host is up (0.048s latency).
Other addresses for google.com (not scanned): 64.233.165.102 64.233.165.100 64.233.165.139 64.233.165.138 64.233.165.101 2a00:1450:4010:c08::64 2a00:1450:4010:c08::8b 2a00:1450:4010:c08::66 2a00:1450:4010:c08::71
rDNS record for 64.233.165.113: lg-in-f113.1e100.net
Not shown: 998 filtered tcp ports (no-response)
PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https
```
анализ: сканирование указанных адресов из файла, выдает открытые порты с возмодными сервисами.


```
nmap -A -iL exmp_targets.txt
```
вывод:
```
Other addresses for google.com (not scanned): 64.233.165.139 64.233.165.100 64.233.165.101 64.233.165.138 64.233.165.102 2a00:1450:4010:c08::71 2a00:1450:4010:c08::64 2a00:1450:4010:c08::8b 2a00:1450:4010:c08::66
rDNS record for 64.233.165.113: lg-in-f113.1e100.net
Not shown: 998 filtered tcp ports (no-response)
PORT    STATE SERVICE   VERSION
80/tcp  open  http      gws
...
```
анализ: Агрессивное сканирование (OS, версии, скрипты, traceroute) для списка целей из файла. Получаем актуальные сертификаты сервисов, настройки DNS, сервисы и прочее.

```
nmap -sA scanme.nmap.org
```
вывод:
```
Starting Nmap 7.92 ( https://nmap.org ) at 2026-04-28 21:30 MSK
Nmap scan report for scanme.nmap.org (45.33.32.156)
Host is up (0.00030s latency).
Other addresses for scanme.nmap.org (not scanned): 2600:3c01::f03c:91ff:fe18:bb2f
All 1000 scanned ports on scanme.nmap.org (45.33.32.156) are in ignored states.
Not shown: 1000 unfiltered tcp ports (reset)

Nmap done: 1 IP address (1 host up) scanned in 0.30 seconds
```
анализ: ACK-сканирование. Используется для определения правил файрвола (фильтруется порт или нет).

```
nmap -Pn scanme.nmap.org
```
вывод:
```

```
анализ: пинг-сканирование, заставляет программу выполнять запрошенные функции (сканирование портов, определение версии, определение ОС и т. д.) для всех указанных целевых IP-адресов



### Шаг 3.  NSE-скрипты для поиска уязвимостей

```
nmap --script=vuln localhost -vv
```

вывод:
```
...
Nmap done: 1 IP address (1 host up) scanned in 521.65 seconds
           Raw packets sent: 1000 (44.000KB) | Rcvd: 2001 (84.044KB)

```
анализ: получаем полный анализ с использованием скрипта

```
nmap -sV --script vuln -oN nmapres_new.txt localhost
grep "VULNERABLE" nmapres_new.txt
```
вывод:
```
|   VULNERABLE:
|     State: LIKELY VULNERABLE
|   VULNERABLE:
|     State: VULNERABLE (Exploitable)
```
анализ: видим два флага VULNERABLE, один из которых относится к Exploitable, открывая файл видим строки
```
|       This web server contains password protected resources vulnerable to authentication bypass
|       vulnerabilities via HTTP verb tampering. This is often found in web servers that only limit access to the
|        common HTTP methods and in misconfigured .htaccess files.
```
значит есть возможность атаки через Verb Tampering. Например, если приложение требует аутентификации только для метода POST, но не для PUT или DELETE, атакующий может использовать другой метод для выполнения действий без проверки прав доступа. В данном случае логики за сервером нет, поэтому можно проигнорировать, но если поднимать сервер на этой машине, то придется обратить на это внимание.


### Шаг 4. XML и HTML-отчёт

чтобы вывод был интересней добавим ssh сервис и откроем ему порты.
```
sudo dnf install openssh-server
sudo systemctl start sshd
sudo systemctl enable sshd
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

теперь проведем еще один анализ на конкретных портах для localhost
```
mkdir -p ~/project/reports
nmap -sV -p 22,80,443,8080 --script vuln -oN ~/project/reports/nmapres_new.txt -oX ~/project/reports/nmapres_new.xml localhost
xsltproc ~/project/reports/nmapres_new.xml -o ~/project/reports/nmapres_new.html
```
вывод:
```
...
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.34 seconds
```
анализ: открыв файл мы видим уязвимость порта 22. однако эта уязвимость активна для версий OpenSSH < 10.0, а мы используем версию 10 значит все хорошо.

### Шаг 5.

```
tree
```
вывод:
```
.
├── Desktop
├── Documents
│   ├── lab_1
│   │   └── hello.py
│   ├── lab_2
│   │   ├── pygamesteel_fixed.py
│   │   └── pygamesteel.py
│   ├── lab_3
│   │   ├── exmp_targets.txt
│   │   ├── nmapres_new.txt
│   │   └── nmapres.txt
│   ├── README.md
│   └── screen
├── Downloads
│   └── screen
├── Music
├── Pictures
├── project
│   └── reports
│       ├── nmapres_new.html
│       ├── nmapres_new.txt
│       └── nmapres_new.xml
├── Public
├── screen
├── shared
├── Templates
├── test_privesc.sh
└── Videos
```
анализ: видим файлы анализа в папке `/project/reports` и наши нетронутые файлы из `/lab_3`

### Шаг 6.

```
ip addr 
```
на выводе видим сетевые карты:
```
lo; enp0s3; enp0s8; docker0
```
одна из них виртуальная, другая открыта в сеть, есть docker, возьмем local - lo

```
nmap -sn 127.0.0.1
```
вывод:
```
Host is up (0.0023s latency).
Nmap done: 1 IP address (1 host up) scanned in 0.02 seconds
```

### Шаг 7. Определите ОС, ssh, telnet и пр.

делаем проверку:
```
sudo nmap -O -sV -p 22,23 localhost
```
вывод:
```
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00013s latency).
Other addresses for localhost (not scanned): ::1

PORT   STATE  SERVICE VERSION
22/tcp open   ssh     OpenSSH 10.0 (protocol 2.0)
23/tcp closed telnet
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.92%E=4%D=4/28%OT=22%CT=23%CU=30588%PV=N%DS=0%DC=L%G=Y%TM=69F10F
OS:ED%P=x86_64-redhat-linux-gnu)
```
анализ: видим открытый нами порт 22, работающий для ssh, порт 23 - telenet закрыт, ОС не определиласьЮ, но команда поняла что мы сидим под чем-то на redhat.


### Шаг 8.

для начала добавим пустые файлы nmapres_new.txt nmapres.txt, а так же обновленный exmp_targets.txt на репозиторий.
```
git add -A
git commit -S -m "Добавили файлы для lab_3, обновили файл exmp_targets.txt"
git push origin master
```
теперь, когда файлы появились на github перенесем результаты.

```
cp ~/project/reports/nmapres_new.txt lab_3/nmapres_new.txt 
cp nmapres_new.txt nmapres.txt
```
видим в папке lab_3 появился актуальный файл анализа.

### Шаг 9. Защита файла

```
chmod 600 nmapres.txt
ls -la nmapres.txt
```
вывод:
```
-rw-------+ 1 andrew andrew 1437 Apr 28 23:13 nmapres.txt
```
анализ: теперь только andrew может менять файл

проверим от другого пользователя (smallman из Lab 02):
```
su - smallman
cat ../andrew/Documents/lab_3/nmapres.txt 
```
вывод:
```
cat: ../andrew/Documents/lab_3/nmapres.txt: Permission denied
exit
```

Добавим ACL, чтобы только группа readgroup могла читать (не писать) в файл.
```
setfacl -m g:readgroup:r nmapres.txt
getfacl nmapres.txt
```
вывод:
```
# file: nmapres.txt
# owner: andrew
# group: andrew
user::rw-
user:smallman:rw-
group::r--
group:readgroup:r--
mask::rw-
other::---
```

проверим:
```
su - smallman
cat ../andrew/Documents/lab_3/nmapres.txt    # если smallman в readgroup — OK, иначе — denied
exit
```
файл выводится, OK

Файл nmapres.txt — это карта сокровищ для злоумышленника. он видит все входные точки (открытые порты). зная точную версию сервиса и наличие уязвимости (CVE), остается только скачать готовый эксплойт. Открытый порт Telnet (23) прямо говорят о том, что защита настроена плохо, значит можно использоать более простые методы атаки.

### Шаг 10. .gitignore

```
echo "nmapres.txt" >> .gitignore
echo "nmapres_new.txt" >> .gitignore
git add .gitignore
git commit -S -m "chore: ignore nmap scan results"
```
вывод:
```
[master d291f79] chore: ignore nmap scan results
 1 file changed, 1 insertion(+)
 create mode 100644 .gitignore
```
анализ: по идее файлы должны игнорироваться, проверим:
```
git add -A
git commit -S -m "trying to commit nmapres.txt"
git push origin master 
```
файлы не обновились на github, нам повело :D

### Шаг 11 & 12

## Результаты

- Исследована утилита nmap для сканирования доменов в сети, открытых портов, анализа ОС таргетированных машин
- Исследовано nmap с использованием скриптов
- Исследована возможность записи результатов сканирования в файл и формирование итогового отчета в виде html-отчёта.
- настроены права доступа для файла `nmapres.txt`
- файл добавлен в .gitignore для избежания утечки данных.

***

## Выводы

В результате выполнения работы были исследованы возможности утилиты nmap, изучены основные методы исследования систем в сети, просканированны локальные машины и открытые сайты, полученные данные сохранены в доступный только нам файл, который мы настроили такм образом, чтобы не было утечек в сеть (данный отчет не в счет).

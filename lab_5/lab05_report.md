# Лабораторная работа №5 — Docker — контейнеризация приложений

**Автор:** Матвеичев Андрей
**Группа:** М03-503
**Дата:** 2026-04-29

***

## Цель работы

Данная лабораторная работа посвящена изучению Docker и как с ним работать. Эта лабораторная работа послужит подпоркой для старта в выявлении и определении уязвимостей на уровне сканирования контейнеров при сборке приложений.

***

## Ход выполнения

### Шаг 0. 

Обновим систему и сделаем pull для репозитория

```
sudo dnf update; sudo dnf upgrade
git pull origin master
```
можно работать.

### Шаг 1. Подготовка docker

Контейнер — изолированная среда для запуска приложения, которая включает код, зависимости и конфигурацию. В отличие от виртуальной машины, контейнер не содержит собственного ядра ОС — он использует ядро хост-системы.

Установим Docker с buildkit:
```
sudo dnf install -y docker docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```
проверим
```
docker --version
docker run hello-world
```
вывод:
```
Docker version 29.4.0, build 1.fc43

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```
docker настроен и готов к работе.

Скопируем данные lab05 в нашу папку.
```
cp -r ~/path_to_example/lab05 ~/Documents/lab_5 
```
сделаем commit, обновим данные
```
git add -A
git commit -S -m "Начали 5 лабу"
```

### Шаг 2. Изучение базовых команд.

выполним:
```
cd source
docker buildx build -t hello-appsec-world .
docker run hello-appsec-world
docker run --rm -it hello-appsec-world
```
на выводе видим build процесс. система собираем нужные pip модули. Выдает WARNING о том, что мы запускаем программу с root аккаунта.
после этого программа выводит:
```
Hello AppSec World!
Python version: 3.11.15 (main, Apr 22 2026, 02:06:58) [GCC 14.2.0]
Platform: linux
Current time: 2026-04-29 10:38:22
Hello AppSec World!
Python version: 3.11.15 (main, Apr 22 2026, 02:06:58) [GCC 14.2.0]
Platform: linux
Current time: 2026-04-29 10:38:24
```
как видно `build` собирает образ из текущей директории и тегирует его именем `hello-appsec-world`, `run` - создает и запускает контейнер `run --rm -it` запускает контейнер интерактивно, после чего удаляет.

далее выполним:
```
docker save -o hello.tar hello-appsec-world
```
(сохраняет слои образа в tar-архив)
```
docker load -i hello.tar
```
(загружает образ - `Loaded image: hello-appsec-world:latest`) 
```
docker load -i image.tar
```
ошибка: `open image.tar: no such file or directory`, название указано неправильно и образ не загрузился.

### Шаг 3.
```
cat Dockerfile
cat requirements.txt
```
видим
- базовый образ: python:3.11-slim. официальный образ, пиннинг версии присутствует (тег 3.11-slim).
- multi-stage build: да. первый этап собирает зависимости (wheels), второй — копирует только готовые пакеты. Это уменьшает размер образа и исключает попадание компиляторов в итоговый контейнер, что снижает вектор атак.
- Инструкция USER: отсутствует. приложение запускается от root, что критически небезопасно.
- копирование файлов: используется точечное копирование (COPY requirements.txt ., COPY hello.py .), а не слепое COPY . .., что правильно.
- .dockerignore: отсутствует. без него есть риск скопировать секреты из локальной директории (например, .env).
- секреты: В самом Dockerfile пароли не захардкожены.
- пиннинг зависимостей: В примере requirements.txt версии не зафиксированы.

### Шаг 4. .dockerignore
```
vi .dockerignore
```
сравним образы с помощью команды
```
docker images | grep hello-appsec-world
```
видим 
```
# до
hello-appsec-world:latest   97a08cc2fc11        213MB           53MB   U    
# после
hello-appsec-world-2:latest   7dfe1c01f027        213MB           53MB   U    
```
размер файла не изменился, так как мы в него особо ничего и не добавляли до этого, gitignore в данном случае это хорошая практика на будущее.

без .dockerignore контекст сборки передает демону Docker всю директорию целиком. туда могут попасть папки .git (история коммитов), __pycache__ (мусор), и файлы с секретами .env. это не только раздувает размер образа, но и может привести к утечке критичных данных.

### Шаг 5. Свой python скрипт

Для простоты возьмем файл из 2 лабы.
```
cp ../../lab_2/pygamesteel_fixed.py pygamesteel_from_lab_2.py
```
нам придется сделать заглушку дял экрана, так как docker не видит его. Так же добавим выводы в терминал для наглядности:
```python
import pygame
import os

# Фикс для запуска в Docker без X-сервера (монитора)
os.environ['SDL_VIDEODRIVER'] = 'dummy'

pygame.init()

screen_width = 800
screen_height = 600
window_size = (screen_width, screen_height)
screen = pygame.display.set_mode(window_size) 

bg_color = (255, 255, 255)
font = pygame.font.SysFont(None, 75)
text = font.render("Hello appsec world*", True, (0, 255, 0))
text_rect = text.get_rect()
text_rect.center = (400, 300)

# Для Docker сделаем ограничение: выполним 100 итераций и выйдем
# Иначе контейнер будет крутиться вечно
running_count = 0
running = True
while running and running_count < 100:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(bg_color)
    screen.blit(text, text_rect)
    pygame.display.flip() 
    running_count += 1
    if running_count % 20 == 0:
        print(f"Frame {running_count} rendered successfully")

print("Pygame work finished successfully!")
pygame.quit()
```

Добавим pygame в requirements:
```
pygame==2.5.2
```

Обновим Dockerfile:
```
# Этап 1: Сборка (Builder)
FROM python:3.11-slim AS builder
WORKDIR /app

# Устанавливаем системные зависимости для сборки pygame
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Собираем wheel-пакеты
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-slim
WORKDIR /app

# Нам нужны только базовые библиотеки SDL2 для запуска (без gcc)
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем собранные пакеты
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY pygamesteel_from_lab_2.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "pygamesteel_from_lab_2.py"]
```
делаем commit и переходим к следующему шагу:
```
git add -A
git commit -S -m "Обновили Dockerfile для работы с файлом из 2 лабы, обновили сам скрипт pygamesteel_from_lab_2.py для совместимости с docker"
```

### Шаг 6. Сохранение в файлы
```
docker buildx build -t hello-appsec-world .
```
build прошел успешно за 461.6s, тестируем:
```
docker run hello-appsec-world
```
вывод:
```
pygame 2.5.2 (SDL 2.28.2, Python 3.11.15)
Hello from the pygame community. https://www.pygame.org/contribute.html
ALSA lib confmisc.c:855:(parse_card) cannot find card '0'
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_card_inum returned error: No such file or directory
ALSA lib confmisc.c:422:(snd_func_concat) error evaluating strings
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_concat returned error: No such file or directory
ALSA lib confmisc.c:1342:(snd_func_refer) error evaluating name
ALSA lib conf.c:5205:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
ALSA lib conf.c:5728:(snd_config_expand) Evaluate error: No such file or directory
ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) Unknown PCM default
Frame 20 rendered successfully
Frame 40 rendered successfully
Frame 60 rendered successfully
Frame 80 rendered successfully
Frame 100 rendered successfully
Pygame work finished successfully!
```
как видно, не без ошибок, но программа работает, выводит расставленные маркеры и завершает работу.
сохраним файл:
```
docker save -o hello_your_project.tar hello-appsec-world
```

попробуйем загрузить из файла:
```
docker load -i hello_your_project.tar
docker run hello-appsec-world
```
файл успешно выполняется, мы пропускаем долгий build процесс.

К сожалению, image.tar в репозитории нет, поэтому сравним с hello.tar, собранным нами ранее.
```
docker load -i hello.tar
docker run hello-appsec-world
```
видим вывод:
```
Hello AppSec World!
Python version: 3.11.15 (main, Apr 22 2026, 02:06:58) [GCC 14.2.0]
Platform: linux
Current time: 2026-04-29 12:05:10
```
вывод с сохраненного hello.tar

хэш суммы проектов:
```
sha256sum hello.tar
sha256sum hello_your_project.tar
```
вывод:
```
cfd0958fd976f229b3d22af932cbdf334bf318593b7c93e6031d76e06b40eeb0  hello.tar
7659dcbb6524fb2f0b9375485ef3d2132dfea545d9b24e4d0866caeb390c9b17  hello_your_project.tar
```
видно, то файлы отличаются.


### Шаг 7. еще библиотеки

добавим новую библиотеку
```
requests==2.28.1
```

проверим добавленную библиотеку requests, добавив в файл:
```
import requests

response = requests.get('https://about.google/?fg=1')
print(response.status_code) # 200 означает успешный запрос
print(response.text) # Выводит текстовое содержимое ответа
```

### Шаг 8. rebuild и commit
коммитим измененния:
```
git add -A
git commit -S -m "обновили файл, добавив библиотеку requests, обновили requirements"
```
повторяем сборку и запускаем:
```
docker buildx build -t hello-appsec-world .
docker run hello-appsec-world
docker save -o hello_your_project.tar hello-appsec-world
```
видим вывод:
```
pygame 2.5.2 (SDL 2.28.2, Python 3.11.15)
Hello from the pygame community. https://www.pygame.org/contribute.html
200
<!doctype html>
<html class="page" dir.......
```
библиотека requests установилась и работает.

делаем commit:
```
git add -A
git commit -S -m "Сохранили новый образ в файл hello_your_project.tar"
```

### Шаг 9. История и слои
Посмотрим слои образа:
```
docker history hello-appsec-world
```
вывод:
```
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
d457a076e7af   15 minutes ago   CMD ["python" "pygamesteel_from_lab_2.py"]      0B        buildkit.dockerfile.v0
<missing>      15 minutes ago   ENV PYTHONUNBUFFERED=1                          0B        buildkit.dockerfile.v0
<missing>      15 minutes ago   COPY pygamesteel_from_lab_2.py . # buildkit     4.1kB     buildkit.dockerfile.v0
<missing>      15 minutes ago   RUN /bin/sh -c pip install --no-index --find…   58.3MB    buildkit.dockerfile.v0
<missing>      15 minutes ago   COPY requirements.txt . # buildkit              4.1kB     buildkit.dockerfile.v0
<missing>      40 minutes ago   COPY /wheels /wheels # buildkit                 15MB      buildkit.dockerfile.v0
<missing>      43 minutes ago   RUN /bin/sh -c apt-get update && apt-get ins…   360MB     buildkit.dockerfile.v0
<missing>      46 minutes ago   WORKDIR /app                                    0B        buildkit.dockerfile.v0
<missing>      7 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   20.5kB    buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   47MB      buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PYTHON_VERSION=3.11.15                      0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV GPG_KEY=A035C8C19219BA821ECEA86B64E628F8…   0B        buildkit.dockerfile.v0
<missing>      7 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   5.56MB    buildkit.dockerfile.v0
<missing>      7 days ago       ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      7 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      8 days ago       # debian.sh --arch 'amd64' out/ 'trixie' '@1…   86.4MB    debuerreotype 0.17
```
видим 18 слоев. размером от 0 байт до 360MB (когда скачивали pygame). 

Посмотрим размер образа:
```
docker images hello-appsec-world
```
вывод:
```
IMAGE                       ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-appsec-world:latest   d457a076e7af        778MB          206MB    U   
```
cамые тяжелые слои это базовая ОС и установка зависимостей. gереход на multi-stage build сильно сокращает размер, так как в финальный образ не переносятся кэши пакетного менеджера и утилиты сборки (компиляторы), которые нужны только на этапе установки библиотек.

### Шаг 10. Пользователь

```
docker run --rm hello-appsec-world whoami
docker run --rm hello-appsec-world id
```
вывод:
```
root
uid=0(root) gid=0(root) groups=0(root)
```
исправим добавив в Dockerfile строки
```
# Создаем непривилегированного пользователя
RUN useradd -m dashboard_user

# Переключаемся на пользователя
USER dashboard_user
```

ребилд и проверка:
```
docker buildx build -t hello-appsec-world .
docker run --rm hello-appsec-world whoami
docker run --rm hello-appsec-world id
```
вывод:
```
dashboard_user
uid=1000(dashboard_user) gid=1000(dashboard_user) groups=1000(dashboard_user)
```
теперь запускается от имени dashboard_user.

можно сохранить:
```
docker save -o hello_your_project.tar hello-appsec-world
```
и закоммитить:
```
git add -A
git commit -S -m "Сохранили новый образ c обновленными правами доступа"
```

### Шаг 11.

```
docker login
```
- зарегались
```
docker tag hello-appsec-world andrewbanana/hello-appsec-world
docker push andrewbanana/hello-appsec-world
```
- запушили
```
docker inspect andrewbanana/hello-appsec-world
```
- посмотрели на данные
```
docker container create --name first hello-appsec-world # выпишите id контейнера
```
вывод: `ef133f645338d8500b164ce1bb00450d33431debc5cee939d9b1801211709cb3`
```
docker image pull geminishkv/hello-appsec-world
docker inspect geminishkvdev/hello-appsec-world
```
вывод: 
```
docker inspect geminishkvdev/hello-appsec-world
Using default tag: latest
Error response from daemon: pull access denied for geminishkv/hello-appsec-world, repository does not exist or may require 'docker login'
[]
error: no such object: geminishkvdev/hello-appsec-world
```
так как у нас нет доступа, то выдает ошибку
```
docker container create --name second hello-appsec-world
```
вывод: `dc982a74c31579eb7a16fe22c7f01bcf241b8553764598d6a9c07981da6e2cab`

### Шаг 12. контейнер Ubuntu
запустим
```
docker container run -it --rm ubuntu /bin/bash
```
Мы оказались внутри контейнера, попробуем команды:
```
whoami                    # от какого пользователя?
```
вывод: `root` - так как мы в корне docker контейне, это root внутри контейнера, изолированный от хоста.
```
id                        # uid, gid
```
вывод: `uid=0(root) gid=0(root) groups=0(root)` - мы все еще root
```
ps aux                    # какие процессы видны? (только свои — pid namespace)
```
вывод: 
```
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0   4596  3992 pts/0    Ss   13:30   0:00 /bin/bash
root          12  0.0  0.1   7896  4076 pts/0    R+   13:32   0:00 ps aux
```
видно процессы внутри контейнера.

```
cat /etc/os-release       # какая ОС внутри?
```
вывод:
```
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo
```
видим послоеднюю версию Ubuntu.

```
hostname                  # имя хоста (uts namespace)
```
вывод: `99e9932e943e` - слйчайное id хоста

```
ls /proc/1/ns/            # namespace-файлы процесса PID 1
```
вывод: `cgroup  ipc  mnt  net  pid  pid_for_children  time  time_for_children  user  uts`
видим файлы-дескрипторы для каждого пространства имен (mnt, net, pid, uts и т.д.), которые ядро Linux выделило для изоляции этого процесса.

```
exit
```
вышли

### Шаг 13. ресурсные лимиты контейнера

Запустим с лимитом 64 MB RAM:
```
docker run -d --name stress-test --memory=64m --cpus=0.5 ubuntu sleep 300
```
вывод: `a1f19334571e379302a3ed51ecbeaf69daf565ef4fd4bb4009c637aac4f043c2` означает успешное выполнение


проверим лимиты:
```
docker stats stress-test --no-stream
```
вывод:
```
CONTAINER ID   NAME          CPU %     MEM USAGE / LIMIT   MEM %     NET I/O         BLOCK I/O   PIDS
a1f19334571e   stress-test   0.00%     404KiB / 64MiB      0.62%     1.05kB / 126B   0B / 0B     1
```
видим что запас памяти достаточный даже для такого небольшого количества памяти
почистим:

```
docker rm -f stress-test
```
ограничения задаются через механизм cgroups. если приложение (или вредоносный код) внутри stress-test попытается выделить больше 64MB памяти, ядро Linux вызовет механизм OOM-Killer (Out of Memory) и принудительно "убьет" процесс контейнера. ограничивать ресурсы нужно для того, чтобы один скомпрометированный или зависший контейнер не забрал всю память и процессорное время хост-машины, устроив Denial of Service (DoS) для всех остальных сервисов.

### Шаг 14. Список контейнеров

чтобы посмотреть контейнеры:
```
docker ps -a
```
вывод:
```
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS                      PORTS     NAMES
dc982a74c315   hello-appsec-world   "python pygamesteel_…"   12 minutes ago   Created                               second
ef133f645338   hello-appsec-world   "python pygamesteel_…"   14 minutes ago   Created                               first
```

### Шаг 15. Docker-сеть

создадим сеть в корне lab_5
```
docker network create lab05-net
docker network ls
```
вывод:
```
bde1566b6f141aee69ffeac06d152898acdb33c6f5846e6429d3be0a3bcf7507
NETWORK ID     NAME        DRIVER    SCOPE
88e57358966c   bridge      bridge    local
017d6f637b16   host        host      local
bde1566b6f14   lab05-net   bridge    local
e8b69878b2b7   none        null      local
```
Запустим два контейнера в одной сети:
```
docker run -d --name net-a --network lab05-net nginx
docker run -it --rm --network lab05-net ubuntu bash -c "apt update && apt install -y iputils-ping && ping -c 3 net-a"
```
после установки вывод:
```
PING net-a (172.18.0.2) 56(84) bytes of data.
64 bytes from net-a.lab05-net (172.18.0.2): icmp_seq=1 ttl=64 time=0.230 ms
64 bytes from net-a.lab05-net (172.18.0.2): icmp_seq=2 ttl=64 time=0.198 ms
64 bytes from net-a.lab05-net (172.18.0.2): icmp_seq=3 ttl=64 time=4.74 ms

--- net-a ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2118ms
rtt min/avg/max/mdev = 0.198/1.723/4.743/2.135 ms
```

контейнеры находят друг друга по имени благодаря встроенному DNS-серверу Docker (он работает на адресе 127.0.0.11 внутри пользовательских сетей типа bridge). когда мы пингуем net-a, DNS Docker'а перехватывает запрос и возвращает внутренний IP-адрес этого контейнера. в сети по умолчанию (которая просто называется bridge) этот DNS не работает для имен контейнеров, поэтому всегда нужно создавать свою сеть (как lab05-net).

почистим:
```
docker rm -f net-a
docker network rm lab05-net
```

### Шаг 16. Compose
запустим compose
```
docker compose up --build
```
compose выполнился успешно.

### Шаг 17. Проверка в браузере
переходим на http://localhost:8000 в браузере. Видно, что приложение работает. Выводится html страница с разноцветным текстом "hello appsec world" при этом в терминале появляются красивые радужные выводы :D

```
curl -i http://localhost:8000
```
выдает вормат html страницы.

### Шаг 18. Почистим ресурсы за собой
```
docker ps -a
docker ps -q
docker images

docker ps -q | xargs docker stop
docker compose down
```
вывод:
```
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS                      PORTS                                         NAMES
9efd64d89538   lab_5-client         "python client.py"       3 minutes ago    Exited (0) 35 seconds ago                                                 lab_5-client-1
8dac03043327   lab_5-server         "python app.py"          3 minutes ago    Up 3 minutes                0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   lab_5-server-1
dc982a74c315   hello-appsec-world   "python pygamesteel_…"   24 minutes ago   Created                                                                   second
ef133f645338   hello-appsec-world   "python pygamesteel_…"   26 minutes ago   Created                                                                   first
e6e33b8fec1f   6007170b09fd         "python pygamesteel_…"   58 minutes ago   Exited (0) 58 minutes ago                                                 determined_kowalevski
8dac03043327
                                                                                                                                       i Info →   U  In Use
IMAGE                                    ID             DISK USAGE   CONTENT SIZE   EXTRA
andrewbanana/hello-appsec-world:latest   758bb16e1d50        778MB          206MB    U   
hello-appsec-world:latest                758bb16e1d50        778MB          206MB    U   
lab_5-client:latest                      091a5d175903        205MB         50.8MB    U   
lab_5-server:latest                      ccf8ff3decc7        209MB         51.8MB    U   
nginx:latest                             6e23479198b9        240MB         65.8MB        
ubuntu:latest                            c4a8d5503dfb        117MB         31.7MB        
8dac03043327
WARN[0000] /home/andrew/Documents/lab_5/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] down 3/3
 ✔ Container lab_5-client-1 Removed                                                                                                                                             0.1s
 ✔ Container lab_5-server-1 Removed                                                                                                                                             0.1s
 ✔ Network lab_5_app_net    Removed    
```
все успешно удалено.

### Шаг 19. доработа docker compose

добавим в файл строки:
```
  etc:
    build: ./source
    networks:
      - app_net
    command: python pygamesteel_from_lab_2.py
```

проверим:
```
docker compose up --build
```
видим как выводится наш скрипт на python вместе с предыдушей программой

почистим все и закоммитим:
```
docker ps -q | xargs docker stop
docker compose down

git add -A
git commit -S -m "Поправили compose для работы с нашей программой."
```

### Шаг 20 & 21.

добавим tar файлы в .gitignore, удалим их из коммитов:
```
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch lab_5/source/hello_your_project.tar" \
  --prune-empty --tag-name-filter cat -- --all
  
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch lab_5/source/hello.tar" \
  --prune-empty --tag-name-filter cat -- --all
```

```
git push origin master
git log
```
видим что все коммиты запушились и все верно. Обновляем README.


## Результаты
- Мы изучили основные команды docker
- Научились добавлять файлы и настаивать файлы, которые добавляются и игнорируются компилятором
- Научились запускать Docker от имени неавторизованного root пользователя.
- Изучили идею ограничения памяти для процесса
- Изучили сети в Docker
- Посмотрели Composer как способ запуска нескольких проектов внутри одной сети
- Научились смотреть работающие контейнеры и контроллировать их в удаленных репозиториях

***

## Выводы

В результате выполнения данной работы мы изучили Docker и научились основным методам работы с контейнерами.

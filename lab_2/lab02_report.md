# Лабораторная работа №2 — *nix — права доступа, управление процессами

**Автор:** Матвеичев Андрей
**Группа:** М03-503
**Дата:** 2026-04-28

***

## Цель работы

Данная лабораторная работа посвящена изучению *nix машин и как они работают, позволяет приобрести навыки для работы с терминалом/ консолью и приобрести знания по работе ОС. В лабораторной работе описываются материалы по командам, скриптам и подключаемым приложениям.
***

## Ход выполнения

### Шаг 0. 

```
sudo dnf update; sudo dnf upgrade
```
обновим систему и начнем выполнение работы

### Шаг 1. Информация о системе

#### команда who:
```
who | wc -l
```
вывод: `2`

анализ:

команда `who` показывает текущих пользователей, а  `wc -l` используется как пайпер для подсчета количества строк (параметр `-l`). В итоге мы видим что на данный момент подключены 2 пользователя.

#### команда id:
```
id
```
вывод: `uid=1000(andrew) gid=1000(andrew) groups=1000(andrew),10(wheel),969(docker) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023`

анализ:

id позволяет получить информацию о пользователе; без доп. аргументов она укажет текущего пользователя. Мы видим что uid - User Identifier; gid - Group Identifier; groups = 1000(andrew) - текущий пользователь. мы так же видим что у этого пользователя есть доступ к wheel, docker. Дальнейший вывод показывает security context; что пользователь и роль не выражены, а домен имеет доступ к MLS s0-s0; пользователю доступны категории c0-c1023

#### команда whoami:
```
whoami
```
вывод: andrew

анализ: выдает имя пользователя, то есть меня (andrew)

#### команда  hostnamectl:
```
hostnamectl
```
вывод:
```
  Transient hostname: fedora
     Static hostname: (unset)                              
           Icon name: computer-vm
             Chassis: vm 🖴
          Machine ID: afc6999a03954393a2a16bfd7e852824
             Boot ID: a105f6e939c5404894b12fa1817051dc
      Virtualization: oracle
    Operating System: Fedora Linux 43 (Workstation Edition)
         CPE OS Name: cpe:/o:fedoraproject:fedora:43
      OS Support End: Wed 2026-12-02
OS Support Remaining: 7month 4d
              Kernel: Linux 6.19.12-200.fc43.x86_64
        Architecture: x86-64
     Hardware Vendor: innotek GmbH
      Hardware Model: VirtualBox
    Hardware Version: 1.2
    Firmware Version: VirtualBox
       Firmware Date: Fri 2006-12-01
        Firmware Age: 19y 4month 3w 6d  
```
анализ:

команда выдает множество параметров машины, мы видим что ОС - fedora. Система определила что мы работаем в виртуальной среде на базе oracle, видим версию образа, версии машины, а так же время обновления firmware, сколько ему лет и время окончания поддержки. 19 лет это большой срок и если бы это было развернутое решение то нам бы пришлось точно проверить все права доступа и убедиться в соответствии системы новым нормам. 

### Шаг 2. Файловая система

#### команда `tree`
вывод:
```
.
├── Desktop
├── Documents
│   ├── lab_1
│   │   └── hello.py
│   └── README.md
├── Downloads
├── Music
├── Pictures
├── Public
├── Templates
└── Videos
```
Мы видим стандартную библиотеку пользователя с разделением папок на категории, видно так же что github был инициализирован в папке Documents. надо было конечно сделать отдельную папку для удобства, но поскольку данная машина нужна для обучения, то не страшно.

#### команда `ls`:
```
la -a
```
анализ:

параметр `-a` выводит все файлы и папки в дирректории, в том числе мы видим скрытые файлы (начинаются с `.`), кроме того видно вспомогательные папки для навигации `.` и `..`, указывающие на текущую папку и папку выше по иерархии.

```
ls -l
```
анализ:

параметр `-l` выводит файлы в виде списка с временем изменения, указанием прав доступа и пользователем который в последний раз работал с папкой.

### Шаг 3. Определение типа файловой системы

#### команда file
```
sudo file -s /dev/sda1
```
вывод: `/dev/sda1: data`

анализ: тип данных data показывает что раздел используется для записи файлов

#### команда df
```
df -T /dev/sda1
```
вывод:
```
Filesystem     Type     1K-blocks  Used Available Use% Mounted on
devtmpfs       devtmpfs   1973204     0   1973204   0% /dev
```
анализ: видим тип файловой системы devtmpfs, с 1973204 доступными блоками памяти, сейчас использован на 0% и закреплен в /dev.

### Шаг 4 Обнаружение файлов

Выполним последовательно команды и рассмотрим что они выводят
```
which vi
```
вывод: `vi=vim`
анализ: `which`находит и отображает полный путь к исполняемым файлам => vi ссылается на vim.
```
locate hello.py
```
вывод: `/home/andrew/Documents/lab_1/hello.py` 
анализ: `locate` ищет файлы; созданный в прошлой лабораторной файл `hello.py` лежит в папке lab_1/hello.py
```
sudo updatedb
```
вывод: 
анализ: выполняет полное обновление базы данных, перебирает все доступные файлы (параметр -v покажет прогресс, значительно замедляет выполнение команды)
```
locate hello
```
частичный вывод:
```
/home/andrew/Documents/lab_1/hello.py
/usr/lib/grub/i386-efi/hello.mod
/usr/lib/grub/i386-pc/hello.mod
/usr/lib/grub/x86_64-efi/hello.mod
/usr/lib64/python3.14/__hello__.py
/usr/lib64/python3.14/__pycache__/__hello__.cpython-314.opt-1.pyc
/usr/lib64/python3.14/__pycache__/__hello__.cpython-314.opt-2.pyc
/usr/lib64/python3.14/__pycache__/__hello__.cpython-314.pyc
...
```
анализ: команда находит все файлы с строчкой `hello` в названии, видно временные файлы и артефакты выполнения
```
touch screen
```
вывод:
анализ: создался файл `screen`
```
find ~ -name screen
```
вывод:
```
/home/andrew/.oh-my-zsh/plugins/screen
/home/andrew/screen
```
анализ: `find` выполняет поиск файлов и каталогов по множеству критериев, в данном случае с параметром `-name` находит файл по имени, который мы видим в корневой директории.
```
locate screen
```
частичный вывод:
```
/home/andrew/.cache/gnome-software/icons/ac4dd64b5533b3b300eddfe4925e825f44dc3fc6-com.github.vkohaupt.vokoscreenNG.png
/home/andrew/.cache/gnome-software/icons/f4df565f6efb0cc08a1b9c151ba5737bebc52ea7-com.dec05eba.gpu_screen_recorder.png
/home/andrew/.local/lib/python3.14/site-packages/rich/screen.py
/home/andrew/.local/lib/python3.14/site-packages/rich/__pycache__/screen.cpython-314.pyc
/home/andrew/.oh-my-zsh/plugins/screen
/home/andrew/.oh-my-zsh/plugins/screen/README.md
/home/andrew/.oh-my-zsh/plugins/screen/screen.plugin.zsh
/usr/bin/xdg-screensaver
/usr/include/linux/screen_info.h
...
```
анализ: команда ищет файлы со строкой `screen` в названии, видно, что она ищет так же файлы в скрытый папках. но не находит наш файл в корне.
```
sudo updatedb
```
вывод:
анализ: обновили базу данных

```
locate screen
```
вывод:
```
/home/andrew/screen
/home/andrew/.cache/gnome-software/icons/ac4dd64b5533b3b300eddfe4925e825f44dc3fc6-com.github.vkohaupt.vokoscreenNG.png
/home/andrew/.cache/gnome-software/icons/f4df565f6efb0cc08a1b9c151ba5737bebc52ea7-com.dec05eba.gpu_screen_recorder.png
...
```
анализ: после обновления базы данных файл появился в поиске

### Шаг 5. pygame

установим нужный модуль:

```
sudo dnf install python3-pygame
```

создадим файл `pygamesteel.py`. 

```
touch pygamesteel.py
```
добавим в него код:
```
import pygame
pygame.init()

# Устанавливаем размеры окна
screen_width = 800
screen_height = 600
window_size = (screen_width, screen_height)
pygame.display.set_mode(window_size) # Создаем окно

# Задаем цвет фона
bg_color = (255, 255, 255)
pygame.draw.rect(screen, bg_color, [0, 0, screen_width, screen_height], 1)

# Выводим текст на экран
font = pygame.font.SysFont(None, 75)
text = font.render("Hello appsec world*", True, (0, 255, 0))
text_rect = text.get_rect()
text_rect.center = (400, 300)
screen.blit(text, text_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
pygame.display.flip() # Обновляем экран
```

запустим
```
LIBGL_ALWAYS_SOFTWARE=1 python3 pygamesteel.py
```
выдает ошибки, исправим их в новой копии файла `pygamesteel_fixed.py`:
```
screen_width = 800
screen_height = 600
window_size = (screen_width, screen_height)
# добавили переменную 'screen'
screen = pygame.display.set_mode(window_size)

# Задаем цвет фона
bg_color = (255, 255, 255)

# Подготовка текста
font = pygame.font.SysFont(None, 75)
text = font.render("Hello appsec world*", True, (0, 255, 0))
text_rect = text.get_rect()
text_rect.center = (400, 300)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # отрисовка фона и обновление экрана перенесены в цикл 
    screen.fill(bg_color) # Очищаем экран белым цветом
    screen.blit(text, text_rect) # Рисуем текст
    pygame.display.flip()

pygame.quit()
```
данный файл запускается и создает окно с текстом

### Шаг 6. commit
закоммитим данные изменения на github.

```
git config pull.rebase true
git pull https://github.com/B-a-n-a-n/appsec_labs.git master
git add -A
git commit -S -m "started lab 2 and added new file to /lab_2"
git push origin master
```

после обновления файла:
```
git add -A
git commit -S -m "добавили исправления в новом файле pygamesteel_fixed.py"
git push origin master
```

вывод:
```
Total 4 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (1/1), completed with 1 local object.
To github.com:B-a-n-a-n/appsec_labs.git
   52617c8..f258908  master -> master
```

### Шаг 7. работа с пользователями

```
groups
```
вывод: `andrew wheel docker`
анализ: видно 3 группы; andrew - локальный пользователь,  wheel - для управлением пользователями, docker - для утилиты docker.

```
sudo useradd smallman
```
вывод:
анализ: добавили пользователя :)

```
sudo userdel smallman -rf
```
вывод:
анализ: удалили пользователя с параметром -rf (указывает  то нужно удалять каталоги и делает force remove) :(

```
sudo useradd smallman
```
вывод:
анализ: добавили пользователя назад :3

```
sudo passwd smallman
```
вывод:
```
BAD PASSWORD: The password is shorter than 8 characters
Retype new password: 
passwd: password updated successfully
```
анализ: дали пользователю пароль `beer`, пароль короткий, поэтому нас обругали, хотя немного пива в жизни smallman это хорошо.

```
sudo usermod smallman -c 'Hach Hachov Hacherovich,239,45-67,499-239-45-33'
```
вывод: 
анализ: добавили комментарий к пользователю с именем и номером телефона

```
sudo passwd smallman
```
вывод:
```
New password: 
Retype new password: 
passwd: password updated successfully
```
анализ: обновили пароль пользователя на новый `more beer`. команда не ругается, значит больше пива - лучше.

```
id smallman
```
вывод: `uid=1001(smallman) gid=1001(smallman) groups=1001(smallman)`
анализ: вывели параметры нового пользователя, видим что его отнесло к новому id 1001. 

```
sudo  groupadd -g 1500 readgroup
```
вывод:
анализ: добавили новую группу 1500 readgroup

```
sudo usermod -aG readgroup smallman
```
вывод:
анализ: добавили пользователя smallman к этой группе

```
chmod 666 screen
```
вывод:
анализ: обновили права доступа к файлу `screen`, созданному изначально.

### Шаг 8. 

выведем группу прав `screen`:
```
ls -l screen
```
вывод: `-rw-rw-rw-. 1 andrew andrew 0 Apr 28 18:52 screen`
анализ: видно, что файл доступен для изменения и чтения для andrew.

чтобы пользователь smallman мог получить доступ через группу readgroup, нам нужно сделать эту группу владельцем файла. через команду `readgroup`:

```
sudo chgrp readgroup screen
```

проверим:

```
id smallman
sudo -u smallman cat screen
```
вывод: `uid=1001(smallman) gid=1001(smallman) groups=1001(smallman),1500(readgroup)`
анализ: как видим, smallman теперь относится к нужной группе, при этом не возникло ошибки выполнения фторой команды а значит все настроено верно.

### Шаг 9. POSIX ACL

```
touch nmapres.txt
setfacl -m u:smallman:rw nmapres.txt
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
other::r--
```
мы создали новый файл от имени andrew, доступный для чтения и изменения пользователем smallman, а так же всем находящимся в группе readgroup.

### Шаг 10. commit

Добавим изменения в репозиторий

```
git add -A
git commit -S -m "Добавили файлы screen и nmapres.txt в репозиторий для дальнейших лабораторных."
git push origin master
```
вывод:
```
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 1.11 KiB | 1.11 MiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To github.com:B-a-n-a-n/appsec_labs.git
   f258908..bf36de4  master -> master
```
успешно.

### Шаг 11. группы
```
cat /etc/group
```
вывод:
```
root:x:0:
sys:x:3:
adm:x:4:
tty:x:5:
disk:x:6:
lp:x:7:
mem:x:8:
kmem:x:9:
wheel:x:10:andrew
cdrom:x:11:
mail:x:12:
man:x:15:
dialout:x:18:
floppy:x:19:
games:x:20:
utmp:x:22:
tape:x:33:
kvm:x:36:qemu
video:x:39:
ftp:x:50:
lock:x:54:
audio:x:63:
users:x:100:
clock:x:103:
input:x:104:
render:x:105:
sgx:x:106:
nobody:x:65534:
bin:x:1:
daemon:x:2:
dbus:x:81:
tss:x:59:clevis
systemd-journal:x:190:
systemd-oom:x:999:
polkitd:x:114:
systemd-coredump:x:998:
systemd-timesync:x:997:
chrony:x:996:
systemd-network:x:192:
systemd-resolve:x:193:
avahi:x:70:
printadmin:x:995:
qat:x:994:
unbound:x:993:
clevis:x:992:
usbmuxd:x:113:
utempter:x:35:
gluster:x:991:
dip:x:40:
qemu:x:107:
apache:x:48:
openvpn:x:990:
nm-openvpn:x:989:
libvirt:x:988:
abrt:x:173:
wsdd:x:987:
nm-openconnect:x:986:
rtkit:x:985:
pipewire:x:984:
brlapi:x:983:
flatpak:x:982:
geoclue:x:981:
sssd:x:980:
colord:x:979:
gdm:x:42:
rpc:x:32:
dnsmasq:x:978:
rpcuser:x:29:
gnome-initial-setup:x:977:
gnome-remote-desktop:x:976:
vboxsf:x:975:
sshd:x:74:
passim:x:973:
tcpdump:x:72:
power:x:972:
plocate:x:971:
gamemode:x:970:
andrew:x:1000:
docker:x:969:andrew
vboxdrmipc:x:968:
smallman:x:1001:
readgroup:x:1500:smallman
```

права:
```
ls -ld / /etc /home /root /var
```
вывод:
```
dr-xr-xr-x. 1 root root  170 Oct 23  2025 /
drwxr-xr-x. 1 root root 5012 Apr 28 18:46 /etc
drwxr-xr-x. 1 root root   28 Apr 28 18:38 /home
dr-xr-x---. 1 root root  156 Apr 28 15:59 /root
drwxr-xr-x. 1 root root  200 Apr 22 14:54 /var
```
### Шаг 12
воспользуемся ls:
```
ls -l
```
вывод:
```
total 4
drwxr-xr-x. 1 andrew andrew      16 Apr 22 22:55 lab_1
drwxr-xr-x. 1 andrew andrew      68 Apr 28 18:27 lab_2
-rw-rw-r--+ 1 andrew andrew       0 Apr 28 18:58 nmapres.txt
-rw-r--r--. 1 andrew andrew    1182 Apr 28 18:15 README.md
-rw-rw-rw-. 1 andrew readgroup    0 Apr 28 18:52 screen
```
видим права всех папок в репозитории

### Шаг 13
добавим файл `test_privesc.sh` и сделаем его исполняемым. 
```
echo 'echo "Running as $(whoami)"' > test_privesc.sh
chmod +x test_privesc.sh
sudo chown root test_privesc.sh
sudo chmod u+s test_privesc.sh
```

SUID заставляет программу запускаться с правами владельца файла, а не того, кто её запустил. Если в такой программе есть уязвимость (например, возможность выполнить системную команду), злоумышленник может вылезти из нее и получить полный контроль над системой.

### Шаг 14
создадим директорию shared/ с правами 770 и sticky bit (chmod 1770):
```
mkdir shared
sudo chmod 1770 shared
sudo chgrp readgroup shared
```
создадим файлы от имени andrew и smallman:
```
sudo -u andrew touch andrew_file.txt
sudo -u smallman touch smallman_file.txt
```
попробуем удалить от имени smallman:
```
sudo -u smallman rm andrew_file.txt
```
вывод: `rm: cannot remove 'andrew_file.txt': Operation not permitted`
анализ: не получилось, так как нет прав

```
sudo -u smallman rm smallman_file.txt
```
ошибки нет, файл удалился, так как у нас были права.

разница 770 и 1770:
770: Все члены группы могут читать, писать и удалять любые файлы в папке.
1770 (Sticky bit): Все члены группы могут создавать файлы, но удалять файл может только его владелец (или root).

### Шаг 15

```
find / -perm -4000 2>/dev/null
```
вывод:
```
/home/andrew/test_privesc.sh
/opt/VBoxGuestAdditions-7.2.8/bin/VBoxDRMClient
/usr/bin/at
/usr/bin/chage
/usr/bin/crontab
/usr/bin/fusermount
/usr/bin/fusermount-glusterfs
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/userhelper
/usr/bin/grub2-set-bootflag
/usr/bin/mount
/usr/bin/umount
...
```

1) /usr/bin/passwd - этот файл позволяет пользователям менять свои пароли. если в коде программы есть ошибка обработки входных данных, злоумышленник может подать слишком длинную строку вместо пароля, что приведет к выполнению произвольного кода с правами root.
2) /usr/bin/mount - утилита используется для подключения файловых систем. обычно это привилегированная операция, но SUID-бит позволяет системе разрешать обычным пользователям монтировать устройства, которые прописаны в /etc/fstab с опцией user. подмена файловой системы: Злоумышленник может попытаться смонтировать специально подготовленный образ диска, на котором уже лежит файл с SUID-битом (например, копия /bin/bash с правами root). Если mount не проверяет флаги безопасности (типа nosuid), это приведет к мгновенному захвату системы.
3) /usr/bin/crontab - Эта утилита позволяет пользователям планировать задачи (cron jobs). Сами файлы расписаний хранятся в директории /var/spool/cron, куда обычному пользователю запись запрещена. SUID-бит позволяет программе crontab изменять эти файлы от имени root. Если утилита позволяет через параметры указать путь к редактируемому файлу без должной проверки, пользователь может перезаписать важные системные конфиги.

### Шаг 16

```
ps
```

вывод:
```
PID    TTY          TIME     CMD
3668   pts/0      00:00:01   zsh
13372  pts/0      00:00:00   ps
```
видно два процесса от имени пользователя

```
ps aux
```
выводит все процессы в системе, в том числе от root
```
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.5  38668 20976 ?        Ss   17:47   0:03 /usr/lib/systemd/systemd --switched-root --
root           2  0.0  0.0      0     0 ?        S    17:47   0:00 [kthreadd]
root           3  0.0  0.0      0     0 ?        S    17:47   0:00 [pool_workqueue_release]
root           4  0.0  0.0      0     0 ?        I<   17:47   0:00 [kworker/R-rcu_gp]
root           5  0.0  0.0      0     0 ?        I<   17:47   0:00 [kworker/R-sync_wq]
...
```

можно использовать `htop`, который дефолтно установлен в fedora для графического контроля процессов. (Q - для выхода).

### Шаг 17+18

коммитим

```
vi README.md
git add README.md
git commit -S -m "обновили README.md, после второй лабораторной"
```

если вы это читаете, значит все сделано.

## Результаты

- Изучена файловая система `*nix` машин
- Добавлены новые пользователи и группы
- Изучены права доступов к файлам
- Изучены риски при работе от разных прав доступа
- Созданы файлы `pygamesteel.py` и `pygamesteel_fixed.py`
- Изучено отслеживание процессов

***

## Выводы

Мы научились работать с файловой системой, разобрались с правами доступа для файлов и для папок, изучили способы контроля процессов от разных пользователей и отслеживания действий с папками и файлами.

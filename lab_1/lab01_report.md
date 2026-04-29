# Лабораторная работа №1 — GitSCM — подготовка рабочего окружения

**Автор:** Матвеичев Андрей
**Группа:** М03-503
**Дата:** 2026-04-22

***

## Цель работы

Начальная настройка системы. Установка пакетов. Настройка Git, SSH-ключей, GnuPG для подписания коммитов и GitHub CLI. Работа с github

***

## Ход выполнения

### Шаг 0. Настройка Git, GPG и GitHub CLI

основные команды настройки:
```
git config --global user.name "Андрей"
git config --global user.email "matveichev.ap@phystech.edu"
git config --global core.editor "vim"                    # или nano
git config --global alias.co checkout                    # git co вместо git checkout
git config --global help.autocorrect prompt              # автозамена при опечатке
git config --global core.autocrlf true                   # Windows: true, Linux/macOS: input
git config --global credential.helper cache              # кэш учётных данных (15 мин)
git config --global commit.gpgsign true                  # автоподпись коммитов
```
проверить результат выполнения можно командой `git config list`

выводятся наши настройки:
```
user.name=Andrew
user.email=matveichev.ap@phystech.edu
user.signingkey=A49D68EDE7A192BB93F4D830237E3E571894609E
core.editor=vim
core.autocrlf=true
alias.co=checkout
help.autocorrect=prompt
credential.helper=cache
commit.gpgsign=true
tag.gpgsign=true
```

#### Установка Git и GitHub CLI

```
sudo dnf install -y git gh
```
после введения пароля, без проблем устанавливается github

Авторизация выполняется командой
```
gh auth login
```
авторизуемся через http, вводим ключ в браузер, подключенный к github.

#### SSH-ключ для GitHub
команды для генерации, сохранения и добавления ключа
```
ssh-keygen -t ed25519 -C "email@example.com"             # генерация ключа
eval "$(ssh-agent -s)"                                   # запуск агента
ssh-add ~/.ssh/id_ed25519                                # добавление ключа в агент
cat ~/.ssh/id_ed25519.pub                                # скопировать публичный ключ
```
Добавляем сгенерированный публичный ключ в GitHub: Settings → SSH and GPG keys → New SSH key → вставить содержимое .pub

Проверяем командой `ssh -T git@github.com`

Команда выводит
```
Hi B-a-n-a-n! You've successfully authenticated, but GitHub does not provide shell access.
```
Значит ключ подключен и мы можем продолжать работу дальше

#### GnuPG для подписания коммитов

для генерации и проверки gpg ключа выполним:
```
gpg --full-generate-key                                  # создание ключа (RSA 4096, срок — 1 год)
gpg --list-secret-keys --keyid-format=long               # список ключей
```
получили ключ gpg ABCDEF1234567890, экспортируем его и добавим к github
```
gpg --armor --export ABCDEF1234567890
```
добавляем в GitHub: Settings → SSH and GPG keys → New GPG key

Настраиваем
```
git config --global user.signingkey ABCDEF1234567890     # указать ключ
git config --global commit.gpgsign true                  # автоподпись коммитов
git config --global tag.gpgSign true                     # автоподпись тегов
```
#### Personal Access Token

на github.com/settings/tokens/new
Выбераем scope: gist
Генерируем и сохраняем токен.

### Шаг 1. Инициализируем новый локальный репозиторий в отдельной папке
```
mkdir lab_1
git initls
```
### Шаг 2. Первый коммит в remote_origin
добавим пустой README.md
```
touch README.md
git add README.md
git commit -S -m "first commit"
```
после ввода пароля ключа, программа отвечает
```
git add README.md
git commit -S -m "first commit"
[master (root-commit) d0b74a7] first commit
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 README.md
```
создадим ветку
```
git branch -M master
```
добавим удаленный репозиторий и запушим
```
git remote add origin git@github.com:B-a-n-a-n/appsec_labs.git
git push -u origin master
```
вывод:
```
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Writing objects: 100% (3/3), 867 bytes | 867.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To github.com:B-a-n-a-n/appsec_labs.git
 * [new branch]      master -> master
branch 'master' set up to track 'origin/master'.
```

проверим настройку командой `git remote show origin`:

вывод:
```
* remote origin
  Fetch URL: git@github.com:B-a-n-a-n/appsec_labs.git
  Push  URL: git@github.com:B-a-n-a-n/appsec_labs.git
  HEAD branch: master
  Remote branch:
    master tracked
  Local branch configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push':
    master pushes to master (up to date)

```
указан нужный репозиторий и нужная ветка, значит все верно.

### Шаг 3. Hello appsec world

#### простой файл
создадим файл "hello.py" в lab_1/
```
touch lab_1/hello.py
```
при помощи редактора vim реализуем "Hello appsec world" на питоне
```python
print("Hello appsec world")
```
коммитим:
```
git add -A
git commit -S -m "added simple hello.py to lab_1/"
git push -u origin master
```
после ввода секретного ключа получаем вывод:
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 2 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (4/4), 1.00 KiB | 1.00 MiB/s, done.
Total 4 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To github.com:B-a-n-a-n/appsec_labs.git
   d0b74a7..f7fd75a  master -> master
branch 'master' set up to track 'origin/master'.
```
#### редактируем файл

редактируем файл "hello.py"

```python
name = input("Введите имя: ")
print("Hello appsec world from ", name)
```
пушим изменения

```
git add -A
git commit -S -m "upgraded hello.py"
git push -u origin master
```
ответ:
```
[master f5f1156] upgraded hello.py
 1 file changed, 2 insertions(+), 1 deletion(-)
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 2 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (4/4), 1.05 KiB | 1.05 MiB/s, done.
Total 4 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
To github.com:B-a-n-a-n/appsec_labs.git
   f7fd75a..f5f1156  master -> master
branch 'master' set up to track 'origin/master'.
```
проверяем, что все изменения сохранились и видны актуальные файлы.
```
git log --oneline
```
вывод:
```
f5f1156 (HEAD -> master, origin/master) upgraded hello.py
f7fd75a added simple hello.py to lab_1/
d0b74a7 first commit
```

### Шаг 3. Работаем с ветками

#### редактируем файл в новой ветке

создадим и переключимся на новую ветку:
```
git checkout -b patch1
```
вывод:
```
Switched to a new branch 'patch1'
```

обновим файл

```python
import typer

def main(
    name: str,
    lastname: str = typer.Option("", help="Фамилия пользователя."),
    formal: bool = typer.Option(False, "--formal", "-f", help="Использовать формальное приветствие."),
):
    """
    Говорит "Привет" пользователю, опционально используя фамилию и формальный стиль.
    """
    if formal:
        print(f"Добрый день, {name} {lastname}!")
    else:
        print(f"Привет, {name}!")

if __name__ == "__main__":
    typer.run(main)
```
установим библиотеку typer и проверим:
```
pip3 install typer
python lab_1/hello.py Андрей
```
вывод:
```
Привет, Андрей!
```
все работает, можно коммитить:
```
git add -A
git commit -S -m "Обновили код с формальным приветствием"
git push -u origin patch1
```

в выводе `git log --oneline` видим обновления: 
```
a991f0d (HEAD -> patch1, origin/patch1) Обновили код с формальным приветствием
```

#### создаем pull-request в виде patch1 -> master

```
gh pr create --base master --head patch1 --title "Patch1: использование typer для приветствия" --body "Реализовали hello.py с typer"
```
вывод:
```
Creating pull request for patch1 into master in B-a-n-a-n/appsec_labs

https://github.com/B-a-n-a-n/appsec_labs/pull/1
```
добавим комментарии в код, закоммитим и запушим:
```python
import typer

# main program loop
def main(
    # used parameters
    name: str,
    lastname: str = typer.Option("", help="Фамилия пользователя."),
    formal: bool = typer.Option(False, "--formal", "-f", help="Использовать формальное приветствие."),
):
    """
    Говорит "Привет" пользователю, опционально используя фамилию и формальный стиль.
    """
    # Check if formal greeting is needed
    if formal:
        # Give greetings with name and surname
        print(f"Добрый день, {name} {lastname}!")
    else:
        # Give greetings with name
        print(f"Привет, {name}!")

if __name__ == "__main__":
    typer.run(main)
```

```
git add -A
git commit -S -m "Добавили комментарии в hello.py"
git push origin patch1
```

видим изменения на сайте.

#### Мерджим векти
```
gh pr list
```
видим номер 1 последний с нужными изменениями, значит
```
gh pr merge 1 --merge --delete-branch
```
вывод:
```
✓ Merged pull request B-a-n-a-n/appsec_labs#1 (Patch1: использование typer для приветствия)
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (1/1), 970 bytes | 970.00 KiB/s, done.
From github.com:B-a-n-a-n/appsec_labs
 * branch            master     -> FETCH_HEAD
   f5f1156..6bf066b  master     -> origin/master
Updating f5f1156..6bf066b
Fast-forward
 lab_1/hello.py | 24 ++++++++++++++++++++++--
 1 file changed, 22 insertions(+), 2 deletions(-)
✓ Deleted local branch patch1 and switched to branch master
✓ Deleted remote branch patch1
```
На сайте видим, что ветка patch1 пропала а все изменения с комментариями теперь лежат в master.

#### Стяните актуальные изменения в master и удалите локальную ветку patch1

```
git checkout master
git pull origin master
git branch -d patch1
```
локальная ветка тоже удалена.

рассмотрим изменения через `git log --oneline --graph`:

```
*   6bf066b (HEAD -> master, origin/master) Merge pull request #1 from B-a-n-a-n/patch1
|\  
| * de525dd (origin/patch1) Добавили комментарии в hello.py
| * a991f0d Обновили код с формальным приветствием
|/  
* f5f1156 upgraded hello.py
* f7fd75a added simple hello.py to lab_1/
* d0b74a7 first commit

```

видим что ветка ответвляется, после чего мерджится с master

#### создадим новую ветку

```
git checkout -b patch2
```
обновим файл:

```python
import typer

def main(
    user_name: str,
    user_lastname: str = typer.Option("", help="Фамилия пользователя."),
    is_formal: bool = typer.Option(False, "--formal", "-f", help="Использовать формальное приветствие."),
):
    """
    Говорит "Привет" пользователю, опционально используя фамилию и формальный стиль.
    """
    if is_formal:
        print(f"Добрый день, {user_name} {user_lastname}!")
    else:
        print(f"Привет, {user_name}!")

if __name__ == "__main__":
    typer.run(main)
```

коммит пуш:
```
git add -A
git commit -S -m "Поменяли codestyle"
git push -u origin patch2
```

здесь я немного накосячил и запушил в master, поэтому пришлось делать revert и возвращать изменения назад, потом при помощи git pop прятать изменения но я по итогу все разрешил и дальше вот работаем 

#### Создайте pull-request patch2 -> master

```
gh pr create --base master --head patch2 --title "Change code style" --body "Renamed variables for clarity"
```
вывод:
```
Creating pull request for patch2 into master in B-a-n-a-n/appsec_labs

https://github.com/B-a-n-a-n/appsec_labs/pull/2
```

```
git checkout master
```

добавим в начало файла

```
#program that greets user
#good demonstration of how python functions work
```

коммитим и пушим изменения
```
git add -A
git commit -S -m "Update docstring in master"
git push origin master
```

переходим на ветку назад
```
git checkout patch2
git fetch origin
git rebase origin/master
```

возник конфликт, который мы поправим через редактирование файлов, продолжим rebase
```
git add -A
git rebase --continue
```

Публикуем ветку
```
git push --force-with-lease origin patch2
```

мерджим и переходим на master
```
gh pr merge 2 --merge --delete-branch
```

## Результаты

- Мы изучили основные комманды git
- Разобрались с основными командами add, commit, push
- Разобрались как работают ветки (команды branch, rebase)
- получили основу для работу над последующими лабораторными

***

## Выводы

В ходе лабораторной работы были освоены основные операции с Git и GitHub: работа с ветками, создание pull request, разрешение конфликтов через rebase и подпись коммитов ключом GPG. Полученные навыки позволяют эффективно управлять версиями кода в командных проектах и поддерживать чистоту истории изменений.

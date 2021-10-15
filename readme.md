# CloudPhoto - первое задение. Хазиев Булат 11-806.
* [Установка](#установка)
* [Настройка](#настройка)
* [использование](#использование)
## Установка

#### Устанвите Python верссии 3.7 или выше.
#### Добавьте Python в PATH
#### Склонируйте этот репозиторий
git clone https://github.com/unbrokenguy/cloudphoto.git
#### Перейдите в папку с репозиторием и установите скрипт
```shell
pip install -e .
```
## Настройка
#### Добавьте в домашнюю директерию папку `.aws` с текстовым файлом без расширения `credentials`
`.aws/credentials`
```text
[default]
    aws_access_key_id = <id>
    aws_secret_access_key = <key>
```
#### и файл `.aws/config` с регионом.
```
[default]
    region=ru-central1
```
## Использование
## Чтобы узнать список доступных команд заупустите консольное приложение 
```shell
cloudphoto help
```

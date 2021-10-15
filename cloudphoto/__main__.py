import io
import sys
from enum import Enum
from pathlib import Path
from typing import List
import boto3


class YaCloudProvider:
    def __init__(self):
        session = boto3.session.Session()
        self.s3 = session.client(service_name="s3", endpoint_url="https://storage.yandexcloud.net")

    def get_albums(self) -> List[str]:
        buckets = self.s3.list_buckets()["Buckets"]
        return [b["Name"] for b in buckets]

    def get_bucket_files(self, bucket):
        return [key["Key"] for key in self.s3.list_objects(Bucket=bucket)["Contents"]]

    def upload_file(self, data, file_name, bucket):
        self.s3.upload_fileobj(data, bucket, file_name)

    def upload_album(self, album, photos):
        for photo in photos:
            data = io.BytesIO(open(str(photo), "rb").read())
            data.name = photo.name
            self.upload_file(data=data, file_name=data.name, bucket=album)

    def download_file(self, bucket, file):
        get_object_response = self.s3.get_object(Bucket=bucket, Key=file)
        return get_object_response["Body"].read()

    def download_bucket(self, bucket):
        data = []
        names = self.get_bucket_files(bucket)
        for file in names:
            data.append((file, self.download_file(bucket, file)))
        return data

    def create_album(self, album):
        self.s3.create_bucket(Bucket=album)


class CloudPhotoApp:
    class Commands(Enum):
        LIST = {
            "commands": ["list"],
            "usage": ["", "-a album"],
            "description": [
                "Выводит список альбомов, которые присутствуют в облачном хранилище",
                "Выводит список фотографий, которые относятся к альбому album",
            ],
        }
        HELP = {"commands": ["help"], "usage": [""], "description": ["Выводит эту вспомогательную информацию"]}
        UPLOAD = {
            "commands": ["upload"],
            "usage": ["-p path -a album"],
            "description": [
                "Отправляет все фотографии (без рекурсии) из каталога path в облачное хранилище и привязывает их к альбому album. Если альбома не существует, то создает новый альбом. Если каталога не существует, то выдает соответствующую ошибку"
            ],
        }
        DOWNLOAD = {
            "commands": ["download"],
            "usage": ["-p path -a album"],
            "description": [
                "Загружает из облачного хранилища все фотографии в каталог path, которые относятся к альбому album. Если альбома или каталога не существует, то выдает соответствующую ошибку"
            ],
        }

    def __init__(self, provider: YaCloudProvider):
        self.provider = provider

    def execute(self, command, params):
        if command == self.Commands.UPLOAD:
            return self.upload_command(params)
        elif command == self.Commands.DOWNLOAD:
            return self.download_command(params)
        elif command == self.Commands.LIST:
            return self.list_command(params)
        elif command == self.Commands.HELP:
            return self.help_command(params)
        print("Ошибка! Неправильная команда")

    def get_command(self, command):
        if command == "upload":
            return self.Commands.UPLOAD
        elif command == "download":
            return self.Commands.DOWNLOAD
        elif command == "list":
            return self.Commands.LIST
        elif command == "help":
            return self.Commands.HELP
        print("Ошибка! Неправильная команда")

    def list_command(self, params):
        if params.get("-a"):
            photos = self.provider.get_bucket_files(bucket=params["-a"])
            print(f'Список фотографий в альбоме "{params["-a"]}":')
            print("\n".join(list(map(lambda p: f"{str(photos.index(p) + 1)}) {p}", photos))))
        else:
            albums = self.provider.get_albums()
            print("Список альбомов:")
            print("\n".join(list(map(lambda a: f"{str(albums.index(a) + 1)}) {a}", albums))))

    def download_command(self, params):
        try:
            _path = Path(params["-p"])
            _album = params["-a"]
        except KeyError:
            print("Не был передан параметр '-a' или '-p'")
            return
        if not Path.is_dir(_path):
            print("Ошибка! Указанного каталога не существует.")
            return
        if _album not in self.albums:
            print("Ошибка! Указанного альбома не существует.")
            return
        _path = _path / _album
        Path.mkdir(_path, exist_ok=True)
        data = self.provider.download_bucket(_album)
        for item in data:
            _new_file_path = Path(str(_path)) / item[0]
            file = open(_new_file_path, "wb")
            file.write(item[1])

    def upload_command(self, params):
        try:
            _path = Path(params["-p"])
            _album = params["-a"]
        except KeyError:
            print("Не был передан параметр '-a' или '-p'")
            return
        if not Path.is_dir(_path):
            print("Ошибка! Указанного каталога не существует.")
            return
        if _album not in self.albums:
            self.provider.create_album(_album)
        _photos = list(
            filter(
                lambda p: not Path.is_dir(p) and (p.name.split(".")[-1] == "jpg" or p.name.split(".")[-1] == "jpeg"),
                _path.iterdir(),
            )
        )
        self.provider.upload_album(_album, _photos)

    @property
    def albums(self):
        return self.list_command({})

    def help_command(self, params):
        string = "CloudPhoto commands:\n"
        messages = []
        indent = 0
        for command in self.Commands:
            _command = command._value_["commands"]
            _usage = command._value_["usage"]
            _description = command._value_["description"]
            for i in range(len(_usage)):
                _full_command = f"{_command[0]} {_usage[i]}"
                if len(_full_command) > indent:
                    indent = len(_full_command)
                messages.append([f"{_command[0]} {_usage[i]}", f"{_description[i]}"])
        for message in messages:
            string += f"\t{message[0]}{' ' * (indent - len(message[0]) + 1)}{message[1]}\n"
        print(string)


def main():
    provider = YaCloudProvider()
    app = CloudPhotoApp(provider=provider)
    try:
        command = app.get_command(sys.argv[1])
    except IndexError:
        command = app.get_command("help")
    parameters = {}
    if "-p" in sys.argv:
        parameters["-p"] = sys.argv[sys.argv.index("-p") + 1]
    if "-a" in sys.argv:
        parameters["-a"] = sys.argv[sys.argv.index("-a") + 1]
    app.execute(command, params=parameters)


if __name__ == "__main__":
    main()

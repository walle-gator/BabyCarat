import io
from dataclasses import dataclass
from typing import Callable, IO, cast, BinaryIO
from zipfile import ZipFile

from PIL import ImageFont

from livetext_botc import http


@dataclass
class ZipResource(http.Resource):
    url: str
    ext = 'zip'
    text = False

    def parse(self, content: bytes) -> ZipFile:
        return ZipFile(io.BytesIO(content))


@dataclass
class DelegateResource[X, T]:
    src: http.Resource[X]
    fn: Callable[[X], T]

    def parse(self, content: str | bytes) -> T:
        source = self.src.parse(content)
        return self.fn(source)

    def __getattr__(self, name):
        return self.src.__getattribute__(name)


def get_fira_code_archive(version: str = '6.2') -> http.Resource[ZipFile]:
    r = f'https://github.com/tonsky/FiraCode/releases/download/{version}/Fira_Code_v{version}.zip'
    return ZipResource(r)


def get_fira_code(file: str = 'ttf/FiraCode-Bold.ttf', version: str = '6.2'):
    archive = get_fira_code_archive(version)

    def access_file(z: ZipFile) -> IO[bytes]:
        return z.open(file)

    def open_font(i: IO[bytes]) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(cast(BinaryIO, i))

    return DelegateResource(archive, lambda z: open_font(access_file(z)))

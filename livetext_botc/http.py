from hashlib import sha1
from pathlib import Path
from typing import Protocol

import httpx


class Resource[T](Protocol):
    url: str
    ext: str
    text: bool = True

    def parse(self, content: str | bytes) -> T:
        ...


class Downloader:
    def __init__(self, cache_dir: Path = None):
        if cache_dir is None:
            cache_dir = Path('.ltb')

        self.cache = cache_dir
        if not self.cache.exists():
            self.cache.mkdir()
            git = self.cache / '.gitignore'
            git.write_text('*\n')

        self.cache = self.cache.resolve()

    def download[T](self, res: Resource[T]) -> T:
        if res is None:
            raise ValueError('Res cannot be None!')
        output = self.cache / (Downloader._hash(res.url) + '.' + res.ext)

        if not output.exists():
            r = httpx.get(res.url, follow_redirects=True)
            if not r.is_success:
                raise ValueError(f'Download failed: {r.status_code}')
            output.write_bytes(r.content)

        if res.text:
            return res.parse(output.read_text())

        return res.parse(output.read_bytes())

    @staticmethod
    def _hash(text: str | Resource):
        return sha1(text.encode('UTF-8')).hexdigest()

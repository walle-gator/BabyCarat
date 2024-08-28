import io
import json
import urllib.parse
from dataclasses import dataclass
from typing import Callable, Any

from PIL import Image
from schema import Schema

from livetext_botc import botc
from livetext_botc.http import Resource

SCRIPT_TOOL_URL = 'https://script.bloodontheclocktower.com'


@dataclass
class RemoteResource[T](Resource):
    url: str
    schema: Schema
    transform: Callable[[Any], T] = None
    text: bool = True
    ext: str = 'json'

    def parse(self, content: str) -> T:
        obj = json.loads(content)
        self.schema.validate(obj)
        if self.transform is None:
            return obj
        return self.transform(obj)


@dataclass
class RemoteImage(Resource):
    url: str
    ext: str = 'webp'
    text = False

    def parse(self, content: bytes) -> Image.Image:
        return Image.open(io.BytesIO(
            content
        ))


def get_script(script_id: int) -> Resource[botc.Script]:
    return RemoteResource(
        f'https://botc-scripts.azurewebsites.net/api/scripts/{script_id}/json/',
        botc.ScriptSchema,
        transform=botc.Script.parse
    )


def get_roles() -> Resource:
    def resolve_url(value, key):
        parse = urllib.parse
        value[key] = parse.quote(
            parse.urljoin(SCRIPT_TOOL_URL, value[key]),
            safe=':/'
        )

    def transform(values):
        roles = {}
        for value in values:
            id = value['id']
            roleType = botc.RoleType.parse(value['roleType'])
            resolve_url(value, 'print')
            resolve_url(value, 'icon')
            roles[id] = {
                'id': id,
                'name': value['name'],
                'image': value['icon'],
                'team': roleType,
            }

        return roles

    return RemoteResource(
        f'{SCRIPT_TOOL_URL}/data/roles.json',
        Schema([
            {
                'id': str,
                'name': str,
                'roleType': botc.RoleType.is_role_type,
                'print': str,
                'icon': str,
                'version': str,
                'isDisabled': bool
            }
        ]),
        transform=transform
    )


def get_tether() -> Resource:
    """Get the list of tether constraints required."""
    return RemoteResource(
        f'{SCRIPT_TOOL_URL}/data/tether.json',
        Schema([
            {
                'id': str,
                'tether': [
                    {
                        'id': str,
                        'reason': str,
                    }
                ]
            }
        ])
    )


def get_jinxes() -> Resource:
    return RemoteResource(
        f'{SCRIPT_TOOL_URL}/data/jinx.json',
        Schema(object)
    )


def get_character_restrictions() -> Resource:
    return RemoteResource(
        f'{SCRIPT_TOOL_URL}/data/game-characters-restrictions.json',
        Schema(object)
    )


def get_night_sheet() -> Resource:
    return RemoteResource(
        f'{SCRIPT_TOOL_URL}/data/nightsheet.json',
        Schema({
            'firstNight': [str],
            'otherNight': [str],
        })
    )


def get_shroud() -> Resource:
    return RemoteImage(
        url='https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/shroud.png',
        ext='png'
    )

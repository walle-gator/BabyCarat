from dataclasses import dataclass
from enum import Enum

from schema import Schema, Or, Optional


class RoleType(Enum):
    TOWNSFOLK = 0
    OUTSIDER = 1
    MINION = 2
    DEMON = 3
    FABLED = 4
    TRAVELLERS = 5

    @staticmethod
    def parse(value):
        return RoleType[value.upper()]

    @staticmethod
    def is_role_type(value: str):
        """ Checks a given role is valid """
        try:
            return RoleType.parse(value) is not None
        except KeyError:
            return False


# This is currently just a reference or container to access all info of a role
@dataclass
class Role:
    id: str
    official: bool

    @staticmethod
    def parse(value: str | dict):
        if isinstance(value, str):
            return Role(
                id=value,
                official=True
            )

        return Role(
            id=value['id'],
            # Only contains ID => deprecated old way
            official=len(value.keys()) == 1
        )


@dataclass
class Script:
    name: str
    author: str
    roles: list[Role]

    @staticmethod
    def parse(value: list[dict]) -> 'Script':
        meta = None
        roles = []

        for val in value:
            if isinstance(val, str):
                # Official Character
                roles.append(Role.parse(val))
                continue

            identifier = val['id']
            if identifier != '_meta':
                roles.append(Role.parse(val))
                continue

            if meta is not None:
                raise ValueError('Multiple Meta found!')

            meta = val

        if meta is None:
            # Missing meta is fine, so just make them an empty string
            meta = {
                'name': '',
                'author': ''
            }

        return Script(meta['name'], meta['author'], roles)


ScriptSchema = Schema([
    Or(
        ## Script Metadata
        {'id': '_meta', 'name': str, 'author': str},
        ## Script Character
        {
            'id': str,
            'name': str,
            Optional('image'): Or(str, list),
            Optional('edition'): str,
            'team': RoleType.is_role_type,
            "ability": str,
            Optional('firstNight'): int,
            Optional('firstNightReminder'): str,
            Optional('reminders'): list,
            Optional('remindersGlobal'): list,
            Optional('setup'): bool,
            Optional('jinxes'): list,
            Optional('special'): list,
        },
        ## Official character ID
        str,
        ## Official Character (deprecated)
        {'id': str},
    )
])

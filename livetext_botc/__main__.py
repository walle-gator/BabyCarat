from . import (
    http,
    remote_library as lib,
    grim,
    fonts
)


def download():
    dl = http.Downloader()
    print('get_roles\t\t\t\t\t', dl.download(lib.get_roles()))
    print('get_night_sheet\t\t\t\t', dl.download(lib.get_night_sheet()))
    print('get_character_restrictions\t', dl.download(lib.get_character_restrictions()))
    print('get_jinxes\t\t\t\t\t', dl.download(lib.get_jinxes()))
    print('get_tether\t\t\t\t\t', dl.download(lib.get_tether()))
    print('get_script\t\t\t\t\t', dl.download(lib.get_script(7252)))


def draw(players: list[grim.Player]):
    dl = http.Downloader()
    roles = dl.download(lib.get_roles())

    g = grim.Grim(
        seats=len(players),
        shroud=dl.download(lib.get_shroud()),
        get_text_font=lambda size: dl.download(fonts.get_fira_code()),
        get_role_image=lambda ident: dl.download(lib.RemoteImage(roles[ident]['image'])),
        get_role_name=lambda ident: roles[ident]['name'],
    )

    for i, player in enumerate(players):
        g.draw_seat(i, player, grim_access=True)

    g.show()

    for i, player in enumerate(players):
        g.draw_seat(i, player, grim_access=False)

    g.show()


def draw_example():
    draw([
        grim.Player('Killaw', 'seamstress', reminders=[
            (None, 'Bluffing goblin'),
        ]),
        grim.Player('Gator', 'lunatic'),
        grim.Player('EMC', 'lleech'),
        grim.Player('Louise', 'scarletwoman'),
        grim.Player('Sterling', 'slayer', reminders=[
            ('slayer', 'No ability'),
            ('lunatic', 'Attack 1'),
            ('marionette', 'Is the Marionette')
        ]),

        grim.Player('Axolator', 'devilsadvocate', dead=True, reminders=[
            ('drunk', 'Drunk'),
            ('lleech', 'Poisoned'),
        ]),
        grim.Player('Zipline', 'judge', visible=True),
        grim.Player('Nexus', 'marionette'),
        grim.Player('De', 'choirboy'),
        grim.Player('Miha', 'king'),
    ])


draw_example()

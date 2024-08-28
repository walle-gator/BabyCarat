from dataclasses import dataclass, field
from typing import Callable

from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import (
    math_utils
)


@dataclass
class Player:
    name: str
    role: str
    dead: bool = False
    traveler: bool = False
    visible: bool = False
    reminders: list[tuple[str | None, str]] = field(default_factory=lambda: [])


class Grim:
    def __init__(
            self,
            seats: int,
            shroud: Image.Image,
            get_text_font: Callable[[int], ImageFont.FreeTypeFont],
            get_role_image: Callable[[str], Image.Image],
            get_role_name: Callable[[str], str],
            # These values 'just' work
            width: int = 950,
            height: int = 950,
            token_size: int = 128,
            reminder_size: int = 64,
            nameplate_height: int = 42,
            token_padding: int = 10
    ):
        self.image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        self.ctx = ImageDraw.Draw(self.image)
        self.font = get_text_font(12)
        self.get_role_image = get_role_image
        self.get_role_name = get_role_name
        self.token_size = token_size
        self.reminder_size = reminder_size
        self.nameplate_height = nameplate_height
        self.token_padding = token_padding
        self.seats = seats
        self.shroud = shroud
        self.shroud.thumbnail((self.token_size * 0.5, self.token_size * 0.5))

        top = token_size / 2
        # IDK why this is one pixel off
        plate = nameplate_height + token_padding + 1
        bottom = height - top - plate
        inner_height = bottom - top
        self.center = math_utils.Vec2f((width / 2, top + inner_height / 2))
        self.inner_radius = inner_height / 2

    def draw_seat(
            self,
            seat: int,
            player: Player,
            grim_access: bool = True
    ):
        angle = math_utils.degrees((360 / self.seats) * seat)
        pos = math_utils.get_pos_on_circle(self.center, self.inner_radius, angle)

        self._draw_token_outline(pos, size=self.token_size)
        if player.visible or grim_access:
            self._draw_token_image(pos, player.role, size=self.token_size)
            name = self.get_role_name(player.role)
            self._draw_token_name(pos, name, size=self.token_size, curve=10)

        if player.dead:
            i = math_utils.vec_to_int(pos)
            offset_x = self.shroud.size[0] / 2
            offset_y = self.token_size / 2

            token = self._paste_overlay(
                self.shroud,
                (i[0] - offset_x, i[1] - offset_y)
            )
            self.image.alpha_composite(token)

        self._draw_nameplate(pos, player.name)

        if grim_access:
            self._draw_reminder_tokens(angle, player.reminders)

    def _draw_reminder_tokens(self, angle, reminders):
        # Adjust for the nameplate under the top node and draw smaller circles to place tokens on
        base_pos = (self.center[0], self.center[1] + self.nameplate_height / 2 + self.token_padding / 2)
        base_radius = self.inner_radius - self.token_size
        for depth, (icon, reminder) in enumerate(reminders):
            r = base_radius - depth * (self.token_padding + self.reminder_size)
            p = math_utils.get_pos_on_circle(base_pos, r, angle)

            self._draw_token_outline(p, size=self.reminder_size)
            if icon is not None:
                self._draw_token_image(p, icon, size=self.reminder_size)
            self._draw_token_name(p, reminder, size=self.reminder_size, curve=10, additional_scale=8)

    def _draw_nameplate(self, pos, name):
        (px, py) = pos
        py += self.token_size / 2 + self.token_padding
        px -= self.token_size / 2 - self.token_padding / 2
        width = self.token_size - self.token_padding
        height = self.nameplate_height
        box = (px, py, px + width, py + height)
        self.ctx.rounded_rectangle(box, 5, fill='#39424B', width=0)
        s = self._fit_text_to_box(name, self.font, None, box)
        (left, top, right, bottom) = s.getbbox(name)
        horizontal_padding = (width - right) / 2
        vertical_padding = (height - (bottom - top)) / 2
        self.ctx.text((px - left + horizontal_padding, py - top + vertical_padding), name, font=s)

    def _draw_token_outline(self, pos: math_utils.Vec2f, size: int):
        self.ctx.circle(pos, size / 2, fill='#E5E5E5', outline='#0E0E0E')

    def _draw_token_image(self, pos: math_utils.Vec2f, role: str, size: int):
        mask = Image.new('L', (size, size), 0)
        m = ImageDraw.Draw(mask)
        m.circle((size / 2, size / 2), size / 2, fill=255)

        # Apply the mask to the image
        padding = size // 4
        image = self.get_role_image(role)
        image.thumbnail((size - padding, size - padding))
        image = ImageOps.expand(image, padding // 2)

        token = self._paste_overlay(
            image,
            (int(pos[0] - size / 2), int(pos[1] - size / 2)),
            mask
        )
        self.image.alpha_composite(token)

    def _paste_overlay(self, src: Image.Image, pos: math_utils.Vec2f, mask: Image.Image = None):
        token = Image.new('RGBA', self.image.size)
        token.paste(src, math_utils.vec_to_int(pos), mask=mask)
        return token

    def _draw_token_name(self, pos: math_utils.Vec2f, name: str, size: int, curve: int, additional_scale: int = 0):
        # TODO: Make this method support parenthesis better
        n = len(name)

        min_angle = 120
        max_angle = 240
        len_angle = max_angle - min_angle
        offset = (len_angle - (curve * n)) / 2 + min_angle - n * additional_scale / 2
        font = self.font.font_variant(size=(curve * 1.5))
        r = size / 2.5

        for i, char in enumerate(name):
            angle = offset + (n - i) * curve + (n - i) * additional_scale
            p = math_utils.get_pos_on_circle(pos, r, math_utils.degrees(angle))
            self.ctx.text(p, char, font=font, anchor="mm", fill='#0E0E0E')

    def _fit_text_to_box(
            self,
            name: str,
            font: ImageFont.FreeTypeFont,
            size: float | None,
            box: tuple[float, float, float, float]
    ):
        if size is None:
            size = font.size + 1

        original = font
        font = original.font_variant(size=size)
        (left, top, right, bottom) = font.getbbox(name)
        height = bottom - top
        width = right - left
        if box[0] + width > box[2]:
            return original
        if box[1] + height > box[3]:
            return original
        return self._fit_text_to_box(name, font, size + 1, box)

    def show(self):
        self.image.show()
        self.clear()

    def clear(self):
        (w, h) = self.image.size
        self.image.paste('#0000', (0, 0, w, h))

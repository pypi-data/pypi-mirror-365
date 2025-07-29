from code.enemies import Pearl, Shell, Tooth
from code.groups import AllSprites
from code.player import Player
from code.settings import *
from code.sprites import (AnimatedSprite, Item, MovingSprite,
                          ParticleEffectSprite, Spike, Sprite)
from random import uniform
from typing import List


class Level:
    def __init__(self, tmx_map, level_frames):
        self.display_surf: pygame.Surface = pygame.display.get_surface()  # type: ignore[reportAttributeAccessIssue]
        self.level_frames = level_frames  # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        self.setup(tmx_map, self.level_frames)

    def setup(self, tmx_map, level_frames):
        # tiles
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups: List[pygame.sprite.Group] = [self.all_sprites]
                if layer == "Terrain":
                    groups.append(self.collision_sprites)
                if layer == "Platforms":
                    groups.append(self.semi_collision_sprites)
                match layer:
                    case "BG":
                        z = Z_LAYERS["bg tiles"]
                    case "FG":
                        z = Z_LAYERS["bg tiles"]
                    case _:
                        z = Z_LAYERS["main"]
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        # bg objects
        for obj in tmx_map.get_layer_by_name("BG details"):
            # static
            if obj.name == "static":
                Sprite(
                    (obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS["bg details"]  # type: ignore
                )
            else:
                AnimatedSprite(
                    (obj.x, obj.y),
                    level_frames[obj.name],
                    self.all_sprites,
                    Z_LAYERS["bg details"],
                )
                if obj.name == "candle":
                    AnimatedSprite(
                        (obj.x, obj.y) + vector(-20, -20),
                        level_frames["candle_light"],
                        self.all_sprites,
                        Z_LAYERS["bg tiles"],
                    )

        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=(self.all_sprites,),
                    collision_sprites=self.collision_sprites,
                    semi_collision_sprites=self.semi_collision_sprites,
                    frames=level_frames["player"],
                )
            else:
                if obj.name in ("barrel", "crate"):
                    Sprite(
                        (obj.x, obj.y),
                        obj.image,
                        (self.all_sprites, self.collision_sprites),  # type: ignore
                    )
                else:
                    # frames
                    frames = (
                        level_frames[obj.name]
                        if not "palm" in obj.name
                        else level_frames["palms"][obj.name]
                    )
                    if obj.name == "floor_spike" and obj.properties["inverted"]:
                        frames = [
                            pygame.transform.flip(frame, False, True)
                            for frame in frames
                        ]

                    # groups
                    groups = [self.all_sprites]
                    if obj.name in ("palm_small", "palm_large"):
                        groups.append(self.semi_collision_sprites)
                    if obj.name in ("saw", "floor_spike"):
                        groups.append(self.damage_sprites)

                    # z index
                    z = (
                        Z_LAYERS["main"]
                        if not "bg" in obj.name
                        else Z_LAYERS["bg details"]
                    )

                    # animation speed
                    animation_speed = (
                        ANIMATION_SPEED
                        if not "palm" in obj.name
                        else ANIMATION_SPEED + uniform(-1, 1)
                    )

                    AnimatedSprite((obj.x, obj.y), frames, groups, z, animation_speed)  # type: ignore

        # moving objects
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                Spike(
                    pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf=level_frames["spike"],
                    radius=obj.properties["radius"],
                    speed=obj.properties["speed"],
                    start_angle=obj.properties["start_angle"],
                    end_angle=obj.properties["end_angle"],
                    groups=(self.all_sprites, self.damage_sprites),  # type: ignore
                )
                for radius in range(0, obj.properties["radius"], 20):
                    Spike(
                        pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf=level_frames["spike_chain"],
                        radius=radius,
                        speed=obj.properties["speed"],
                        start_angle=obj.properties["start_angle"],
                        end_angle=obj.properties["end_angle"],
                        groups=(self.all_sprites),  # type: ignore
                        z=Z_LAYERS["bg details"],
                    )
            else:
                frames = level_frames[obj.name]
                groups = (
                    (self.all_sprites, self.semi_collision_sprites)
                    if obj.properties["platform"]
                    else (self.all_sprites, self.damage_sprites)
                )  # type: ignore

                # horizontal
                if obj.width > obj.height:
                    move_dir = "x"
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                # vertical
                else:
                    move_dir = "y"
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
                speed = obj.properties["speed"]
                MovingSprite(
                    frames,
                    groups,
                    start_pos,
                    end_pos,
                    move_dir,
                    speed,
                    obj.properties["flip"],
                )

            if obj.name == "saw":
                if move_dir == "x":  # pyright: ignore
                    y = (
                        start_pos[1] - level_frames["saw_chain"].get_height() / 2  # type: ignore
                    )  # pyright: ignore
                    left, right = int(start_pos[0]), int(end_pos[0])  # pyright: ignore
                    for x in range(left, right, 20):
                        Sprite(
                            (x, y),
                            level_frames["saw_chain"],
                            self.all_sprites,  # type: ignore
                            Z_LAYERS["bg details"],
                        )
                else:
                    x = (
                        start_pos[0] - level_frames["saw_chain"].get_width() / 2  # type: ignore
                    )  # pyright: ignore
                    top, bottom = int(start_pos[1]), int(end_pos[1])  # pyright: ignore
                    for y in range(top, bottom, 20):
                        Sprite(
                            (x, y),
                            level_frames["saw_chain"],
                            self.all_sprites,  # type: ignore
                            Z_LAYERS["bg details"],
                        )

        # enemies
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name == "tooth":
                Tooth(
                    (obj.x, obj.y),
                    level_frames["tooth"],
                    self.collision_sprites,
                    (
                        self.all_sprites,
                        self.damage_sprites,
                        self.tooth_sprites,
                    ),
                )
            if obj.name == "shell":
                Shell(
                    pos=(obj.x, obj.y),
                    frames=level_frames["shell"],
                    groups=(self.all_sprites, self.collision_sprites),
                    reverse=obj.properties["reverse"],
                    player=self.player,
                    create_pearl=self.create_pearl,
                )

        # items
        for obj in tmx_map.get_layer_by_name("Items"):
            Item(
                obj.name,
                (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2),
                level_frames["items"][obj.name],
                (self.all_sprites, self.item_sprites),
            )

    def create_pearl(self, pos, direction):
        Pearl(
            pos,
            self.level_frames["pearl"],
            direction,
            150,
            (self.all_sprites, self.damage_sprites, self.pearl_sprites),
        )

    def pearl_collision(self):
        for sprite in self.collision_sprites:
            sprite = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            if sprite:
                ParticleEffectSprite(
                    sprite[0].rect.center,
                    self.level_frames["particle"],
                    self.all_sprites,
                )

    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                print("player damage")
                if hasattr(sprite, "pearl"):
                    sprite.kill()
                    ParticleEffectSprite(
                        sprite.rect.center,
                        self.level_frames["particle"],
                        self.all_sprites,
                    )

    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(
                self.player, self.item_sprites, True
            )
            if item_sprites:
                ParticleEffectSprite(
                    (item_sprites[0].rect.center),
                    self.level_frames["particle"],
                    self.all_sprites,
                )

    def attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
            facing_target = (
                self.player.rect.centerx < target.rect.centerx
                and self.player.facing_right
                or self.player.rect.centerx > target.rect.centerx
                and not self.player.facing_right
            )
            if (
                target.rect.colliderect(self.player.rect)
                and self.player.attacking
                and facing_target
            ):
                target.reverse()

    def run(self, dt):
        self.display_surf.fill("black")

        self.all_sprites.update(dt)
        self.pearl_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()

        self.all_sprites.draw(self.player.hitbox_rect.center)

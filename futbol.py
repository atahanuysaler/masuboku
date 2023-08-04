#!/usr/bin/env python
""" TODO """


# Import Modules
import os
import pygame as pg


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


# functions to create our resources
def load_image(name, colorkey=None, scale=1, targetSize=None):
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)
    image = image.convert()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)
    if targetSize is not None:
        image = pg.transform.scale(image, targetSize)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)

    return sound


# classes for our game objects
class Abou(pg.sprite.Sprite):
    
    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("abou.png", -1, 1, (200, 200))
        self.heading = False

    def update(self):
        """move the abou based on the mouse position"""
        pos = pg.mouse.get_pos()
        self.rect.topleft = pos
        if self.heading:
            self.rect.move_ip(0, -50)

    def head(self, target):
        """returns true if the abou collides with the target"""
        if not self.heading:
            self.heading = True
            hitbox = self.rect.inflate(-50, -50)
            hitbox.move_ip(0,-100)
            return hitbox.colliderect(target.rect)

    def unhead(self):
        """called to pull the abou back"""
        self.heading = False


class Top(pg.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
    monkey when it is headed."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image("top.png", -1, 0.25)
        screen = pg.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 400
        self.x_move = 10
        self.y_move = 0
        self.dizzy = False

    def update(self):
        """walk or spin, depending on the monkeys state"""
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        """move the monkey across the screen, and turn at the ends"""
        newpos = self.rect.move((self.x_move, self.y_move))
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.x_move = -self.x_move
                newpos = self.rect.move((self.x_move, self.y_move))
                self.image = pg.transform.flip(self.image, True, False)
            if self.rect.bottom < self.area.top or self.rect.top > self.area.top:
                self.y_move = -self.y_move
                newpos = self.rect.move((self.x_move, self.y_move))
                self.image = pg.transform.flip(self.image, False, True)
        self.rect = newpos

    def _spin(self):
        """spin the monkey image"""
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = False
            self.image = self.original
            self.y_move = -10
        else:
            rotate = pg.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def headed(self):
        """this will cause the monkey to start spinning"""
        if not self.dizzy:
            self.dizzy = True
            self.original = self.image


def main():
    # Initialize Everything
    pg.init()
    screen = pg.display.set_mode((900, 900), pg.SCALED)
    pg.display.set_caption("i can football")
    pg.mouse.set_visible(False)

    # Create The Background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((170, 238, 187))

    # Put Text On The Background, Centered
    if pg.font:
        font = pg.font.Font(None, 16)
        text = font.render("i can football", True, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width() / 2, y=10)
        background.blit(text, textpos)

    # Display The Background
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Prepare Game Objects
    whiff_sound = load_sound("whiff.wav")
    head_sound = load_sound("punch.wav")
    top = Top()
    abou = Abou()
    allsprites = pg.sprite.RenderPlain((top, abou))
    clock = pg.time.Clock()

    # Main Loop
    going = True
    while going:
        clock.tick(60)

        # Handle Input Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if abou.head(top):
                    head_sound.play()  # head
                    top.headed()
                else:
                    whiff_sound.play()  # miss
            elif event.type == pg.MOUSEBUTTONUP:
                abou.unhead()

        allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pg.display.flip()

    pg.quit()


# Game Over


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

from sys import argv
from contextlib import contextmanager
import yaml
import cairo
from cairottf import create_cairo_font_face_for_file
from math import pi


def parse_css_color(css_color):
    return tuple(int(css_color[2*i+1:2*i+3], 16)/255. for i in range(3))


class Affiche(object):
    SHOW_CONF_IMG = True
    PLACE_SHADOW = False

    # Smartmonday
    TITLE_FONTSIZE = 0.1
    TITLE_POS = (0.02, 0.1)

    # Conférences gratuites en français
    DESCRIPTION_FONTSIZE = 0.05
    DESCRIPTION_POS = (0.02, 0.81)

    # http://urlab.be
    URL_FONTSIZE = 0.05
    URL_POS = (0.02, 0.96)

    # Editeur responsable
    DISCLAIMER_FONTSIZE = 0.025
    DISCLAIMER_POS = (0.02, 0.99)

    # ex: ULB - K.4.401
    PLACE_FONTSIZE = 0.05
    PLACE_POS = (0.02, 0.2)

    # ex: 5 oct. 2015 - 18h30
    DATE_FONTSIZE = 0.045
    DATE_POS = (0.02, 0.15)

    LOGO_CI_POS = (0.5, 0.84)
    LOGO_CI_SIZE = 0.2

    LOGO_URLAB_POS = (0.71, 0.85)
    LOGO_URLAB_SIZE = 0.2

    QRCODE_POS = (0.75, 0.03)
    QRCODE_SIZE = 0.2

    width = 2100
    height = 2970

    def __init__(self, options):
        self.font = options.get('font', 'Sans')
        self.options = options
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.width, self.height)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(self.width, self.height)

        # White background
        self.ctx.rectangle(0, 0, 1, 1)
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.fill()

    def conf_container_path(self, x, y1, y2):
        self.ctx.move_to(x, y1)
        self.ctx.line_to(1-x, (y1+y2)/2)
        self.ctx.line_to(x, y2)

    @contextmanager
    def saved(self):
        self.ctx.save()
        yield
        self.ctx.restore()

    def const_text_path(self, text, fontsize, x, y):
        self.ctx.translate(x, y)
        self.ctx.set_font_size(fontsize)
        for i, line in enumerate(text.split('\n')):
            self.ctx.move_to(0, i*fontsize)
            self.ctx.text_path(line)

    def draw_pratical_infos(self, date_text, place):
        with self.saved():
            self.const_text_path(place,
                self.PLACE_FONTSIZE, *self.PLACE_POS)
            self.ctx.set_source_rgb(0.3, 0.3, 0.3)
            self.ctx.fill()

        if self.PLACE_SHADOW:
            with self.saved():
                left, top = self.DATE_POS
                self.const_text_path(date_text,
                    self.DATE_FONTSIZE, 0.002+left, 0.003+top)
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.fill()

        with self.saved():
            self.const_text_path(date_text,
                self.DATE_FONTSIZE, *self.DATE_POS)
            self.ctx.set_source_rgb(1, 0.1, 0.3)
            self.ctx.fill()

    def draw_constant_infos(self):
        with self.saved():
            self.const_text_path("Smartmonday",
                self.TITLE_FONTSIZE, *self.TITLE_POS)
        with self.saved():
            self.const_text_path(u"Conférences\ngratuites en français",
                self.DESCRIPTION_FONTSIZE, *self.DESCRIPTION_POS)

        with self.saved():
            self.const_text_path("http://urlab.be/sm",
                self.URL_FONTSIZE, *self.URL_POS)

        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.fill()

        with self.saved():
            self.const_text_path(
                u"Éditeur responsable: Cercle informatique, "
                u"Boulevard du Triomphe CP 206, 1050 Bruxelles",
                self.DISCLAIMER_FONTSIZE, *self.DISCLAIMER_POS)
        self.ctx.set_source_rgb(0.5, 0.5, 0.5)
        self.ctx.fill()

        img = cairo.ImageSurface.create_from_png("logo_CI.png")
        rw = self.LOGO_CI_SIZE/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(*self.LOGO_CI_POS)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

        img = cairo.ImageSurface.create_from_png("urlab.png")
        rw = self.LOGO_URLAB_SIZE/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(*self.LOGO_URLAB_POS)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

        img = cairo.ImageSurface.create_from_png("smartMondayQR.png")
        rw = self.QRCODE_SIZE/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(*self.QRCODE_POS)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

    def draw_conf(self, triangle_options, x, y1, y2):
        triangle_path = lambda: self.conf_container_path(x, y1, y2)

        imgfile = triangle_options.get('image', None)
        text = triangle_options.get('text', None).upper()
        color = triangle_options.get('color', "#ffffff")
        if isinstance(color, str) or isinstance(color, unicode):
            color = parse_css_color(color)
        alpha = 0.5 if self.SHOW_CONF_IMG else 0.9
        if len(color) == 3:
            color = tuple(color) + (alpha,)

        # Image
        if imgfile and self.SHOW_CONF_IMG:
            triangle_path()
            self.ctx.close_path()
            img = cairo.ImageSurface.create_from_png(imgfile)
            r = 1./float(img.get_width())
            with self.saved():
                self.ctx.translate(0, y1)
                self.ctx.clip()
                self.ctx.scale(r, r)
                self.ctx.set_source_surface(img, 0, 0)
                self.ctx.paint()

        # Overlay color
        triangle_path()
        self.ctx.close_path()
        self.ctx.set_source_rgba(*color)
        self.ctx.fill()

        # Perimeter
        triangle_path()
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.set_line_width(0.005)
        self.ctx.stroke()

        self.draw_conf_text(text, x, y1, y2)

    def conf_text_path(self, text, x, y, x_incr, y_incr):
        for i, line in enumerate(text.split('\n')):
            self.ctx.move_to(x + i*x_incr, y + i*y_incr)
            self.ctx.text_path(line)

    def draw_conf_text(self, text, x, y1, y2):
        with self.saved():
            font_size = 0.08
            self.ctx.set_font_size(font_size)

            if x == 0:
                left = 0.05
                top = (y1 + y2)/2 - 0.05
            else:
                left = 0.3
                top = 0.003 + (y1 + y2)/2

            # Shadow
            with self.saved():
                self.conf_text_path(text, 0.002+left, 0.003+top, 2.5*font_size, font_size)
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.fill()

            # Front text
            with self.saved():
                self.conf_text_path(text, left, top, 2.5*font_size, font_size)
                self.ctx.set_source_rgb(1, 1, 1)
                self.ctx.fill()

    def render(self, filename='affiche.png'):
        ys = [0.1, 0.3, 0.5, 0.7, 0.9]
        date = self.options.get('date', '')
        location = self.options.get('location', '')
        font = create_cairo_font_face_for_file(self.font,
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_face(font)

        for i in range(3):
            opts = self.options['conferences'][i]
            self.draw_conf(opts, (i+1) % 2, ys[i], ys[i+2])
        self.draw_pratical_infos(date, location)
        self.draw_constant_infos()
        self.surface.write_to_png(filename)
        print "Wrote", filename


class FacebookBanner(Affiche):
    SHOW_CONF_IMG = False

    TITLE_FONTSIZE = 0.3
    TITLE_POS = (0.02, 0.25)

    PLACE_SHADOW = True
    PLACE_POS = (0.02, 0.45)
    PLACE_FONTSIZE = 0.1
    DATE_POS = (0.02, 0.35)
    DATE_FONTSIZE = 0.1

    URL_POS = (0.97, 0.9)
    URL_FONTSIZE = 0.08
    DESCRIPTION_FONTSIZE = 0
    DISCLAIMER_FONTSIZE = 0

    LOGO_URLAB_SIZE = 0.17
    LOGO_URLAB_POS = (0.81, 0.55)

    LOGO_CI_SIZE = 0.13
    LOGO_CI_POS = (0.85, 0.27)

    QRCODE_SIZE = 0.07
    QRCODE_POS = (0.92, 0.03)

    width = 1200
    height = 628

    def conf_container_path(self, x, y1, y2):
        self.ctx.move_to(y1, 1-x)
        self.ctx.line_to((y1+y2)/2, x)
        self.ctx.line_to(y2, 1-x)

    def conf_text_path(self, text, x, y, x_incr, y_incr):
        # No conf text
        return

    def const_text_path(self, *args, **kwargs):
        self.ctx.scale(0.4, 1.1)
        super(FacebookBanner, self).const_text_path(*args, **kwargs)

if __name__ == "__main__":
    inFile = argv[1]
    options = yaml.load(open(inFile))

    outFile = argv[1].replace('.yaml', '.png')
    Affiche(options).render(outFile)

    fbFile = argv[1].replace('.yaml', '-fb.png')
    FacebookBanner(options).render(fbFile)

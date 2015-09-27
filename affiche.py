# -*- coding: utf-8 -*-

from sys import argv
from contextlib import contextmanager
import yaml
import cairo
from cairottf import create_cairo_font_face_for_file


def parse_css_color(css_color):
    return tuple(int(css_color[2*i+1:2*i+3], 16)/255. for i in range(3))


class Affiche(object):
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

    @contextmanager
    def saved(self):
        self.ctx.save()
        yield
        self.ctx.restore()

    def draw_pratical_infos(self, date_text, place):
        self.ctx.set_font_size(self.PLACE_FONTSIZE)
        self.ctx.move_to(*self.PLACE_POS)
        self.ctx.text_path(place)
        self.ctx.set_source_rgb(0.3, 0.3, 0.3)
        self.ctx.fill()

        self.ctx.set_font_size(self.DATE_FONTSIZE)
        self.ctx.move_to(*self.DATE_POS)
        self.ctx.text_path(date_text)
        self.ctx.set_source_rgb(1, 0.1, 0.3)
        self.ctx.fill()

    def draw_constant_infos(self):
        self.ctx.set_font_size(self.TITLE_FONTSIZE)
        self.ctx.move_to(*self.TITLE_POS)
        self.ctx.text_path("SmartMonday")

        self.ctx.set_font_size(self.DESCRIPTION_FONTSIZE)
        x, y = self.DESCRIPTION_POS
        self.ctx.move_to(x, y)
        self.ctx.text_path(u"Conférences")
        self.ctx.move_to(x, y+self.DESCRIPTION_FONTSIZE)
        self.ctx.text_path(u"gratuites en français")

        self.ctx.set_font_size(self.URL_FONTSIZE)
        self.ctx.move_to(*self.URL_POS)
        self.ctx.text_path(u"http://urlab.be/sm")
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.fill()

        self.ctx.move_to(*self.DISCLAIMER_POS)
        self.ctx.set_font_size(self.DISCLAIMER_FONTSIZE)
        self.ctx.text_path(
            u"Éditeur responsable: Cercle informatique, "
            u"Boulevard du Triomphe CP 206, 1050 Bruxelles")
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

    def draw_triangle(self, triangle_options, x, y1, y2):
        def triangle_path():
            self.ctx.move_to(x, y1)
            self.ctx.line_to(1-x, (y1+y2)/2)
            self.ctx.line_to(x, y2)

        imgfile = triangle_options.get('image', None)
        text = triangle_options.get('text', None).upper()
        color = triangle_options.get('color', "#ffffff")
        if isinstance(color, str) or isinstance(color, unicode):
            color = parse_css_color(color)
        if len(color) == 3:
            color = tuple(color) + (0.5,)

        # Image
        if imgfile:
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

        # Text
        if text:
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
                for i, line in enumerate(text.split('\n')):
                    self.ctx.move_to(
                        0.002 + left + i*font_size*2.5,
                        0.003 + top + i*font_size)
                    self.ctx.text_path(line)
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.fill()

                # Front text
                for i, line in enumerate(text.split('\n')):
                    self.ctx.move_to(
                        left + i*font_size*2.5,
                        top + i*font_size)
                    self.ctx.text_path(line)
                self.ctx.set_source_rgb(1, 1, 1)
                self.ctx.fill()

    def render(self, filename='affiche.png'):
        ys = [0.1, 0.3, 0.5, 0.7, 0.9]
        date = self.options.get('date', '')
        location = self.options.get('location', '')
        font = create_cairo_font_face_for_file(self.font, 
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.ctx.set_font_face(font)

        self.draw_pratical_infos(date, location)
        for i in range(3):
            opts = self.options['conferences'][i]
            self.draw_triangle(opts, (i+1) % 2, ys[i], ys[i+2])
        self.draw_constant_infos()
        self.surface.write_to_png(filename)
        print "Wrote", filename

if __name__ == "__main__":
    Affiche(yaml.load(open(argv[1]))).render(argv[1].replace('.yaml', '.png'))

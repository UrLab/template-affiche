# -*- coding: utf-8 -*-

from sys import argv
from contextlib import contextmanager
import yaml
import cairo


def parse_css_color(css_color):
    return tuple(int(css_color[2*i+1:2*i+3], 16)/255. for i in range(3))


class Affiche(object):
    def __init__(self, options):
        self.width = options.get('width', 2100)
        self.height = options.get('height', 2970)
        self.font = options.get('font', 'Sans')
        self.options = options
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.width, self.height)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(self.width, self.height)
        self.ctx.rectangle(0, 0, 1, 1)
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.fill()

    @contextmanager
    def saved(self):
        self.ctx.save()
        yield
        self.ctx.restore()

    def draw_triangle(self, triangle_options, x, y1, y2):
        def triangle_path():
            self.ctx.move_to(x, y1)
            self.ctx.line_to(1-x, (y1+y2)/2)
            self.ctx.line_to(x, y2)

        imgfile = triangle_options.get('image', None)
        text = triangle_options.get('text', None)
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
                self.ctx.select_font_face(
                    self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                font_size = 0.08
                self.ctx.set_font_size(font_size)

                if x == 0:
                    left = 0.05
                    top = (y1 + y2)/2 - 0.05
                else:
                    left = 0.3
                    top = 0.01 + (y1 + y2)/2

                for i, line in enumerate(text.split('\n')):
                    self.ctx.move_to(
                        0.002 + left + i*font_size*2.5,
                        0.003 + top + i*(font_size*0.9))
                    self.ctx.text_path(line)
                self.ctx.set_source_rgb(0, 0, 0)
                self.ctx.fill()

                for i, line in enumerate(text.split('\n')):
                    self.ctx.move_to(
                        left + i*font_size*2.5,
                        top + i*(font_size*0.9))
                    self.ctx.text_path(line)
                self.ctx.set_source_rgb(1, 1, 1)
                self.ctx.fill()

    def draw_pratical_infos(self, date_text, place):
        self.ctx.select_font_face(
                self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        self.ctx.set_font_size(0.05)
        self.ctx.move_to(0.02, 0.2)
        self.ctx.text_path(place)
        self.ctx.set_source_rgb(0.3, 0.3, 0.3)
        self.ctx.fill()

        self.ctx.set_font_size(0.05)
        self.ctx.move_to(0.02, 0.15)
        self.ctx.text_path(date_text)
        self.ctx.set_source_rgb(1, 0.1, 0.3)
        self.ctx.fill()

    def draw_constant_infos(self):
        self.ctx.select_font_face(
                self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        self.ctx.set_font_size(0.1)
        self.ctx.move_to(0.02, 0.1)
        self.ctx.text_path("SmartMonday")

        self.ctx.set_font_size(0.05)
        self.ctx.move_to(0.02, 0.82)
        self.ctx.text_path(u"Conférences")
        self.ctx.move_to(0.02, 0.86)
        self.ctx.text_path(u"gratuites en français")
        
        self.ctx.move_to(0.02, 0.97)
        self.ctx.text_path(u"http://urlab.be/sm")
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.fill()

        img = cairo.ImageSurface.create_from_png("logo_CI.png")
        rw = 0.2/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(0.5, 0.85)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

        img = cairo.ImageSurface.create_from_png("urlab.png")
        rw = 0.2/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(0.71, 0.85)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

        img = cairo.ImageSurface.create_from_png("smartMondayQR.png")
        rw = 0.20/float(img.get_width())
        rh = rw * self.width / self.height
        with self.saved():
            self.ctx.translate(0.75, 0.03)
            self.ctx.scale(rw, rh)
            self.ctx.set_source_surface(img, 0, 0)
            self.ctx.paint()

    def render(self, filename='affiche.png'):
        ys = [0.1, 0.3, 0.5, 0.7, 0.9]
        date = self.options.get('date', '')
        location = self.options.get('location', '')
        self.draw_pratical_infos(date, location)
        for i in range(3):
            opts = self.options['conferences'][i]
            self.draw_triangle(opts, (i+1) % 2, ys[i], ys[i+2])
        self.draw_constant_infos()
        self.surface.write_to_png(filename)
        print "Wrote", filename

if __name__ == "__main__":
    Affiche(yaml.load(open(argv[1]))).render(argv[1].replace('.yaml', '.png'))

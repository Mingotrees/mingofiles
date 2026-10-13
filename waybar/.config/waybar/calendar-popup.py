#!/usr/bin/env python3
"""A click-toggle, layer-shell month popup for Waybar's clock."""

import calendar
import datetime as dt
import json
from pathlib import Path
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, Gio, Gtk, GtkLayerShell


class CalendarPopup(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="local.waybar.CalendarPopup",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.window = None
        self.selected = dt.date.today()
        self.year, self.month = self.selected.year, self.selected.month

    def do_activate(self):
        if self.window is not None:
            self.quit()
            return

        provider = Gtk.CssProvider()
        provider.load_from_path(str(Path(__file__).with_name("calendar.css")))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_name("calendar-popup")
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        visual = self.window.get_screen().get_rgba_visual()
        if visual is not None:
            self.window.set_visual(visual)
        self.window.connect("key-press-event", self.on_key)

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, "waybar-calendar")
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        GtkLayerShell.set_exclusive_zone(self.window, -1)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self.window, edge, True)
        # Leave the bar clickable so another clock click toggles the popup off.
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.TOP, 40)
        self.choose_monitor()

        backdrop = Gtk.EventBox()
        backdrop.set_name("calendar-backdrop")
        backdrop.connect("button-press-event", self.on_backdrop_click)
        self.window.add(backdrop)

        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.panel.set_name("calendar-panel")
        self.panel.set_halign(Gtk.Align.CENTER)
        self.panel.set_valign(Gtk.Align.START)
        self.panel.set_margin_top(4)
        backdrop.add(self.panel)

        header = Gtk.Box(spacing=6)
        header.pack_start(self.button("‹", lambda *_: self.change_month(-1),
                                      "Previous month"), False, False, 0)
        self.heading = Gtk.Label()
        self.heading.set_name("calendar-heading")
        header.pack_start(self.heading, True, True, 0)
        header.pack_start(self.button("›", lambda *_: self.change_month(1),
                                      "Next month"), False, False, 0)
        header.pack_start(self.button("↻", self.reset, "Return to today"), False, False, 0)
        self.panel.pack_start(header, False, False, 0)

        self.grid = Gtk.Grid(column_spacing=3, row_spacing=3)
        self.grid.set_column_homogeneous(True)
        self.panel.pack_start(self.grid, False, False, 0)
        self.render_month()
        self.window.show_all()

    def choose_monitor(self):
        """Place the popup on Niri's active output when multiple screens exist."""
        try:
            result = subprocess.run(
                ["niri", "msg", "--json", "focused-output"],
                capture_output=True, text=True, timeout=1, check=True,
            )
            name = json.loads(result.stdout)["name"]
            screen = Gdk.Screen.get_default()
            display = Gdk.Display.get_default()
            for index in range(display.get_n_monitors()):
                if screen.get_monitor_plug_name(index) == name:
                    GtkLayerShell.set_monitor(self.window, display.get_monitor(index))
                    break
        except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError):
            pass

    @staticmethod
    def button(label, callback, tooltip):
        button = Gtk.Button(label=label)
        button.get_style_context().add_class("navigation")
        button.set_tooltip_text(tooltip)
        button.connect("clicked", callback)
        return button

    def render_month(self):
        for child in self.grid.get_children():
            self.grid.remove(child)
        self.heading.set_text(dt.date(self.year, self.month, 1).strftime("%B %Y").upper())
        for column, name in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            label = Gtk.Label(label=name)
            label.get_style_context().add_class("weekday")
            self.grid.attach(label, column, 0, 1, 1)

        weeks = calendar.Calendar(firstweekday=calendar.MONDAY).monthdatescalendar(
            self.year, self.month
        )
        # Keep popup height stable when changing months.
        while len(weeks) < 6:
            start = weeks[-1][-1] + dt.timedelta(days=1)
            weeks.append([start + dt.timedelta(days=i) for i in range(7)])
        for row, week in enumerate(weeks, start=1):
            for column, date in enumerate(week):
                button = Gtk.Button(label=str(date.day))
                button.set_tooltip_text(date.strftime("%A, %B %d, %Y"))
                context = button.get_style_context()
                context.add_class("day")
                if date.month != self.month:
                    context.add_class("other-month")
                elif column >= 5:
                    context.add_class("weekend")
                if date == dt.date.today():
                    context.add_class("today")
                if date == self.selected:
                    context.add_class("selected")
                button.connect("clicked", self.select_day, date)
                self.grid.attach(button, column, row, 1, 1)
        self.grid.show_all()

    def select_day(self, _button, date):
        self.selected = date
        self.year, self.month = date.year, date.month
        self.render_month()

    def change_month(self, offset):
        index = self.year * 12 + self.month - 1 + offset
        year, month = divmod(index, 12)
        if 1 <= year <= 9998:
            self.year, self.month = year, month + 1
            self.render_month()

    def reset(self, *_args):
        self.selected = dt.date.today()
        self.year, self.month = self.selected.year, self.selected.month
        self.render_month()

    def on_key(self, _window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.quit()
        elif event.keyval == Gdk.KEY_Left:
            self.change_month(-1)
        elif event.keyval == Gdk.KEY_Right:
            self.change_month(1)
        else:
            return False
        return True

    def on_backdrop_click(self, _backdrop, event):
        x, y = self.panel.translate_coordinates(_backdrop, 0, 0)
        allocation = self.panel.get_allocation()
        if x <= event.x < x + allocation.width and y <= event.y < y + allocation.height:
            return False
        self.quit()
        return True


if __name__ == "__main__":
    CalendarPopup().run(None)

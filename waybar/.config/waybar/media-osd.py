#!/usr/bin/env python3
"""Centered, transient volume and brightness indicator for Niri."""

import re
import subprocess
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk


COMMANDS = {
    "volume-up": ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "0.1+", "-l", "1.0"],
    "volume-down": ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "0.1-"],
    "volume-mute": ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"],
    "brightness-up": ["brightnessctl", "--class=backlight", "set", "+10%"],
    "brightness-down": ["brightnessctl", "--class=backlight", "set", "10%-"],
}


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip()


def state(kind):
    if kind == "volume":
        result = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        match = re.search(r"Volume:\s*([0-9.]+)", result)
        if not match:
            raise RuntimeError(f"Could not parse volume: {result}")
        muted = "[MUTED]" in result
        return round(float(match.group(1)) * 100), muted

    result = run(["brightnessctl", "-m", "--class=backlight", "info"])
    match = re.search(r",(\d+(?:\.\d+)?)%", result)
    if not match:
        raise RuntimeError(f"Could not parse brightness: {result}")
    return round(float(match.group(1))), False


def show():
    app = Gtk.Application(
        application_id="com.local.MediaOSD",
        flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
    )
    window = None
    hide_timer = None
    icon = title = value = meter = None

    def activate(application):
        nonlocal window, icon, title, value, meter
        window = Gtk.ApplicationWindow(application=application)
        window.set_title("Media OSD")
        window.set_default_size(360, 112)
        window.set_resizable(False)
        window.set_decorated(False)
        window.add_css_class("osd")

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=13)
        outer.set_margin_top(18)
        outer.set_margin_bottom(18)
        outer.set_margin_start(22)
        outer.set_margin_end(22)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        icon = Gtk.Label()
        icon.add_css_class("icon")
        title = Gtk.Label()
        title.add_css_class("title")
        value = Gtk.Label()
        value.set_hexpand(True)
        value.set_xalign(1)
        value.add_css_class("value")
        row.append(icon)
        row.append(title)
        row.append(value)

        meter = Gtk.ProgressBar()
        meter.add_css_class("meter")

        outer.append(row)
        outer.append(meter)
        window.set_child(outer)

    def command_line(application, command):
        nonlocal hide_timer
        action = command.get_arguments()[1]
        try:
            run(COMMANDS[action])
            kind = "volume" if action.startswith("volume-") else "brightness"
            percent, muted = state(kind)
        except (subprocess.CalledProcessError, RuntimeError) as error:
            print(error, file=sys.stderr)
            return 1
        if window is None:
            application.activate()
        icon.set_label(("󰖁" if muted else "󰕾") if kind == "volume" else "󰃠")
        title.set_label("Volume" if kind == "volume" else "Brightness")
        value.set_label("Muted" if muted else f"{percent}%")
        meter.set_fraction(0 if muted else max(0, min(percent, 100)) / 100)
        if not window.get_visible():
            window.present()
        if hide_timer is not None:
            GLib.source_remove(hide_timer)
        hide_timer = GLib.timeout_add(1450, application.quit)
        return 0

    css = b"""
    window.osd {
        background: #1b1e22;
        color: #dce1e5;
        border: 1px solid #33383e;
        border-radius: 18px;
    }
    window.osd > box { background: transparent; }
    .icon { color: #8bcac8; font-size: 24px; min-width: 32px; }
    .title { font-size: 15px; font-weight: 600; }
    .value { color: #aaaaaa; font-size: 14px; }
    progressbar.meter trough { min-height: 7px; background: #33383e; border-radius: 5px; }
    progressbar.meter progress { min-height: 7px; background: #8bcac8; border-radius: 5px; }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    app.connect("activate", activate)
    app.connect("command-line", command_line)
    return app.run(sys.argv)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"Usage: {sys.argv[0]} <{'|'.join(COMMANDS)}>")

    raise SystemExit(show())


if __name__ == "__main__":
    main()

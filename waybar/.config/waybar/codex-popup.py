#!/usr/bin/env python3
"""Toggle a Codex usage panel from Waybar."""
import importlib.util
import os
from pathlib import Path
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gdk, Gio, GLib, Gtk, GtkLayerShell

# Share the monitor selection and outside-click behavior with the clock popup.
spec = importlib.util.spec_from_file_location('calendar_popup', Path(__file__).with_name('calendar-popup.py'))
calendar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calendar)
spec = importlib.util.spec_from_file_location('codex_usage', Path(__file__).with_name('codex-usage.py'))
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)


class CodexPopup(calendar.CalendarPopup):
    def __init__(self):
        Gtk.Application.__init__(self, application_id='local.waybar.CodexUsage', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None

    def do_activate(self):
        if self.window is not None:
            self.quit()
            return
        provider = Gtk.CssProvider()
        provider.load_from_path(str(Path(__file__).with_name('codex-popup.css')))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_name('codex-popup')
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        visual = self.window.get_screen().get_rgba_visual()
        if visual:
            self.window.set_visual(visual)
        self.window.connect('key-press-event', self.on_key)
        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, 'waybar-codex')
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        GtkLayerShell.set_exclusive_zone(self.window, -1)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self.window, edge, True)
        GtkLayerShell.set_margin(self.window, GtkLayerShell.Edge.TOP, 40)
        self.choose_monitor()
        backdrop = Gtk.EventBox()
        backdrop.set_name('codex-backdrop')
        backdrop.connect('button-press-event', self.on_backdrop_click)
        self.window.add(backdrop)
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.panel.set_name('codex-panel')
        self.panel.set_halign(Gtk.Align.END)
        self.panel.set_valign(Gtk.Align.START)
        self.panel.set_margin_top(4)
        self.panel.set_margin_end(8)
        self.panel.set_size_request(340, -1)
        backdrop.add(self.panel)
        header = Gtk.Box(spacing=12)
        icon = self.label('󰚩', 'agent-icon')
        header.pack_start(icon, False, False, 0)
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        titles.pack_start(self.label('CODEX', 'agent-title'), False, False, 0)
        self.plan = self.label('Usage limits', 'muted')
        titles.pack_start(self.plan, False, False, 0)
        header.pack_start(titles, True, True, 0)
        for text, callback, tip in [('↻', self.refresh, 'Refresh local usage'), ('×', lambda *_: self.quit(), 'Close')]:
            button = Gtk.Button(label=text)
            button.set_tooltip_text(tip)
            button.connect('clicked', callback)
            header.pack_start(button, False, False, 0)
        self.panel.pack_start(header, False, False, 0)
        self.panel.pack_start(Gtk.Separator(), False, False, 0)
        self.panel.pack_start(self.label('USAGE REMAINING', 'section-title'), False, False, 0)
        self.rows = {}
        for key, title in [('primary', 'Session (5h)'), ('secondary', 'Weekly')]:
            group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
            line = Gtk.Box()
            line.pack_start(self.label(title), True, True, 0)
            percent = self.label('—')
            line.pack_end(percent, False, False, 0)
            group.pack_start(line, False, False, 0)
            bar = Gtk.ProgressBar()
            group.pack_start(bar, False, False, 0)
            reset = self.label('', 'muted')
            group.pack_start(reset, False, False, 0)
            self.panel.pack_start(group, False, False, 0)
            self.rows[key] = (percent, bar, reset)
        self.panel.pack_start(Gtk.Separator(), False, False, 0)
        self.updated = self.label('', 'muted')
        self.updated.set_xalign(0.5)
        self.panel.pack_start(self.updated, False, False, 0)
        self.refresh()
        GLib.timeout_add_seconds(30, self.refresh)
        self.window.show_all()

    @staticmethod
    def label(text, style=None):
        label = Gtk.Label(label=text, xalign=0)
        if style:
            label.get_style_context().add_class(style)
        return label

    def on_key(self, _window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.quit()
            return True
        return False

    def refresh(self, *_args):
        root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
        try:
            snapshot = usage.latest_snapshot(root)
            now = time.time()
            timestamp, limits = snapshot if snapshot else (now, {})
            plan = limits.get('plan_type')
            self.plan.set_text(f'{plan.title()} · local usage' if plan else 'Local usage')
            for key, (percent, bar, reset) in self.rows.items():
                window = limits.get(key) or {}
                used = float(window.get('used_percent', 0))
                end = window.get('resets_at')
                expired = end is not None and end <= now
                percent.set_text(f'{max(0, 100 - used):g}%' if window and not expired else '—')
                bar.set_fraction(max(0, min(1, (100 - used) / 100)) if window and not expired else 0)
                context = bar.get_style_context()
                for name, active in [('warning', used >= 80), ('critical', used >= 95)]:
                    context.add_class(name) if active else context.remove_class(name)
                if expired:
                    message = 'Reset passed · awaiting Codex update'
                elif end:
                    minutes = max(1, int((end - now) / 60))
                    days, hours = divmod(minutes // 60, 24)
                    message = f'Resets in {days}d {hours}h' if days else f'Resets in {hours}h {minutes % 60}m'
                else:
                    message = 'Awaiting Codex usage data'
                reset.set_text(message)
            age = max(0, int((now - timestamp) / 60))
            self.updated.set_text(('Updated just now' if age == 0 else f'Updated {age}m ago') if snapshot else 'Use Codex to populate usage')
            self.updated.set_tooltip_text('Local snapshots refresh when Codex reports usage. No API requests are made.')
        except (OSError, ValueError, TypeError, OverflowError):
            self.updated.set_text('Usage data unavailable')
        return True


if __name__ == '__main__':
    CodexPopup().run(None)

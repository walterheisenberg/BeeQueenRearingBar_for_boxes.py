# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import boxes
from boxes.lids import LidSettings


class NotchedEdge(boxes.edges.BaseEdge):
    """Oberkante mit rechteckigen Einkerbungen.

    Die erste Einkerbung beginnt im Abstand notch_spacing vom Anfang der Kante
    (Innenseite der Wand), danach folgen die Einkerbungen im Abstand
    notch_spacing. Der Restplatz bleibt am anderen Ende der Kante frei
    (mindestens ebenfalls notch_spacing).

    notch_count > 0: genau diese Anzahl Einkerbungen.
    notch_count == 0: so viele Einkerbungen, wie auf die Kante passen.
    notch_radius: Abrundung der beiden oberen (äußeren) Ecken jeder Einkerbung.
    """

    def __init__(
        self,
        box,
        settings,
        notch_width,
        notch_spacing,
        notch_depth,
        notch_count=0,
        notch_radius=0.0,
    ):
        super().__init__(box, settings)
        self.notch_width = notch_width
        self.notch_spacing = notch_spacing
        self.notch_depth = notch_depth
        self.notch_count = notch_count
        self.notch_radius = notch_radius

    @staticmethod
    def max_count(length, width, spacing):
        """Maximale Anzahl Einkerbungen (Abstand 'spacing' vorn, zwischen den
        Einkerbungen und am Ende)."""
        return max(int((length - spacing) / (width + spacing) + 1e-6), 0)

    @staticmethod
    def needed_length(count, width, spacing):
        """Benötigte Kantenlänge für 'count' Einkerbungen."""
        return count * width + (count + 1) * spacing

    def __call__(self, length, **kw):
        w = self.notch_width
        s = self.notch_spacing
        d = self.notch_depth
        r = self.notch_radius

        if self.notch_count > 0:
            n = self.notch_count
        else:
            n = self.max_count(length, w, s)
        if n < 1:
            self.boxes.edge(length)
            return

        # Restplatz am Ende der Kante
        rest = length - s - n * w - (n - 1) * s

        b = self.boxes
        b.edge(s - r)
        for i in range(n):
            b.corner(90, r)
            b.edge(d - r)
            b.corner(-90)
            b.edge(w)
            b.corner(-90)
            b.edge(d - r)
            b.corner(90, r)
            if i < n - 1:
                b.edge(s - 2 * r)
            else:
                b.edge(rest - r)


class MiniBivoBox(boxes.Boxes):
    """Mini-Bivo-Box mit Overthetop-Deckel, Lüftungsschlitzen und Einkerbungen"""

    description = """Einfache Box mit Overthetop-Deckel. An den Wänden sind waagerechte
    Lüftungsschlitze (Standard: 25 x 4,2 mm); jede weitere Reihe ist um 50 % der
    Schlitzlänge versetzt (Ziegelmuster). An den Oberkanten der Seitenwände sind
    Einkerbungen (Standard: 20 mm breit, 5 mm Abstand, 5 mm tief, 1 mm Rundung an
    den oberen Ecken). Lüftungsschlitze
    und Einkerbungen gibt es nur an der linken und rechten Seite; die Schlitze
    lassen sich für jede der beiden Seiten einzeln an- und abwählen."""

    ui_group = "Box"

    SIDES = ("front", "back", "left", "right")
    SLOT_SIDES = ("left", "right")
    NOTCH_SIDES = ("left", "right")

    def __init__(self) -> None:
        boxes.Boxes.__init__(self)
        self.addSettingsArgs(boxes.edges.FingerJointSettings)
        self.addSettingsArgs(LidSettings, style="overthetop")
        self.buildArgParser("x", "y", "h", "outside", "bottom_edge")
        self.argparser.set_defaults(x=81.0, y=200.0, h=100.0)

        # -----------------------------------------------------------------
        # UNTERMENÜ: STAPELFÜSSE (nur bei Bottom-Edge "s" / "š")
        # -----------------------------------------------------------------
        foot_group = self.argparser.add_argument_group("Stapelfüße (absolute Maße)")
        foot_group.add_argument(
            "--foot_height",
            action="store",
            type=float,
            default=6.0,
            help="Höhe der Füße in mm (unabhängig von der Materialdicke)",
        )
        foot_group.add_argument(
            "--foot_width",
            action="store",
            type=float,
            default=12.0,
            help="Breite der Füße in mm (unabhängig von der Materialdicke)",
        )

        # -----------------------------------------------------------------
        # UNTERMENÜ: LÜFTUNGSSCHLITZE
        # -----------------------------------------------------------------
        slot_group = self.argparser.add_argument_group("Lüftungsschlitze")
        for side in self.SLOT_SIDES:
            slot_group.add_argument(
                f"--slots_{side}",
                action="store",
                type=boxes.boolarg,
                default=True,
                help=f"Lüftungsschlitze an der Seite '{side}'",
            )
        slot_group.add_argument(
            "--slot_length",
            action="store",
            type=float,
            default=25.0,
            help="Länge der Lüftungsschlitze in mm (waagerecht)",
        )
        slot_group.add_argument(
            "--slot_width",
            action="store",
            type=float,
            default=4.2,
            help="Breite (Höhe) der Lüftungsschlitze in mm",
        )
        slot_group.add_argument(
            "--slot_separation",
            action="store",
            type=float,
            default=3.0,
            help="Abstand zwischen den übereinanderliegenden Schlitzreihen in mm",
        )
        slot_group.add_argument(
            "--slot_min_spacing",
            action="store",
            type=float,
            default=6.0,
            help="Abstand zwischen den Schlitzen einer Reihe in mm",
        )
        slot_group.add_argument(
            "--slot_radius",
            action="store",
            type=float,
            default=2.1,
            help="Eckenradius der Schlitze in mm",
        )
        slot_group.add_argument(
            "--slot_top_margin",
            action="store",
            type=float,
            default=10.0,
            help="Abstand der obersten Schlitzreihe zur Oberseite in mm (bei Wänden mit Einkerbungen ab Unterkante der Einkerbungen)",
        )
        slot_group.add_argument(
            "--slot_bottom_margin",
            action="store",
            type=float,
            default=22.0,
            help="Mindestabstand der untersten Schlitzreihe zur Unterseite in mm",
        )
        slot_group.add_argument(
            "--slot_margin",
            action="store",
            type=float,
            default=10.0,
            help="Mindestabstand der Schlitze zu den senkrechten Wandkanten in mm (zusätzlich zur Materialdicke)",
        )
        slot_group.add_argument(
            "--slot_count",
            action="store",
            type=int,
            default=0,
            help="Maximale Anzahl Schlitzreihen pro Wand (0 = so viele wie passen)",
        )

        # -----------------------------------------------------------------
        # UNTERMENÜ: EINKERBUNGEN AN DEN OBERKANTEN
        # -----------------------------------------------------------------
        notch_group = self.argparser.add_argument_group("Einkerbungen an der Oberseite")
        notch_group.add_argument(
            "--notch_count",
            action="store",
            type=int,
            default=0,
            help="Anzahl der Einkerbungen pro Oberkante (0 = so viele wie auf die ganze Breite passen)",
        )
        notch_group.add_argument(
            "--notch_width",
            action="store",
            type=float,
            default=20.0,
            help="Breite der Einkerbungen in mm",
        )
        notch_group.add_argument(
            "--notch_spacing",
            action="store",
            type=float,
            default=5.0,
            help="Abstand der ersten Einkerbung von der Innenseite der Wand und zwischen den Einkerbungen in mm; der Restplatz bleibt am anderen Ende frei (dort mindestens ebenfalls dieser Abstand)",
        )
        notch_group.add_argument(
            "--notch_radius",
            action="store",
            type=float,
            default=1.0,
            help="Radius der Abrundung an den oberen Ecken der Einkerbungen in mm (0 = scharfkantig)",
        )
        notch_group.add_argument(
            "--notch_depth",
            action="store",
            type=float,
            default=5.0,
            help="Tiefe der Einkerbungen in mm",
        )

    # ------------------------------------------------------------------
    # Hilfsfunktionen
    # ------------------------------------------------------------------
    def _absolute_feet(self):
        """Füße (und die passenden Aussparungen oben) mit festen Maßen.

        In boxes.py sind 'height' und 'width' der Stackable-Kanten Vielfache
        der Materialdicke (relative_params). Dadurch werden die Füße bei
        dickerem Material größer und passen nicht mehr auf Boxen mit anderer
        Dicke. Hier werden beide Werte absolut in mm gesetzt.
        """
        seen = set()
        for char in "sSšŠ":
            edge = self.edges.get(char)
            st = getattr(edge, "settings", None)
            if st is None or id(st) in seen or not hasattr(st, "setValues"):
                continue
            seen.add(id(st))
            st.setValues(
                self.thickness,
                relative=False,
                height=self.foot_height,
                width=self.foot_width,
            )

    def _has_slots(self, side):
        return side in self.SLOT_SIDES and getattr(self, f"slots_{side}")

    def _has_notches(self, side):
        return side in self.NOTCH_SIDES

    def _top_clear(self, side):
        """Höhe, die oben durch Einkerbungen belegt ist."""
        return self.notch_depth if self._has_notches(side) else 0.0

    def _slot_rows(self, wall_h, top_clear):
        """Anzahl der übereinanderliegenden Schlitzreihen, die in die Wand passen."""
        w = self.slot_width
        sep = self.slot_separation
        avail = wall_h - top_clear - self.slot_top_margin - self.slot_bottom_margin
        n = int((avail + sep) / (w + sep) + 1e-6)
        if self.slot_count > 0:
            n = min(n, self.slot_count)
        return max(n, 0)

    def _slot_layout(self, wall_w):
        """Raster der Schlitze einer Reihe.

        Der Abstand zwischen zwei Schlitzen einer Reihe ist slot_min_spacing.
        Ungerade Reihen sind um die halbe Schlitzlänge nach rechts versetzt
        (die Reihe darunter beginnt also in der Mitte des Schlitzes darüber).
        Das gesamte Muster wird auf der Wand mittig ausgerichtet.

        Liefert (x0, pitch, n_even, n_odd): x0 ist die linke Kante des ersten
        Schlitzes einer geraden Reihe, pitch der Abstand von Schlitzanfang zu
        Schlitzanfang, n_even / n_odd die Schlitzanzahl in geraden bzw.
        ungeraden Reihen.
        """
        length = self.slot_length
        spacing = self.slot_min_spacing
        pitch = length + spacing
        half = length / 2.0

        x_min = self.thickness + self.slot_margin
        usable = wall_w - 2 * x_min

        n_even = max(int((usable + spacing) / pitch + 1e-6), 1)
        n_odd = max(int((usable - half + spacing) / pitch + 1e-6), 0)

        end_even = n_even * length + (n_even - 1) * spacing
        end_odd = half + n_odd * length + (n_odd - 1) * spacing if n_odd else 0.0
        extent = max(end_even, end_odd)

        x0 = x_min + (usable - extent) / 2.0
        return x0, pitch, n_even, n_odd

    def _slots_callback(self, wall_w, wall_h, top_clear):
        """Liefert eine Funktion, die die Lüftungsschlitze in eine Wand zeichnet.

        Gerade Reihen (0, 2, ...) beginnen bei x0, ungerade Reihen (1, 3, ...)
        beginnen bei x0 + halbe Schlitzlänge (Ziegelmuster).
        """

        def draw():
            w = self.slot_width
            sep = self.slot_separation
            rows = self._slot_rows(wall_h, top_clear)
            x0, pitch, n_even, n_odd = self._slot_layout(wall_w)
            half = self.slot_length / 2.0

            y_top = wall_h - top_clear - self.slot_top_margin
            for row in range(rows):
                yc = y_top - w / 2.0 - row * (w + sep)

                if row % 2 == 0:
                    count, xs = n_even, x0
                else:
                    count, xs = n_odd, x0 + half

                for i in range(count):
                    xc = xs + i * pitch + self.slot_length / 2.0
                    self.rectangularHole(
                        xc,
                        yc,
                        self.slot_length,
                        w,
                        r=self.slot_radius,
                    )

        return draw

    def _check_parameters(self, x, y, h):
        # Stapelfüße
        if self.bottom_edge in ("s", "š"):
            if self.foot_height <= 0 or self.foot_width <= 0:
                raise ValueError("Höhe und Breite der Füße müssen größer als 0 sein")
            st = self.edges[self.bottom_edge].settings
            r = st.height / 2.0 / (1 - math.cos(math.radians(st.angle)))
            l = r * math.sin(math.radians(st.angle))
            need = 2 * st.width + 4 * l
            if min(x, y) < need:
                raise ValueError(
                    f"Füße zu groß für die Box: kürzeste Bodenkante mindestens "
                    f"{need:.1f} mm nötig, aktuell {min(x, y):.1f} mm"
                )

        # Einkerbungen
        notch_sides = [s for s in self.SIDES if self._has_notches(s)]
        if notch_sides:
            if (
                self.notch_width <= 0
                or self.notch_spacing <= 0
                or self.notch_depth <= 0
            ):
                raise ValueError(
                    "Breite, Abstand und Tiefe der Einkerbungen müssen größer als 0 sein"
                )
            if self.notch_depth >= h:
                raise ValueError("Einkerbungen sind tiefer als die Wand hoch ist")
            if self.notch_count < 0:
                raise ValueError("Anzahl der Einkerbungen darf nicht negativ sein")
            if self.notch_radius < 0:
                raise ValueError("Radius der Abrundung darf nicht negativ sein")
            if self.notch_radius > self.notch_depth:
                raise ValueError(
                    f"Radius der Abrundung ({self.notch_radius:.1f} mm) darf nicht "
                    f"größer als die Tiefe der Einkerbungen ({self.notch_depth:.1f} mm) sein"
                )
            if 2 * self.notch_radius > self.notch_spacing:
                raise ValueError(
                    f"Radius der Abrundung zu groß: der Abstand der Einkerbungen "
                    f"({self.notch_spacing:.1f} mm) muss mindestens doppelt so groß "
                    f"wie der Radius sein"
                )

            for side in notch_sides:
                wall_w = x if side in ("front", "back") else y
                max_n = NotchedEdge.max_count(
                    wall_w, self.notch_width, self.notch_spacing
                )
                if self.notch_count == 0:
                    if max_n < 1:
                        need = NotchedEdge.needed_length(
                            1, self.notch_width, self.notch_spacing
                        )
                        raise ValueError(
                            f"Seite '{side}' zu schmal für Einkerbungen: mindestens "
                            f"{need:.1f} mm nötig, aktuell {wall_w:.1f} mm"
                        )
                elif self.notch_count > max_n:
                    need = NotchedEdge.needed_length(
                        self.notch_count, self.notch_width, self.notch_spacing
                    )
                    raise ValueError(
                        f"{self.notch_count} Einkerbungen passen nicht auf die Seite "
                        f"'{side}': {need:.1f} mm nötig, aktuell {wall_w:.1f} mm "
                        f"(maximal {max_n} möglich)"
                    )

        # Lüftungsschlitze
        slot_sides = [s for s in self.SIDES if self._has_slots(s)]
        if not slot_sides:
            return

        if min(self.slot_length, self.slot_width, self.slot_separation) <= 0:
            raise ValueError(
                "Länge, Breite und Abstand der Schlitze müssen größer als 0 sein"
            )
        if self.slot_min_spacing < 0:
            raise ValueError("Mindestabstand der Schlitze darf nicht negativ sein")
        max_radius = min(self.slot_length, self.slot_width) / 2.0
        if self.slot_radius < 0 or self.slot_radius > max_radius:
            raise ValueError(
                f"Eckenradius der Schlitze muss zwischen 0 und {max_radius:.1f} mm liegen"
            )

        for side in slot_sides:
            wall_w = x if side in ("front", "back") else y
            need_w = self.slot_length + 2 * (self.thickness + self.slot_margin)
            if wall_w < need_w:
                raise ValueError(
                    f"Seite '{side}' zu schmal für die Schlitze: mindestens {need_w:.1f} mm "
                    f"nötig, aktuell {wall_w:.1f} mm"
                )
            if self._slot_rows(h, self._top_clear(side)) < 1:
                need_h = (
                    self._top_clear(side)
                    + self.slot_top_margin
                    + self.slot_bottom_margin
                    + self.slot_width
                )
                raise ValueError(
                    f"Seite '{side}' zu niedrig für die Schlitze: mindestens {need_h:.1f} mm "
                    f"nötig, aktuell {h:.1f} mm"
                )

    # ------------------------------------------------------------------
    # Rendern
    # ------------------------------------------------------------------
    def render(self):
        self._absolute_feet()
        x, y, h = self.x, self.y, self.h

        b = self.edges.get(self.bottom_edge, self.edges["F"])
        sideedge = "F"

        if self.outside:
            self.x = x = self.adjustSize(x, sideedge, sideedge)
            self.y = y = self.adjustSize(y)
            self.h = h = self.adjustSize(h, b, "e")

        self._check_parameters(x, y, h)

        notched = NotchedEdge(
            self,
            None,
            self.notch_width,
            self.notch_spacing,
            self.notch_depth,
            self.notch_count,
            self.notch_radius,
        )
        plain = self.edges["e"]

        width = {"front": x, "back": x, "left": y, "right": y}
        top = {s: notched if self._has_notches(s) else plain for s in self.SIDES}
        callback = {
            s: [self._slots_callback(width[s], h, self._top_clear(s))]
            if self._has_slots(s)
            else None
            for s in self.SIDES
        }

        with self.saved_context():
            self.rectangularWall(
                x,
                h,
                [b, sideedge, top["front"], sideedge],
                ignore_widths=[1, 6],
                callback=callback["front"],
                move="up",
            )
            self.rectangularWall(
                x,
                h,
                [b, sideedge, top["back"], sideedge],
                ignore_widths=[1, 6],
                callback=callback["back"],
                move="up",
            )

            if self.bottom_edge != "e":
                self.rectangularWall(x, y, "ffff", move="up")
            self.lid(x, y)

        self.rectangularWall(
            x,
            h,
            [b, sideedge, top["back"], sideedge],
            ignore_widths=[1, 6],
            move="right only",
        )
        self.rectangularWall(
            y,
            h,
            [b, "f", top["left"], "f"],
            ignore_widths=[1, 6],
            callback=callback["left"],
            move="up",
        )
        self.rectangularWall(
            y,
            h,
            [b, "f", top["right"], "f"],
            ignore_widths=[1, 6],
            callback=callback["right"],
            move="up",
        )

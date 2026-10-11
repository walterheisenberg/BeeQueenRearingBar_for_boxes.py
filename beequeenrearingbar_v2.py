# Copyright (C) 2026 Ralf Lindlein <lindlein@gmx.com>
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


class BeeQueenRearingBar(boxes.Boxes):
    """Zuchtleisten und Abstandhalter für die Seiten der Rähmchen"""

    description = """Zuchtleisten mit variabler Reihenanzahl und zentrierten Bohrungen,
    nebeneinander gezeichnet, Abstandhalter für die Seiten der Rähmchen möglich.
    Die Lochanzahl ergibt sich automatisch aus Länge, Randabstand, Lochdurchmesser
    und Lochabstand (Standard: 25 mm). Bei den Abstandhaltern können die
    Verbindungsstege nach dem Einkleben einfach mit dem Cuttermesser abgeschnitten
    werden."""

    ui_group = "Misc"

    MIN_WALL = 1.0  # mm, kleinster erlaubter Steg zwischen zwei Löchern
    EPS = 1e-6  # Toleranz gegen Fließkommafehler
    MARGIN_BETWEEN = 5.0  # mm Abstand zwischen den Bauteilen

    def __init__(self) -> None:
        super().__init__()

        # -----------------------------------------------------------------
        # PARAMETER FÜR DIE ZUCHTLEISTE (HAUPTMENÜ)
        # -----------------------------------------------------------------
        self.argparser.add_argument(
            "--draw_mode",
            action="store",
            type=str,
            default="all",
            choices=["all", "spacers_only", "bar_only"],
            help="Ausgabe wählen: all (Zuchtleiste & Abstandhalter), spacers_only (Nur Abstandhalter), bar_only (Nur Leiste)",
        )
        self.argparser.add_argument(
            "--length",
            action="store",
            type=float,
            default=400.0,
            help="Länge der Leiste in mm (z. B. 400 mm für Zander)",
        )
        self.argparser.add_argument(
            "--bar_width",
            action="store",
            type=float,
            default=25.0,
            help="Breite der Leiste in mm (Default: 25mm), bestimmt auch die Höhe der Abstandhalter",
        )
        self.argparser.add_argument(
            "--hole_diameter",
            action="store",
            type=float,
            default=8.5,
            help="Durchmesser der Löcher in mm (8,5mm für Nicot Näpfchen, 18mm für die gelben Nicot-Halter, 3mm für JZBZ)",
        )
        self.argparser.add_argument(
            "--pitch_x",
            action="store",
            type=float,
            default=25.0,
            help="Lochabstand innerhalb einer Reihe in mm (für Nicot-Näpfchen sind 25mm der Standard nach Ralf Kolbe)",
        )
        self.argparser.add_argument(
            "--rows",
            action="store",
            type=int,
            default=2,
            choices=[1, 2],
            help="Anzahl der Reihen (1 oder 2)",
        )
        self.argparser.add_argument(
            "--margin_x_min",
            action="store",
            type=float,
            default=20.0,
            help="Mindestabstand von der Stirnseite bis zur Außenkante des ersten Lochs in mm",
        )
        self.argparser.add_argument(
            "--margin_y",
            action="store",
            type=float,
            default=4.0,
            help="Mindestabstand der Löcher von der Längskante in mm",
        )

        # -----------------------------------------------------------------
        # UNTERMENÜ: PARAMETER FÜR DIE ABSTANDHALTER
        # -----------------------------------------------------------------
        frame_group = self.argparser.add_argument_group(
            "Abstandhalter für die Seiten am Rähmchen"
        )
        frame_group.add_argument(
            "--bars_count",
            action="store",
            type=int,
            default=2,
            choices=[1, 2, 3],
            help="Anzahl der unterzubringenden Zuchtleisten (1-3)",
        )
        frame_group.add_argument(
            "--bar_thickness",
            action="store",
            type=float,
            default=6.0,
            help="Dicke der Zuchtleiste in mm (Default: 6.0mm), bestimmt die Breite der Schlitze",
        )
        frame_group.add_argument(
            "--first_rect_width",
            action="store",
            type=float,
            default=10.0,
            help="Breite des ersten (äußeren) Abstandhalters in mm (Default: 10mm)",
        )
        frame_group.add_argument(
            "--rect_width",
            action="store",
            type=float,
            default=30.0,
            help="Abstand der Zuchtleisten in mm = Breite der folgenden Abstandhalter (Default: 30mm)",
        )
        frame_group.add_argument(
            "--bridge_width",
            action="store",
            type=float,
            default=0.8,
            help="Dicke der Verbindungsstege in mm (Default: 0.8mm)",
        )
        frame_group.add_argument(
            "--edge_offset",
            action="store",
            type=float,
            default=4.0,
            help="Abstand der Stege von Ober- und Unterkante in mm (Default: 4mm)",
        )
        frame_group.add_argument(
            "--corner_radius",
            action="store",
            type=float,
            default=1.5,
            help="Eckenrundung der Abstandhalter in mm (Default: 1.5mm)",
        )
        frame_group.add_argument(
            "--round_first_rect",
            action="store",
            type=boxes.boolarg,
            default=True,
            help="Außenecken des ersten Abstandhalters (links) abrunden",
        )
        frame_group.add_argument(
            "--round_last_rect",
            action="store",
            type=boxes.boolarg,
            default=True,
            help="Außenecken des letzten Abstandhalters (rechts) abrunden",
        )
        frame_group.add_argument(
            "--spacer_sets",
            action="store",
            type=int,
            default=2,
            help="Anzahl der Sätze nebeneinander (2 = beide Rähmchenseiten)",
        )

    # =====================================================================
    # TEIL 1: ZUCHTLEISTE
    # =====================================================================
    def _check_bar_parameters(self):
        d = self.hole_diameter

        if self.pitch_x <= 0:
            raise ValueError("Lochabstand muss größer als 0 sein")
        if self.length - 2 * self.margin_x_min - d < 0:
            raise ValueError("Leiste zu kurz für Randabstand und Lochdurchmesser")
        if d + self.MIN_WALL > self.pitch_x:
            raise ValueError(
                f"Lochabstand zu klein: mindestens {d + self.MIN_WALL:.1f} mm "
                "für diesen Lochdurchmesser nötig"
            )
        if self.bar_width < d + 2 * self.margin_y:
            raise ValueError(
                f"Leiste zu schmal: mindestens {d + 2 * self.margin_y:.1f} mm nötig "
                f"(Lochdurchmesser {d:.1f} mm + 2 x Randabstand {self.margin_y:.1f} mm), "
                f"aktuelle Breite {self.bar_width:.1f} mm"
            )
        if self.rows == 2:
            dy = self.bar_width - 2 * self.margin_y - d  # Mittenabstand der Reihen
            if math.hypot(self.pitch_x / 2.0, dy) < d + self.MIN_WALL:
                raise ValueError("Löcher der beiden Reihen würden sich überlappen")

    def _hole_positions(self):
        """Liefert alle Lochmittelpunkte als Liste von (x, y)."""
        p = self.pitch_x
        r = self.hole_diameter / 2.0

        x_min = self.margin_x_min + r
        available = self.length - 2 * self.margin_x_min - 2 * r

        # Maximale Lochanzahl der vollen Reihe
        k = int(available / p + self.EPS) + 1

        if self.rows == 1:
            y_pos = [self.bar_width / 2.0]
            counts, offsets = [k], [0.0]
            span = (k - 1) * p
        else:
            y_edge = self.margin_y + r
            y_pos = [y_edge, self.bar_width - y_edge]
            offsets = [0.0, p / 2.0]
            span_even = (k - 1) * p + p / 2.0
            if span_even <= available + self.EPS:
                counts, span = [k, k], span_even  # gerade Gesamtanzahl
            else:
                counts, span = [k, k - 1], (k - 1) * p  # ungerade Gesamtanzahl

        # Alles mittig auf der Leiste platzieren
        start = x_min + (available - span) / 2.0

        return [
            (start + off + i * p, y)
            for y, n, off in zip(y_pos, counts, offsets)
            for i in range(n)
        ]

    def _draw_bar_label(self, hole_count):
        self.ctx.save()
        self.ctx.translate(8.0, self.bar_width / 2.0)
        self.ctx.rotate(math.radians(90))
        self.text(
            f"{hole_count}x",
            x=0,
            y=-2.5,
            fontsize=8,
            align="center",
            color=boxes.Color.ANNOTATIONS,
        )
        self.text(
            f"⌀ {self.hole_diameter:.1f}mm",
            x=0,
            y=-9,
            fontsize=4,
            align="center",
            color=boxes.Color.ANNOTATIONS,
        )
        self.ctx.restore()

    def draw_bar(self):
        """Zeichnet eine Zuchtleiste inkl. Bohrungen & Beschriftung."""
        r = self.hole_diameter / 2.0
        positions = self._hole_positions()

        for x, y in positions:
            self.hole(x, y, r=r)

        self.polyline(
            self.length, 90, self.bar_width, 90, self.length, 90, self.bar_width, 90
        )

        if getattr(self, "labels", True):
            self._draw_bar_label(len(positions))

    # =====================================================================
    # TEIL 2: ABSTANDHALTER
    # =====================================================================
    @property
    def _r_first(self):
        return self.corner_radius if self.round_first_rect else 0.0

    @property
    def _r_last(self):
        return self.corner_radius if self.round_last_rect else 0.0

    @property
    def _spacer_total_width(self):
        return self.first_rect_width + self.bars_count * (
            self.rect_width + self.bar_thickness
        )

    @staticmethod
    def _corner(r):
        """Ecke mit Radius r, bei r = 0 eine scharfe Ecke."""
        return (90, r) if r > 0 else 90

    def _check_spacer_parameters(self):
        r = self.corner_radius
        o = self.edge_offset
        bw = self.bridge_width

        if self.spacer_sets < 1:
            raise ValueError("Mindestens ein Satz Abstandhalter nötig")
        if self.bar_thickness <= 0 or bw <= 0 or r < 0:
            raise ValueError(
                "Leistendicke und Stegdicke müssen größer als 0, die Eckenrundung nicht negativ sein"
            )
        if o < r:
            raise ValueError(
                f"Stegabstand zu klein: mindestens die Eckenrundung ({r:.1f} mm) nötig, "
                f"aktuell {o:.1f} mm"
            )

        min_height = 2 * (o + bw)
        if self.bar_width <= min_height:
            raise ValueError(
                f"Abstandhalter zu niedrig: Breite der Zuchtleiste muss größer als "
                f"{min_height:.1f} mm sein (2 x (Stegabstand {o:.1f} mm + Stegdicke {bw:.1f} mm)), "
                f"aktuell {self.bar_width:.1f} mm"
            )
        if self.bar_width < 2 * max(self._r_first, self._r_last):
            raise ValueError("Leistenbreite zu klein für die Eckenrundung")

        min_first = self._r_first + r
        if self.first_rect_width < min_first:
            raise ValueError(
                f"Erster Abstandhalter zu schmal: mindestens {min_first:.1f} mm nötig, "
                f"aktuell {self.first_rect_width:.1f} mm"
            )
        min_rect = max(r + self._r_last, 2 * r if self.bars_count > 1 else 0.0)
        if self.rect_width < min_rect:
            raise ValueError(
                f"Abstand der Zuchtleisten zu klein: mindestens {min_rect:.1f} mm nötig, "
                f"aktuell {self.rect_width:.1f} mm"
            )

    def _notch(self):
        """Eine Aussparung (Schlitz-Einschnitt) am Rand."""
        r, o, g = self.corner_radius, self.edge_offset, self.bar_thickness
        c = self._corner(r)
        return [c, o - r, -90, g, -90, o - r, c]

    def _side(self, start, end):
        """Eine komplette Längsseite mit allen Aussparungen."""
        mid = self.rect_width - 2 * self.corner_radius
        cmds = [start]
        for i in range(self.bars_count):
            cmds += self._notch()
            cmds.append(mid if i < self.bars_count - 1 else end)
        return cmds

    def _draw_spacer_label(self, center_x, text, fontsize):
        self.ctx.save()
        self.ctx.translate(center_x, self.bar_width / 2.0)
        self.ctx.rotate(math.radians(90))
        self.text(
            text,
            x=0,
            y=0,
            fontsize=fontsize,
            align="center",
            color=boxes.Color.ANNOTATIONS,
        )
        self.ctx.restore()

    def draw_spacer_segment(self):
        """Zeichnet einen verbundenen Satz Abstandhalter für 1 bis 3 Leisten."""
        w1 = self.first_rect_width
        wm = self.rect_width
        h = self.bar_width
        g = self.bar_thickness
        r = self.corner_radius
        r_first, r_last = self._r_first, self._r_last

        # 1. Innere Ausschnitte, einer je Zuchtleiste
        inner_y = self.edge_offset + self.bridge_width
        inner_h = h - 2 * inner_y
        for i in range(self.bars_count):
            self.rectangularHole(
                w1 + i * (g + wm),
                inner_y,
                g,
                inner_h,
                center_x=False,
                center_y=False,
            )

        # 2. Durchgehende Außenkontur
        first_len = w1 - r_first - r
        last_len = wm - r - r_last
        c_first = self._corner(r_first)
        c_last = self._corner(r_last)

        self.ctx.save()
        self.moveTo(r_first, 0, 0)
        self.polyline(
            *self._side(first_len, last_len),
            c_last,
            h - 2 * r_last,
            c_last,
            *self._side(last_len, first_len),
            c_first,
            h - 2 * r_first,
            c_first,
        )
        self.ctx.restore()

        # 3. Beschriftung
        if getattr(self, "labels", True):
            self._draw_spacer_label(w1 / 2.0, f"{w1:.1f}mm", 4.0)
            for i in range(self.bars_count):
                center_x = w1 + (i + 1) * g + i * wm + wm / 2.0
                self._draw_spacer_label(center_x, f"{wm:.1f}mm", 5.0)

    # =====================================================================
    # RENDER
    # =====================================================================
    def render(self):
        draw_spacers = self.draw_mode in ("all", "spacers_only")
        draw_bar = self.draw_mode in ("all", "bar_only")

        # Nur die Parameter des tatsächlich gezeichneten Teils prüfen
        if draw_spacers:
            self._check_spacer_parameters()
        if draw_bar:
            self._check_bar_parameters()

        y_offset = 0.0

        # 1. Abstandhalter-Sätze zeichnen
        if draw_spacers:
            step = self._spacer_total_width + self.MARGIN_BETWEEN
            for i in range(self.spacer_sets):
                self.ctx.save()
                self.ctx.translate(i * step, 0)
                self.draw_spacer_segment()
                self.ctx.restore()
            y_offset = self.bar_width + self.MARGIN_BETWEEN

        # 2. Zuchtleiste darunter zeichnen
        if draw_bar:
            self.ctx.save()
            self.ctx.translate(0, y_offset)
            self.draw_bar()
            self.ctx.restore()


if __name__ == "__main__":
    b = BeeQueenRearingBar()
    b.parseArgs()
    b.render()

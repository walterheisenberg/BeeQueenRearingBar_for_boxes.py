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
    Bei den Abstandhaltern können die Verbindungsstege nach dem Einkleben
    einfach mit dem Cuttermesser abgeschnitten werden."""

    ui_group = "Misc"

    def __init__(self) -> None:
        super().__init__()

        # Festgelegte Standardwerte für die Zuchtleisten
        self.pitch_x = (
            25.0  # 2,5 cm Abstand der Löcher innerhalb einer Reihe nach Ralf Kolbe
        )

        # Standardwert für labels aktivieren (wird von boxes.Boxes bereitgestellt)
        self.labels = True

        # -----------------------------------------------------------------
        # PARAMETER FÜR DIE ZUCHTLEISTEN (HAUPTMENÜ)
        # -----------------------------------------------------------------
        self.argparser.add_argument(
            "--draw_mode",
            action="store",
            type=str,
            default="all",
            choices=["all", "spacers_only", "bar_only"],
            help="Ausgabe wählen: all (Zuchtleiste & Abstandshalter), spacers_only (Nur Abstandshalter), bar_only (Nur Leiste)",
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
            help="Breite der Leiste in mm (Default: 25mm)",
        )
        self.argparser.add_argument(
            "--hole_diameter",
            action="store",
            type=float,
            default=8.5,
            help="Durchmesser der Löcher in mm (8,5mm für Nicot Näpfchen, 18mm für die gelben Nicot-Halter, 3mm für JZBZ)",
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
            help="Abstand der Löcher von der Außenkante in mm",
        )

        # -----------------------------------------------------------------
        # UNTERMENÜ: PARAMETER FÜR DIE HALTERUNG
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
            "--first_rect_width",
            action="store",
            type=float,
            default=10.0,
            help="Länge des obersten Abstandshalters in mm (Default: 10mm)",
        )
        frame_group.add_argument(
            "--rect_width",
            action="store",
            type=float,
            default=30.0,
            help="Abstand der Zuchtleisten (Default: 30mm)",
        )
        frame_group.add_argument(
            "--gap",
            action="store",
            type=float,
            default=6.0,
            help="Dicke der Zuchtleiste in mm (Default: 6.0mm), Materialdicke",
        )
        frame_group.add_argument(
            "--bridge_width",
            action="store",
            type=float,
            default=0.8,
            help="Breite/Dicke der Verbindungsstege in mm (Default: 0.8mm)",
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
            help="Ersten Abstandhalter (links) unten abrunden",
        )
        frame_group.add_argument(
            "--round_last_rect",
            action="store",
            type=boxes.boolarg,
            default=True,
            help="Letzten Abstandhalter (rechts) unten abrunden",
        )

    def draw_bar(self):
        """Zeichnet eine Zuchtleiste inkl. Bohrungen & Beschriftung."""
        length = self.length
        width = self.bar_width
        pitch_x = self.pitch_x
        rows = self.rows
        r = self.hole_diameter / 2.0

        # Zentrierung der Löcher in X-Richtung
        margin_x_center_min = self.margin_x_min + r
        available_length = length - (2 * margin_x_center_min)

        if available_length < 0:
            margin_x_start = length / 2.0
        else:
            n_intervals = int(available_length // pitch_x)
            pattern_span = n_intervals * pitch_x
            margin_x_start = (length - pattern_span) / 2.0

        # Y-Positionen der Reihen
        y_positions = []
        if rows == 1:
            y_positions.append(width / 2.0)
        else:
            margin_y_center = self.margin_y + r
            if rows == 2:
                y_positions = [margin_y_center, width - margin_y_center]
            else:
                y_step = (width - 2 * margin_y_center) / (rows - 1)
                for i in range(rows):
                    y_positions.append(margin_y_center + i * y_step)

        # 1. Löcher zeichnen
        hole_count = 0
        for row_idx, y_pos in enumerate(y_positions):
            offset = (pitch_x / 2.0) if (row_idx % 2 == 1) else 0.0
            x = margin_x_start + offset

            while x <= (length - margin_x_center_min + 0.1):
                if x >= (margin_x_center_min - 0.1):
                    self.hole(x, y_pos, r=r)
                    hole_count += 1
                x += pitch_x

        # 2. Außenkontur der Leiste
        self.polyline(length, 90, width, 90, length, 90, width, 90)

        # 3. Beschriftungen der Leiste (abhängig von self.labels)
        if getattr(self, "labels", True):
            self.ctx.save()
            # An Position (8.0, width/2) verschieben und 90° drehen
            self.ctx.translate(8.0, width / 2.0)
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

    def draw_spacer_segment(self):
        """Zeichnet ein verbundenes Halterungssegment für 1, 2 oder 3 Leisten."""
        w1 = self.first_rect_width
        w_middle = self.rect_width
        h = self.bar_width
        gap = self.gap
        bw = self.bridge_width
        offset = self.edge_offset
        r = self.corner_radius

        # Radien je nach Checkbox-Einstellung
        r_first = r if self.round_first_rect else 0.0
        r_last = r if self.round_last_rect else 0.0

        num_bars = self.bars_count  # 1, 2 oder 3

        # Geradenlängen der Außenrechtecke
        w_first_top_straight = w1 - r_first - r
        w_first_bot_straight = w1 - r_first - r

        w_last_top_straight = w_middle - r - r_last
        w_last_bot_straight = w_middle - r_last - r

        w_mid_straight = w_middle - 2 * r

        h_left_straight = h - 2 * r_first
        h_right_straight = h - 2 * r_last

        # 1. INNERES RECHTECK / AUSSCHNITTE (SCHWARZ) FÜR JEDE LEISTEN-LÜCKE
        inner_y = offset + bw
        hole_w = gap
        hole_h = h - 2 * (offset + bw)

        for i in range(num_bars):
            self.ctx.save()
            current_x = w1 + i * (gap + w_middle)
            self.ctx.rectangle(current_x, inner_y, hole_w, hole_h)
            self.ctx.set_source_rgb(0.0, 0.0, 0.0)
            self.ctx.set_line_width(getattr(self, "burn", 0.1))
            self.ctx.stroke()
            self.ctx.restore()

        # 2. DURCHGEHENDE AUSSENKONTUR DYNAMISCH ERZEUGEN
        self.ctx.save()
        self.moveTo(r_first, 0, 0)

        # Vorbereitung der Eck-Befehle
        c_first = (90, r_first) if r_first > 0 else 90
        c_last = (90, r_last) if r_last > 0 else 90

        # Oberseite aufbauen
        top_commands = [w_first_top_straight]

        for i in range(num_bars):
            top_commands.extend(
                [
                    (90, r),
                    offset - r,
                    -90,
                    gap,
                    -90,
                    offset - r,
                    (90, r),
                ]
            )
            if i < num_bars - 1:
                top_commands.append(w_mid_straight)
            else:
                top_commands.append(w_last_top_straight)

        # Unterseite aufbauen
        bot_commands = [w_last_bot_straight]

        for i in range(num_bars):
            bot_commands.extend(
                [
                    (90, r),
                    offset - r,
                    -90,
                    gap,
                    -90,
                    offset - r,
                    (90, r),
                ]
            )
            if i < num_bars - 1:
                bot_commands.append(w_mid_straight)
            else:
                bot_commands.append(w_first_bot_straight)

        # Gesamte Polyline ausführen
        self.polyline(
            *top_commands,
            c_last,
            h_right_straight,
            c_last,
            *bot_commands,
            c_first,
            h_left_straight,
            c_first,
        )
        self.ctx.restore()

        # 3. BESCHRIFTUNG DER EINZELNEN RECHTECKE (ABHÄNGIG VON self.labels)
        if getattr(self, "labels", True):
            # 3.1 Erstes Rechteck (w1)
            self.ctx.save()
            self.ctx.translate(w1 / 2.0, h / 2.0)
            self.ctx.rotate(math.radians(90))
            self.text(
                f"{w1:.1f}mm",
                x=0,
                y=0,
                fontsize=4.0,
                align="center",
                color=boxes.Color.ANNOTATIONS,
            )
            self.ctx.restore()

            # 3.2 Alle folgenden Rechtecke (w_middle), dynamisch nach bars_count
            for i in range(num_bars):
                # Zentrum des jeweiligen Folge-Rechtecks berechnen
                rect_center_x = w1 + (i + 1) * gap + i * w_middle + (w_middle / 2.0)

                self.ctx.save()
                self.ctx.translate(rect_center_x, h / 2.0)
                self.ctx.rotate(math.radians(90))
                self.text(
                    f"{w_middle:.1f}mm",
                    x=0,
                    y=0,
                    fontsize=5,
                    align="center",
                    color=boxes.Color.ANNOTATIONS,
                )
                self.ctx.restore()

    def render(self):
        margin_between = 5.0  # Abstand zwischen den Bauteilen

        draw_spacers = self.draw_mode in ["all", "spacers_only"]
        draw_bar = self.draw_mode in ["all", "bar_only"]

        # 1. Halterungs-Segmente zeichnen
        if draw_spacers:
            spacer_total_width = (
                self.first_rect_width
                + (self.bars_count * self.rect_width)
                + (self.bars_count * self.gap)
            )

            for i in range(2):
                self.ctx.save()
                x_offset = i * (spacer_total_width + margin_between)
                self.ctx.translate(x_offset, 0)
                self.draw_spacer_segment()
                self.ctx.restore()

            y_offset = self.bar_width + margin_between
        else:
            y_offset = 0.0

        # 2. Zuchtleiste zeichnen
        if draw_bar:
            self.ctx.save()
            self.ctx.translate(0, y_offset)
            self.draw_bar()
            self.ctx.restore()


if __name__ == "__main__":
    b = BeeQueenRearingBar()
    b.parseArgs()
    b.render()

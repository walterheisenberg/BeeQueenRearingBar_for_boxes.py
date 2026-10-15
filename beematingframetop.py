#!/usr/bin/env python3
# Copyright (C) 2013-2024 Florian Festi
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

from boxes import Boxes, Color


class BeeMatingFrameTop(Boxes):
    """Rähmchen für Begattungskästchen: Oberseite plus 2 Seitenteile (Apidea)

    Variante 1 (Klick): T-Ausschnitt in der Oberseite, einklickbare Seitenteile.
    Variante 2 (ApideaStyle): Wie beim Apidea Kunststoff-Rähmchen
    """

    ui_group = "Misc"

    # Varianten (Auswahl --variant)
    KLICK = "Klick"  # Variante 1
    APIDEA_STYLE = "ApideaStyle"  # Variante 2

    # Apidea-Standardwerte der einstellbaren Felder (Default und Hilfetext)
    APIDEA = {
        "width": 25.0,  # Gesamtbreite des Oberträgers
        "length": 118.0,  # Gesamtlänge des Oberträgers
        "ear_length": 6.0,  # Ohrenlänge: von außen bis zum Anfang des Seitenteils
        "height": 106.0,  # Höhe der Seitenteile
        "notches": 2,  # Anzahl der Rundungen am Rand
    }

    # Feste Maße in mm (Apidea, aus Zeichnung + Maßstabsbild) - nicht einstellbar
    CORNER_RADIUS = 2.0  # Abrundung der vier Außenecken
    STEM_WIDTH = 3.0  # Breite des Mittelstegs im Ausschnitt
    MIN_WALL = 2.0  # kleinste erlaubte Reststärke zwischen Ausschnitt und Rand
    SIDE_MIN_EXTRA = 10.0  # Mindestlänge unter Schlitzspitze bzw. Verjüngung

    # Rundungen am Rand (beide Varianten gleich)
    NOTCH_RADIUS = 12.0  # vorher: Klick 12.5, ApideaStyle 11.5
    NOTCH_DEPTH = 7.5  # Tiefe vom Rand; vorher: Klick 7.5, ApideaStyle 7.6
    NOTCH_CENTER = 29.5  # Mitte vom Ende (bei 2); vorher: Klick 29.0, ApideaStyle 29.5

    # Standardwert der Clearance (Spiel der Steckverbindungen) in mm, gesamt und
    # nicht je Seite; einstellbar über --clearance, in beiden Varianten gleich.
    # Vorher: Klick 0.4, ApideaStyle 0.2
    CLEARANCE = 0.2

    # Gravur-Text auf dem Oberträger (beide Varianten). Die Schriftgröße wählt das
    # Script selbst: höchstens TEXT_SIZE, bei langem Text kleiner.
    TEXT_SIZE = 6.0  # größte Schriftgröße in mm (Großbuchstaben ca. 4.3 mm hoch)
    TEXT_MIN_SIZE = 2.5  # kleinste Schriftgröße; kleiner = Fehlermeldung
    TEXT_MARGIN = 2.0  # Abstand des Textes zu Schnittkanten in mm
    TEXT_CAP = 0.72  # Höhe der Großbuchstaben relativ zur Schriftgröße
    TEXT_CHAR = 0.6  # geschätzte mittlere Zeichenbreite relativ zur Schriftgröße

    # Variante 2 (Apidea-like): Maße in mm aus dem Apidea-Bild (4 Pixel je mm).
    # Breite = Gesamtbreite der Oberseite (wie bei Variante 1). Das Seitenteil ist
    # unten 1 mm schmaler als die Oberseite; alle breiteren Teile darüber wachsen
    # um denselben Betrag wie die Oberseite mit.
    A_TAB_WIDTH = 8.0  # Breite der beiden Nasen an den Enden der Oberseite
    A_TAB_RADIUS = 0.5  # Abrundung der Nasen
    A_SIDE_CAP_DEPTH = 5.25  # Höhe des Kopfes (Unterkante des Kopfes, ab oben)
    A_SIDE_TAPER_END = 41.25  # Tiefe (ab Oberkante), ab der der schmale Teil beginnt
    A_SIDE_SHOULDER_RADIUS = 0.75  # Schulter, obere Außenecke
    A_SIDE_CAP_BOTTOM_RADIUS = 1.0  # Kopf, untere Außenecke
    A_SIDE_CAP_TOP_RADIUS = 1.0  # Kopf, obere Außenecken
    # Seitenteil Variante 2 (ohne die beiden Aussparungen): (halbe Breite, Tiefe
    # ab Oberkante, Radius), von der Unterkante nach oben. Tiefe None = Höhe.
    A_SIDE_LOWER = [
        (12.0, None, 1.0),  # unten, schmaler Teil
        (12.0, A_SIDE_TAPER_END, 0.0),
        (17.0, 31.75, 0.0),  # Verjüngung zum breiten Wulst
        (17.0, 27.5, 0.0),
        (15.5, 26.25, 0.0),  # Körper
        (15.5, 14.75, 0.0),
        (17.0, 13.5, 0.0),  # Schulter
    ]
    A_SIDE_CAP_HALF = 14.5  # halbe Breite des Kopfes
    # halbe Breite an der breitesten Stelle (aus A_SIDE_LOWER berechnet)
    A_SIDE_MAX_HALF = max(hw for hw, _, _ in A_SIDE_LOWER)

    # Seitenteil (Apidea), Maße in mm: aus der Zeichnung gemessen und gerade
    # (symmetrisch) ausgerichtet. Nur die Höhe ist einstellbar; der senkrechte
    # Schlitz wird dabei nicht mitskaliert. Bei geänderter Breite werden die
    # Seitenteile um denselben Betrag breiter/schmaler (nur der Vollmaterial-Teil).
    SIDE_CAP_HALF = 10.65  # halbe Breite des Kopfes
    SIDE_CAP_HEIGHT = 2.9  # Höhe des Kopfes
    SIDE_NECK_HALF = 7.8  # halbe Breite des Halses unter dem Kopf
    SIDE_RAMP = 0.8  # Höhe der Schräge zwischen Hals und Schulter (Einklick-Kante)
    SIDE_SHOULDER_HALF = 8.7  # halbe Breite an der Schulter
    SIDE_BOTTOM_HALF = 6.25  # halbe Breite unten (Körper verjüngt sich dorthin)
    SIDE_BOTTOM_RADIUS = 1.7  # Abrundung der unteren Ecken
    SIDE_NECK_RADIUS = 0.4  # Abrundung am Übergang Hals -> Schräge
    SIDE_CAP_INNER_RADIUS = 0.9  # Abrundung zwischen Hals und Kopf (innen)
    SIDE_CAP_BOTTOM_RADIUS = 0.8  # Kopf, untere Außenecke
    SIDE_CAP_TOP_RADIUS = 1.0  # Kopf, obere Außenecken
    SIDE_SLIT_MOUTH_HALF = 1.95  # halbe Schlitzbreite an der Oberkante (Einlauf)
    SIDE_SLIT_HALF = 1.7  # halbe Schlitzbreite im geraden Teil (= Radius am Ende)
    SIDE_SLIT_LEAD = 19.4  # Länge des Einlaufs (Schlitz verengt sich bis dahin)
    SIDE_SLIT_DEPTH = 47.1  # Tiefe der Schlitzspitze ab Oberkante

    def __init__(self) -> None:
        Boxes.__init__(self)
        if not any(
            "--thickness" in action.option_strings for action in self.argparser._actions
        ):
            self.argparser.add_argument(
                "--thickness",
                action="store",
                type=float,
                default=3.0,
                help="Materialstärke in mm (Variante 2: Höhe der Aussparungen)",
            )
        self.argparser.add_argument(
            "--variant",
            action="store",
            type=str,
            default=self.KLICK,
            choices=[self.KLICK, self.APIDEA_STYLE],
            help="Variante 1 = Klick (T-Ausschnitt, einklickbare Seitenteile); "
            "Variante 2 = Apidea (Wie Original Apidea-Rähmchen)",
        )
        self.argparser.add_argument(
            "--width",
            action="store",
            type=float,
            default=self.APIDEA["width"],
            help="Gesamtbreite des Oberträgers in mm "
            f"(Apidea: {self.APIDEA['width']:g}); die Seitenteile werden angepasst",
        )
        self.argparser.add_argument(
            "--length",
            action="store",
            type=float,
            default=self.APIDEA["length"],
            help="Gesamtlänge des Oberträgers in mm "
            f"(Apidea: {self.APIDEA['length']:g})",
        )
        self.argparser.add_argument(
            "--ear_length",
            action="store",
            type=float,
            default=self.APIDEA["ear_length"],
            help="Ohrenlänge in mm: von außen bis zum Anfang des Seitenteils "
            f"(Apidea: {self.APIDEA['ear_length']:.1f}); "
            "in beiden Varianten gleich lang",
        )
        self.argparser.add_argument(
            "--height",
            action="store",
            type=float,
            default=self.APIDEA["height"],
            help="Höhe der Seitenteile in mm "
            f"(Apidea: {self.APIDEA['height']:g})",
        )
        self.argparser.add_argument(
            "--notches",
            action="store",
            type=int,
            default=self.APIDEA["notches"],
            choices=[1, 2],
            help="Anzahl der Aussparungen für Zellen: 2 wie Apidea oder 1 in der "
            "Mitte",
        )
        self.argparser.add_argument(
            "--clearance",
            action="store",
            type=float,
            default=self.CLEARANCE,
            help="Clearance (Spiel) der Steckverbindungen in mm, gesamt und nicht je "
            "Seite: Der T-Ausschnitt (Klick) bzw. die Aussparung zwischen den Nasen "
            "der Oberseite (ApideaStyle) wird um diesen Wert größer als das "
            "Gegenstück im Seitenteil. 0 = keine Clearance. Die Schnittfuge (burn) "
            f"wird davon unabhängig ausgeglichen (Standard: {self.CLEARANCE:g})",
        )
        self.argparser.add_argument(
            "--engrave_text",
            action="store",
            type=str,
            default="",
            help="Text, der in den Oberträger gelasert (graviert) wird; leer = kein "
            "Text. Er läuft in Längsrichtung: bei Klick im freien Streifen neben "
            "dem Mittelsteg, bei ApideaStyle mittig. Die Schriftgröße wählt das "
            f"Script (höchstens {self.TEXT_SIZE:g} mm, bei langem Text kleiner)",
        )

    # ------------------------------------------------------------------
    # Hilfsfunktionen
    # ------------------------------------------------------------------
    def setup_variant(self):
        """Übernimmt Breite und Ohrenlänge (gelten in beiden Varianten gleich)"""
        self.ear = self.ear_length
        self.w = self.width
        if self.clearance < 0:
            raise ValueError("Die Clearance darf nicht negativ sein.")

    def notch_geometry(self):
        """Gibt (c, h, a) zurück.

        c: Abstand der Kreismitte vom rechten Rand (nach außen)
        h: halbe Sehnenlänge, mit der die Rundung den Rand schneidet
        a: Winkel in Grad, in dem der Rand in die Rundung übergeht
        """
        r = self.NOTCH_RADIUS
        c = r - self.NOTCH_DEPTH
        h = math.sqrt(r * r - c * c)
        a = math.degrees(math.asin(h / r))
        return c, h, a

    def notch_centers(self, l):
        """y-Positionen der Rundungsmitten (vom unteren Ende gemessen)"""
        if self.notches == 1:
            return [l / 2]
        return [self.NOTCH_CENTER, l - self.NOTCH_CENTER]

    @staticmethod
    def rect_distance(px, py, x0, y0, x1, y1):
        """Abstand eines Punktes zu einem Rechteck (0 wenn innen)"""
        dx = max(x0 - px, 0, px - x1)
        dy = max(y0 - py, 0, py - y1)
        return math.hypot(dx, dy)

    def check_dimensions(self, w, l, e):
        wall = self.MIN_WALL
        tw, th, sw = self.t_width(w), self.thickness, self.STEM_WIDTH
        c, h, _ = self.notch_geometry()
        centers = self.notch_centers(l)

        if e < wall:
            raise ValueError(f"Die Ohrenlänge muss mindestens {wall} mm betragen.")
        if w < tw + 2 * wall:
            raise ValueError(
                f"Die Breite muss mindestens {tw + 2 * wall} mm betragen "
                "(T-Ausschnitt plus Rand)."
            )
        if l < 2 * (e + th) + wall:
            raise ValueError(
                "Länge zu klein: Länge muss größer als 2 x (Ohrenlänge + T-Höhe) sein."
            )
        if self.notches == 2:
            min_len = 2 * (self.NOTCH_CENTER + h)
        else:
            min_len = 2 * (h + self.CORNER_RADIUS)
        if l < min_len:
            raise ValueError(
                f"Die Länge muss mindestens {min_len:.1f} mm betragen, "
                "damit die Rundung(en) Platz haben."
            )

        # Ausschnitt darf den Rundungen nicht zu nahe kommen
        xl, xr = (w - tw) / 2, (w + tw) / 2
        sl, sr = (w - sw) / 2, (w + sw) / 2
        parts = [
            (xl, e, xr, e + th),  # unterer T-Balken
            (xl, l - e - th, xr, l - e),  # oberer T-Balken
            (sl, e + th, sr, l - e - th),  # Mittelsteg
        ]
        for cy in centers:
            for x0, y0, x1, y1 in parts:
                dist = self.rect_distance(w + c, cy, x0, y0, x1, y1)
                if dist - self.NOTCH_RADIUS < wall:
                    raise ValueError(
                        "Der Ausschnitt kommt einer Rundung zu nah "
                        f"(Rest unter {wall} mm): Breite vergrößern oder "
                        "Ohrenlänge verkleinern."
                    )

    def t_width(self, w):
        """Breite des T-Balkens: passt zum Hals der Seitenteile (wächst mit w).

        Der lange Teil (Mittelsteg, STEM_WIDTH) wird nicht mitskaliert.
        """
        return 2 * (self.SIDE_NECK_HALF + self.side_grow(w)) + self.clearance

    def side_neck_end(self):
        """Tiefe (ab Oberkante), wo die Schräge zur Schulter beginnt.

        Der Hals ist so lang, dass der Oberträger (Materialstärke) zwischen
        Kopf und der Einklick-Kante der Schulter sitzt: die Schräge erreicht die
        Breite des T-Ausschnitts genau bei Kopfhöhe + Materialstärke.
        """
        ramp_dx = self.SIDE_SHOULDER_HALF - self.SIDE_NECK_HALF
        catch = self.SIDE_RAMP * (self.clearance / 2) / ramp_dx
        return self.SIDE_CAP_HEIGHT + self.thickness - catch

    def side_shoulder_depth(self):
        """Tiefe (ab Oberkante), ab der die Schulter voll breit ist"""
        return self.side_neck_end() + self.SIDE_RAMP

    def side_grow(self, w):
        """Zuwachs je Seite der Seitenteil-Breite bei geänderter Breite w"""
        return (w - self.APIDEA["width"]) / 2

    def check_side(self, w, h):
        # Die Schulter ist breiter als der T-Ausschnitt (Einklick-Überstand)
        max_clr = 2 * (self.SIDE_SHOULDER_HALF - self.SIDE_NECK_HALF)
        if self.clearance >= max_clr:
            raise ValueError(
                "Die Clearance ist zu groß: das Seitenteil würde nicht mehr "
                f"einklicken. Sie muss kleiner als {max_clr:.1f} mm sein."
            )
        min_h = self.SIDE_SLIT_DEPTH + self.SIDE_MIN_EXTRA
        if h < min_h:
            raise ValueError(
                f"Die Höhe muss mindestens {min_h:.1f} mm betragen "
                "(Länge des senkrechten Schlitzes plus Rand)."
            )
        # Restmaterial neben dem Schlitz (Einlauf und Schlitzspitze)
        g = self.side_grow(w)
        t = (self.SIDE_SLIT_DEPTH - self.side_shoulder_depth()) / (
            h - self.side_shoulder_depth()
        )
        half_at_tip = (self.SIDE_SHOULDER_HALF + g) + (
            self.SIDE_BOTTOM_HALF - self.SIDE_SHOULDER_HALF
        ) * t
        neck = self.SIDE_NECK_HALF + g - self.SIDE_SLIT_MOUTH_HALF
        if min(half_at_tip - self.SIDE_SLIT_HALF, neck) < self.MIN_WALL:
            raise ValueError(
                "Seitenteil zu schmal: neben dem Schlitz bleibt weniger als "
                f"{self.MIN_WALL} mm Material. Breite vergrößern."
            )

    # ------------------------------------------------------------------
    # Zeichnen
    # ------------------------------------------------------------------
    def slot(self, w, l, e):
        """T-förmiger Ausschnitt (an beiden Enden ein T-Balken), mittig"""
        tw, th, sw = self.t_width(w), self.thickness, self.STEM_WIDTH
        side = (tw - sw) / 2
        stem = l - 2 * e - 2 * th

        self.ctx.save()
        self.set_source_color(Color.INNER_CUT)
        self.moveTo((w - tw) / 2, e, 90)
        # im Uhrzeigersinn: Innenausschnitt
        for length, angle in (
            (th, -90),
            (side, 90),
            (stem, 90),
            (side, -90),
            (th, -90),
            (tw, -90),
            (th, -90),
            (side, 90),
            (stem, 90),
            (side, -90),
            (th, -90),
            (tw, -90),
        ):
            self.edge(length)
            self.corner(angle)
        self.ctx.restore()

    def notch(self):
        """Rundung am rechten Rand (Kreisabschnitt nach innen)"""
        _, _, a = self.notch_geometry()
        self.corner(a)
        self.corner(-2 * a, self.NOTCH_RADIUS)
        self.corner(a)

    def outline(self, w, l):
        r = self.CORNER_RADIUS
        _, h, _ = self.notch_geometry()

        self.moveTo(r, 0)
        self.edge(w - 2 * r)  # unten
        self.corner(90, r)
        pos = r  # aktuelle Höhe am rechten Rand
        for cy in self.notch_centers(l):
            self.edge(cy - h - pos)
            self.notch()
            pos = cy + h
        self.edge(l - r - pos)
        self.corner(90, r)
        self.edge(w - 2 * r)  # oben
        self.corner(90, r)
        self.edge(l - 2 * r)  # links
        self.corner(90, r)

    def rounded_polygon(self, vertices):
        """Zeichnet ein Polygon gegen den Uhrzeigersinn mit Eckenradien.

        vertices: Liste (x, y, radius) der scharfen Ecken
        """
        n = len(vertices)

        def turn(i):  # Richtungsänderung in Ecke i in Grad (links = positiv)
            ax, ay, _ = vertices[i - 1]
            bx, by, _ = vertices[i]
            cx, cy, _ = vertices[(i + 1) % n]
            abx, aby, bcx, bcy = bx - ax, by - ay, cx - bx, cy - by
            return math.degrees(
                math.atan2(abx * bcy - aby * bcx, abx * bcx + aby * bcy)
            )

        angles = [turn(i) for i in range(n)]
        # Tangentenlänge je Ecke
        tans = [
            vertices[i][2] * math.tan(math.radians(abs(angles[i])) / 2)
            for i in range(n)
        ]

        # Start auf der Kante von Ecke 0 nach Ecke 1, hinter der Rundung von Ecke 0
        x0, y0, _ = vertices[0]
        x1, y1, _ = vertices[1]
        heading = math.atan2(y1 - y0, x1 - x0)
        self.moveTo(
            x0 + tans[0] * math.cos(heading),
            y0 + tans[0] * math.sin(heading),
            math.degrees(heading),
        )
        for i in range(n):
            j = (i + 1) % n
            length = math.hypot(
                vertices[j][0] - vertices[i][0], vertices[j][1] - vertices[i][1]
            )
            self.edge(max(length - tans[i] - tans[j], 0))
            self.corner(angles[j], vertices[j][2])

    def side_vertices(self, w, h):
        """Ecken des Seitenteils (x ab linker Kante, y ab Unterkante)"""
        g = self.side_grow(w)  # Breitenänderung je Seite, Schlitz bleibt gleich
        hc = self.SIDE_CAP_HALF + g
        hn = self.SIDE_NECK_HALF + g
        hs = self.SIDE_SHOULDER_HALF + g
        hb = self.SIDE_BOTTOM_HALF + g
        m, sl = self.SIDE_SLIT_MOUTH_HALF, self.SIDE_SLIT_HALF
        rb = self.SIDE_BOTTOM_RADIUS

        def v(x, d, r=0.0):  # x relativ zur Mittelachse, d = Tiefe ab Oberkante
            return (hc + x, h - d, r)

        return [
            v(-hb, h, rb),  # unten links
            v(hb, h, rb),  # unten rechts
            v(hs, self.side_shoulder_depth()),
            v(hn, self.side_neck_end(), self.SIDE_NECK_RADIUS),
            v(hn, self.SIDE_CAP_HEIGHT, self.SIDE_CAP_INNER_RADIUS),
            v(hc, self.SIDE_CAP_HEIGHT, self.SIDE_CAP_BOTTOM_RADIUS),
            v(hc, 0, self.SIDE_CAP_TOP_RADIUS),  # Kopf rechts oben
            v(m, 0),  # Schlitz-Einlauf rechts
            v(sl, self.SIDE_SLIT_LEAD),
            v(sl, self.SIDE_SLIT_DEPTH, sl),  # Schlitzende (Halbkreis)
            v(-sl, self.SIDE_SLIT_DEPTH, sl),
            v(-sl, self.SIDE_SLIT_LEAD),
            v(-m, 0),
            v(-hc, 0, self.SIDE_CAP_TOP_RADIUS),  # Kopf links oben
            v(-hc, self.SIDE_CAP_HEIGHT, self.SIDE_CAP_BOTTOM_RADIUS),
            v(-hn, self.SIDE_CAP_HEIGHT, self.SIDE_CAP_INNER_RADIUS),
            v(-hn, self.side_neck_end(), self.SIDE_NECK_RADIUS),
            v(-hs, self.side_shoulder_depth()),
        ]

    def side_plate(self, w, h, move=None):
        """Seitenteil, gerade und symmetrisch.

        w: Breite der Oberseite (die Seitenteile wachsen mit), h: Höhe.
        Der senkrechte Schlitz bleibt immer gleich.
        """
        pw = 2 * (self.SIDE_CAP_HALF + self.side_grow(w))
        if self.move(pw, h, move, True):
            return
        self.rounded_polygon(self.side_vertices(w, h))
        self.move(pw, h, move)

    # ------------------------------------------------------------------
    # Variante 2: Apidea-Style
    # ------------------------------------------------------------------
    def a_gap(self, w):
        """Breite der Aussparung zwischen den Nasen der Oberseite"""
        return w - 2 * self.A_TAB_WIDTH

    def a_tongue_half(self, w):
        """Halbe Breite der Zunge im Seitenteil: passt in die Aussparung"""
        return (self.a_gap(w) - self.clearance) / 2

    def check_apidea(self, w, l, e, h):
        t, r = self.A_TAB_WIDTH, self.A_TAB_RADIUS
        _, nh, _ = self.notch_geometry()
        mat = self.thickness
        depth = e + mat  # Tiefe der Aussparung = Ohr + Materialstärke
        min_tongue = 2 * self.MIN_WALL
        if self.a_tongue_half(w) * 2 < min_tongue:
            min_w = w + (min_tongue - self.a_tongue_half(w) * 2)
            raise ValueError(
                "Die Zunge des Seitenteils würde schmaler als "
                f"{min_tongue} mm (Breite zu klein oder Clearance zu groß). "
                f"Bei dieser Clearance mindestens {min_w:.1f} mm Breite."
            )
        if e < 2 * r:
            raise ValueError(f"Die Ohrenlänge muss mindestens {2 * r} mm betragen.")
        if self.notches == 2:
            if depth > self.NOTCH_CENTER - nh - self.MIN_WALL:
                raise ValueError(
                    "Die Ohrenlänge oder Materialstärke ist zu groß: die "
                    "Aussparung kommt der Rundung zu nah."
                )
            min_len = 2 * (self.NOTCH_CENTER + nh)
        else:
            min_len = 2 * (nh + depth + self.MIN_WALL)
        if l < min_len:
            raise ValueError(
                f"Die Länge muss mindestens {min_len:.1f} mm betragen, "
                "damit die Rundung(en) Platz haben."
            )
        top = self.A_SIDE_TAPER_END
        if h < top + self.SIDE_MIN_EXTRA:
            raise ValueError(
                f"Die Höhe muss mindestens {top + self.SIDE_MIN_EXTRA:.1f} mm "
                "betragen."
            )

    def outline_apidea(self, w, l, depth):
        """Oberseite: Nasen an den Enden, Aussparung für die Zunge dazwischen.

        depth: Tiefe der Aussparung ab dem Ende (Ohrenlänge + Materialstärke);
        das Seitenteil sitzt am Grund der Aussparung, die Ohren ragen also
        genau um die Ohrenlänge über das Seitenteil hinaus.
        """
        r, t = self.A_TAB_RADIUS, self.A_TAB_WIDTH
        _, h, _ = self.notch_geometry()

        self.moveTo(r, 0)
        # unteres Ende: linke Nase, Aussparung, rechte Nase
        self.edge(t - 2 * r)
        self.corner(90, r)
        self.edge(depth - r)
        self.corner(-90)
        self.edge(w - 2 * t)
        self.corner(-90)
        self.edge(depth - r)
        self.corner(90, r)
        self.edge(t - 2 * r)
        self.corner(90, r)
        # rechter Rand mit Rundungen
        pos = r
        for cy in self.notch_centers(l):
            self.edge(cy - h - pos)
            self.notch()
            pos = cy + h
        self.edge(l - r - pos)
        self.corner(90, r)
        # oberes Ende: rechte Nase, Aussparung, linke Nase
        self.edge(t - 2 * r)
        self.corner(90, r)
        self.edge(depth - r)
        self.corner(-90)
        self.edge(w - 2 * t)
        self.corner(-90)
        self.edge(depth - r)
        self.corner(90, r)
        self.edge(t - 2 * r)
        self.corner(90, r)
        # linker Rand
        self.edge(l - 2 * r)
        self.corner(90, r)

    def top_bar_apidea(self, w, l, e, move=None):
        if self.move(w, l, move, True):
            return
        self.draw_text(self.text_layout)
        self.outline_apidea(w, l, e + self.thickness)
        self.move(w, l, move)

    def side_vertices_apidea(self, w, h):
        """Ecken des Apidea-Seitenteils.

        Alle Breiten wachsen mit der Breite der Oberseite mit. Links und rechts
        der Zunge liegen die Aussparungen (Höhe = Materialstärke), durch die die
        Nasen der Oberseite laufen.
        """
        g = self.side_grow(w)
        d_cap = self.A_SIDE_CAP_DEPTH
        d_shoulder = d_cap + self.thickness
        tongue = self.a_tongue_half(w) - g  # g wird unten wieder addiert
        half = [(hw, h if d is None else d, r) for hw, d, r in self.A_SIDE_LOWER]
        half += [
            (self.A_SIDE_LOWER[-1][0], d_shoulder, self.A_SIDE_SHOULDER_RADIUS),
            (tongue, d_shoulder, 0.0),  # Aussparung: Boden bis zur Zunge
            (tongue, d_cap, 0.0),  # Zunge hoch bis zum Kopf
            (self.A_SIDE_CAP_HALF, d_cap, self.A_SIDE_CAP_BOTTOM_RADIUS),  # Kopf unten
            (self.A_SIDE_CAP_HALF, 0.0, self.A_SIDE_CAP_TOP_RADIUS),  # Kopf oben
        ]
        cx = self.A_SIDE_MAX_HALF + g  # Mittelachse
        right = [(cx + hw + g, h - d, r) for hw, d, r in half]
        left = [(cx - hw - g, h - d, r) for hw, d, r in reversed(half)]
        return right + left

    def side_plate_apidea(self, w, h, move=None):
        # Platzbedarf = breiteste Stelle (Wulst/Schulter), nicht der Kopf
        pw = 2 * (self.A_SIDE_MAX_HALF + self.side_grow(w))
        if self.move(pw, h, move, True):
            return
        self.rounded_polygon(self.side_vertices_apidea(w, h))
        self.move(pw, h, move)

    # ------------------------------------------------------------------
    # Gravur-Text
    # ------------------------------------------------------------------
    def text_length(self, text, size):
        """Länge des Textes in mm (mit cairo gemessen, sonst geschätzt)"""
        self.ctx.save()
        try:
            self.ctx.select_font_face("Arial")
            self.ctx.set_font_size(size)
            return self.ctx.text_extents(text)[4]
        except Exception:
            return self.TEXT_CHAR * size * len(text)
        finally:
            self.ctx.restore()

    def layout_text(self, w, l, e):
        """Platz und Schriftgröße für den Gravur-Text: (x, y, Größe) oder None.

        Der Text läuft in Längsrichtung und sitzt mittig auf der Länge.
        Klick: im freien Streifen links neben dem Mittelsteg.
        ApideaStyle: mittig auf dem Oberträger, zwischen linkem Rand und Rundungen.
        An den Enden bleibt Platz für die T-Balken bzw. die Aussparungen.
        """
        if not self.engrave_text.strip():
            return None
        m = self.TEXT_MARGIN
        y0 = e + self.thickness + m  # hinter T-Balken bzw. Aussparung am Ende
        if self.variant == self.APIDEA_STYLE:
            lo, hi = m, w - self.NOTCH_DEPTH - m  # zwischen Rand und Rundungen
        else:
            lo, hi = m, (w - self.STEM_WIDTH) / 2 - m  # neben dem Mittelsteg
        band = hi - lo
        length = l - 2 * y0
        if band <= 0 or length <= 0:
            raise ValueError("Für den Text ist auf dem Oberträger kein Platz.")
        size = min(self.TEXT_SIZE, band / self.TEXT_CAP)
        width = self.text_length(self.engrave_text, size)
        if width > length:
            size *= length / width
        if size < self.TEXT_MIN_SIZE:
            max_chars = int(length / (self.TEXT_MIN_SIZE * self.TEXT_CHAR))
            raise ValueError(
                f"Der Text ist zu lang: auf dem Oberträger ist Platz für etwa "
                f"{max_chars} Zeichen."
            )
        x = (lo + hi) / 2
        if self.variant == self.APIDEA_STYLE:
            # mittig, solange der Text nicht an die Rundungen stößt
            x = min(w / 2, hi - size * self.TEXT_CAP / 2)
        return x, l / 2, size

    def draw_text(self, layout):
        """Graviert den Text (Längsrichtung, von unten nach oben lesbar)"""
        if not layout:
            return
        x, y, size = layout
        self.text(
            self.engrave_text,
            x,
            y,
            angle=90,
            align="middle center",
            fontsize=size,
            color=getattr(Color, "ETCHING", [0.0, 1.0, 0.0]),
        )

    def top_bar(self, w, l, e, move=None):
        if self.move(w, l, move, True):
            return
        self.draw_text(self.text_layout)
        self.slot(w, l, e)
        self.outline(w, l)
        self.move(w, l, move)

    def render(self):
        self.setup_variant()
        w, l, e = self.w, self.length, self.ear
        if self.variant == self.APIDEA_STYLE:
            self.check_apidea(w, l, e, self.height)
            self.text_layout = self.layout_text(w, l, e)
            self.top_bar_apidea(w, l, e, move="right")
            for _ in range(2):  # 2 Seitenteile: Rähmchen ohne Unterträger
                self.side_plate_apidea(w, self.height, move="right")
            return
        self.check_dimensions(w, l, e)
        self.check_side(w, self.height)
        self.text_layout = self.layout_text(w, l, e)
        self.top_bar(w, l, e, move="right")
        # 2 Seitenteile: Rähmchen ohne Unterträger
        for _ in range(2):
            self.side_plate(w, self.height, move="right")

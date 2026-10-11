#!/usr/bin/env python3
# boxes.py generator "HangFrame"
# Copy this file to boxes/generators/hangframe.py (class name HangFrame).

from boxes import *


class HangFrame(Boxes):
    """Rahmen zum Einhängen in eine Beute: Seitenwände mit Ohren an beiden Enden,
    Stirn- und Rückwand, kein Boden, kein Deckel, Einkerbungen oben an den Seitenwänden"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)

        self.argparser.add_argument(
            "--x", action="store", type=float, default=81.0,
            help="Innenbreite zwischen den Seitenwänden (mm)")
        self.argparser.add_argument(
            "--y", action="store", type=float, default=470.0,
            help="Gesamtlänge der Seitenwände inkl. Ohren (mm)")
        self.argparser.add_argument(
            "--h", action="store", type=float, default=100.0,
            help="Höhe des Rahmens (mm)")
        self.argparser.add_argument(
            "--hang_height", action="store", type=float, default=20.0,
            help="Höhe der Aufhängung (Ohren) in mm")
        self.argparser.add_argument(
            "--hang_inset", action="store", type=float, default=20.0,
            help="Abstand der Außenseite von Stirn-/Rückwand zum äußeren Ende (mm)")
        self.argparser.add_argument(
            "--notch_width", action="store", type=float, default=20.0,
            help="Breite einer Einkerbung (mm)")
        self.argparser.add_argument(
            "--notch_gap", action="store", type=float, default=5.0,
            help="Abstand zwischen den Einkerbungen (mm)")
        self.argparser.add_argument(
            "--notch_depth", action="store", type=float, default=5.0,
            help="Tiefe der Einkerbungen (mm)")
        self.argparser.add_argument(
            "--notch_radius", action="store", type=float, default=1.0,
            help="Radius der Abrundung an der Oberseite der Einkerbungen (mm)")
        self.argparser.add_argument(
            "--notch_spacing", action="store", type=float, default=5.0,
            help="Abstand der ersten Einkerbung von der Innenseite der Stirnwand (mm)")
        self.argparser.add_argument(
            "--notch_count", action="store", type=int, default=0,
            help="Anzahl Einkerbungen (0 = so viele wie hineinpassen)")

    # ------------------------------------------------------------------
    def topProfile(self, l):
        """Obere Kante der Seitenwand, von rechts (Rückseite) nach links (Stirnseite).
        Liefert die Argumente für self.polyline()."""
        nw, gap, d = self.notch_width, self.notch_gap, self.notch_depth
        sp, r = self.notch_spacing, self.notch_radius
        T = self.y - 2 * l  # Länge zwischen den Innenseiten von Stirn- und Rückwand

        if r > d or 2 * r > nw:
            raise ValueError("notch_radius ist zu groß für Tiefe/Breite der Einkerbung")

        n = self.notch_count
        if n > 0:
            needed = sp + n * nw + (n - 1) * gap
            if needed > T + 1e-6:
                raise ValueError(
                    "%d Einkerbungen passen nicht: benötigt %.1f mm, verfügbar %.1f mm"
                    % (n, needed, T))
        else:
            n = max(0, int((T - sp + gap) // (nw + gap)))

        toks = []
        cur = self.y  # x-Position, Start am äußeren Ende rechts
        for i in reversed(range(n)):
            a = l + sp + i * (nw + gap)  # linke Kante der Einkerbung
            toks.append(["s", cur - (a + nw)])
            toks += [["t", 90, r], ["s", d], ["t", -90, 0], ["s", nw],
                     ["t", -90, 0], ["s", d], ["t", 90, r]]
            cur = a
        toks.append(["s", cur])

        # Abrundungen verbrauchen r von den angrenzenden Geraden
        for i, tok in enumerate(toks):
            if tok[0] == "t" and tok[2] > 0:
                toks[i - 1][1] -= r
                toks[i + 1][1] -= r

        args = []
        for tok in toks:
            if tok[0] == "s":
                if tok[1] < -1e-6:
                    raise ValueError("notch_radius ist zu groß für den Abstand an den Einkerbungen")
                args.append(max(tok[1], 0))
            else:
                args.append((tok[1], tok[2]) if tok[2] > 0 else tok[1])
        return args

    # ------------------------------------------------------------------
    def sideWall(self, move=None):
        t = self.thickness
        l = self.hang_inset + t          # Ohr: äußeres Ende -> Innenseite der Stirnwand
        T = self.y - 2 * l               # Länge zwischen Stirn- und Rückwand
        hh = self.h - self.hang_height   # Länge der Fingerzinken (unterhalb der Ohren)

        if T <= 0 or hh <= 0:
            raise ValueError("Maße passen nicht (y zu kurz oder Aufhängung zu hoch)")

        m = self.edges["f"].margin()
        tw, th = self.y + 2 * m, self.h + 2 * m
        if self.move(tw, th, move, True):
            return

        self.moveTo(m + l, m)
        self.edge(T)                      # unten, ohne Boden
        self.corner(90)
        self.edges["f"](hh)               # Rückwand
        self.corner(-90)
        self.edge(l)                      # Ohr (Unterseite)
        self.corner(90)
        self.edge(self.hang_height)       # Ohr (Außenseite)
        self.corner(90)
        self.polyline(*self.topProfile(l))  # oben, mit Einkerbungen
        self.corner(90)
        self.edge(self.hang_height)       # Ohr (Außenseite)
        self.corner(90)
        self.edge(l)                      # Ohr (Unterseite)
        self.corner(-90)
        self.edges["f"](hh)               # Stirnwand
        self.corner(90)
        self.ctx.stroke()
        self.move(tw, th, move)

    # ------------------------------------------------------------------
    def endWall(self, move=None):
        t = self.thickness
        W = self.x + 2 * t
        hh = self.h - self.hang_height

        m = self.edges["F"].margin()
        tw, th = W + 2 * m, self.h + 2 * m
        if self.move(tw, th, move, True):
            return

        self.moveTo(m, m)
        self.edge(W)                      # unten
        self.corner(90)
        self.edges["F"](hh)               # rechts
        self.corner(90)
        self.edge(t)                      # Absatz nach innen (Platz für das Ohr)
        self.corner(-90)
        self.edge(self.hang_height)
        self.corner(90)
        self.edge(self.x)                 # oben
        self.corner(90)
        self.edge(self.hang_height)
        self.corner(-90)
        self.edge(t)
        self.corner(90)
        self.edges["F"](hh)               # links
        self.corner(90)
        self.ctx.stroke()
        self.move(tw, th, move)

    # ------------------------------------------------------------------
    def render(self):
        self.sideWall(move="right")
        self.sideWall(move="right")
        self.endWall(move="right")
        self.endWall(move="right")

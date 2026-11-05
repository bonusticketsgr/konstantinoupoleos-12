"""Shared drawing library for the clean formwork sheets (A3, 1:SCALE) built from Fespa 1:50 vector PDFs."""
import pymupdf, json, math, datetime, os, re
from shapely.geometry import Polygon, LineString, Point

S = 56.6929                      # source pt per metre (1:50)
MM = 72 / 25.4
FONT_R = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
FONT_B = pymupdf.Font(fontfile="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
BLUE = (0, 0.43, 0.85); BLACK = (0, 0, 0); GRAY = (0.35, 0.35, 0.35)
DIM_SIZE = 7.2
TICK = 2.2 * MM
ROW = 8.0 * MM

class Sheet:
    def __init__(self, geometry, texts, scale=75, ox_mm=45, oy_mm=24, page_w=420, page_h=297, sx0=None, sy0=None, fs=1.0):
        self.FS = fs                     # font scale applied to every text size (A2 sheets use ~1.25)
        self.G = json.load(open(geometry)) if isinstance(geometry, str) else geometry
        self.T = json.load(open(texts)) if isinstance(texts, str) else texts
        self.SCALE = scale; self.K = 50.0 / scale
        self.PAGE_W, self.PAGE_H = page_w * MM, page_h * MM
        self.OX, self.OY = ox_mm * MM, oy_mm * MM
        self.SX0 = sx0 if sx0 is not None else self.G["region"][0]
        self.SY0 = sy0 if sy0 is not None else self.G["region"][1]
        self.doc = pymupdf.open(); self.page = self.doc.new_page(width=self.PAGE_W, height=self.PAGE_H)
        self.shape = self.page.new_shape()
        self.texts_out = []      # (rect, text) for overlap checks

    # ---------------- transforms
    def X(self, x): return self.OX + (x - self.SX0) * self.K
    def Y(self, y): return self.OY + (y - self.SY0) * self.K
    def P(self, x, y): return pymupdf.Point(self.X(x), self.Y(y))
    def flush(self):
        self.shape.commit(); self.shape = self.page.new_shape()

    # ---------------- primitives (output coords)
    def oline(self, x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
        self.shape.draw_line(pymupdf.Point(x0, y0), pymupdf.Point(x1, y1))
        self.shape.finish(width=w, color=color, dashes=dashes, lineCap=0)
    def sline(self, x0, y0, x1, y1, w=0.5, color=BLACK, dashes=None):
        self.oline(self.X(x0), self.Y(y0), self.X(x1), self.Y(y1), w, color, dashes)
    def orect(self, x0, y0, x1, y1, w=0.5, color=BLACK, fill=None):
        self.shape.draw_rect(pymupdf.Rect(x0, y0, x1, y1)); self.shape.finish(width=w, color=color, fill=fill)
    def ocircle(self, x, y, r, w=0.35, color=BLACK, fill=None):
        self.shape.draw_circle(pymupdf.Point(x, y), r); self.shape.finish(width=w, color=color, fill=fill)
    @staticmethod
    def text_w(s, size, bold=False): return (FONT_B if bold else FONT_R).text_length(s, fontsize=size)
    def tw(self, s, size, bold=False): return self.text_w(s, size * self.FS, bold)    # width as drawn (font scale applied)

    def otext(self, x, y, s, size=7, bold=False, rot=0, align="left", color=BLACK, mask=False):
        """(x,y) = baseline start (left) / centre / right end. rot=90 -> reads bottom-to-top from (x,y), glyphs left of x.
        mask=True paints a white box behind the text (hides hatch / crossing thin lines)."""
        size = size * self.FS
        font = FONT_B if bold else FONT_R
        w = font.text_length(s, fontsize=size)
        off = -w / 2 if align == "center" else (-w if align == "right" else 0)
        if mask:
            if rot == 0: self.orect(x + off - 0.8, y - size * 0.8, x + off + w + 0.8, y + size * 0.26, 0, (1, 1, 1), (1, 1, 1))
            else: self.orect(x - size * 0.8, y - w - 0.8, x + size * 0.26, y + 0.8, 0, (1, 1, 1), (1, 1, 1))
        self.flush()
        tw = pymupdf.TextWriter(self.page.rect)
        tw.append(pymupdf.Point(x + off, y), s, font=font, fontsize=size)
        if rot == 0:
            tw.write_text(self.page, color=color)
            self.texts_out.append((pymupdf.Rect(x + off, y - size * 0.75, x + off + w, y + size * 0.22), s))
        else:
            m = pymupdf.Matrix(1, 0, 0, 1, 0, 0).prerotate(rot)
            tw.write_text(self.page, color=color, morph=(pymupdf.Point(x, y), m))
            self.texts_out.append((pymupdf.Rect(x - size * 0.75, y - w, x + size * 0.22, y), s))
        return w
    def stext(self, x, y, s, **kw): return self.otext(self.X(x), self.Y(y), s, **kw)

    def hatch_polygon(self, pts_src, spacing=2.6, angle=45, w=0.25, color=BLACK):
        poly = Polygon([(self.X(x), self.Y(y)) for x, y in pts_src])
        if not poly.is_valid: poly = poly.buffer(0)
        minx, miny, maxx, maxy = poly.bounds
        d = max(maxx - minx, maxy - miny) * 2; cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        a = math.radians(angle); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        n = int(d / spacing) + 1
        for i in range(-n, n + 1):
            ox, oy = cx + nx * i * spacing, cy + ny * i * spacing
            inter = LineString([(ox - ux * d, oy - uy * d), (ox + ux * d, oy + uy * d)]).intersection(poly)
            for g in getattr(inter, "geoms", [inter]):
                if g.is_empty or g.geom_type != "LineString": continue
                c = list(g.coords); self.oline(c[0][0], c[0][1], c[-1][0], c[-1][1], w, color)

    # ---------------- geometry from extraction
    def draw_geometry(self, rehatch_columns=False, wmap=None, drop=None):
        G = self.G
        WMAP = wmap or {1.7: 1.1, 0.85: 0.6, 0.57: 0.3, 0.28: 0.22}
        for poly in G["columns"]:
            if rehatch_columns: self.hatch_polygon(poly)
            pts = [self.P(x, y) for x, y in poly] + [self.P(*poly[0])]
            self.shape.draw_polyline(pts); self.shape.finish(width=1.1, color=BLACK)
        for ch in G.get("open17", []):
            self.shape.draw_polyline([self.P(x, y) for x, y in ch]); self.shape.finish(width=1.1, color=BLACK)
        for l in G["lines"]:
            if rehatch_columns and l.get("hatch") and self._in_column((l["x0"] + l["x1"]) / 2, (l["y0"] + l["y1"]) / 2): continue
            if drop and drop(l): continue
            self.sline(l["x0"], l["y0"], l["x1"], l["y1"], w=WMAP[l["w"]], color=BLUE if l["blue"] else BLACK)
        for c in G["curves"]:
            p = [self.P(x, y) for x, y in c["pts"]]
            self.shape.draw_bezier(*p); self.shape.finish(width=WMAP.get(c["w"], 0.6), color=BLUE if c["blue"] else BLACK)
    def _in_column(self, px, py):
        for poly in self.G["columns"]:
            if Polygon(poly).contains(Point(px, py)): return True
        return False

    # ---------------- dimensioning
    @staticmethod
    def fmt(v):
        c = int(math.floor(v * 100 + 0.5 + 1e-9))      # centimetres, half-up
        return "%d.%02d" % (c // 100, c % 100)
    def tick(self, xo, yo, color=BLACK):
        self.oline(xo - TICK / 2 * 0.7071, yo + TICK / 2 * 0.7071, xo + TICK / 2 * 0.7071, yo - TICK / 2 * 0.7071, 0.6, color)

    def hchain(self, xs, y_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True, values=None, narrow_perp=False, mask=False):
        X, Y = self.X, self.Y
        xs = sorted(xs); x0, x1 = X(xs[0]), X(xs[-1])
        self.oline(x0 - 1.0 * MM, y_out, x1 + 1.0 * MM, y_out, 0.35, color)
        for x in xs:
            xo = X(x); self.tick(xo, y_out, color)
            if ext and x in ext:
                ys = Y(ext[x]); gap = 0.8 * MM
                if ys < y_out: self.oline(xo, ys + gap, xo, y_out + ext_over, 0.25, color)
                else: self.oline(xo, ys - gap, xo, y_out - ext_over, 0.25, color)
        last1 = -1e9
        for i, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
            s = self.fmt((b - a) / S) if not values else values[i]
            if s == "": continue
            sz = size * self.FS
            w = self.text_w(s, sz); mid = (X(a) + X(b)) / 2; L = X(b) - X(a)
            lvl = 0
            if stagger and w + 1.5 > L:
                lvl = 1
                if mid - w / 2 < last1 + 1.0: lvl = 2
            if lvl == 1: last1 = mid + w / 2
            if narrow_perp and lvl > 0:
                # vertical (rotated) text centred on the narrow segment, just off the line
                xb = mid + sz * 0.36
                yb = y_out - 1.2 * MM if text_side < 0 else y_out + 1.2 * MM + w
                self.otext(xb, yb, s, size=size, rot=90, color=color, mask=mask); continue
            dy = 0.6 * MM + lvl * (sz * 0.72 + 1.6)
            yb = y_out - dy if text_side < 0 else y_out + dy + sz * 0.72
            self.otext(mid, yb, s, size=size, align="center", color=color, mask=mask)

    def vchain(self, ys, x_out, text_side=-1, size=DIM_SIZE, ext=None, ext_over=1.2 * MM, color=BLACK, stagger=True, narrow_h=False, values=None, mask=False):
        X, Y = self.X, self.Y
        ys = sorted(ys); y0, y1 = Y(ys[0]), Y(ys[-1])
        self.oline(x_out, y0 - 1.0 * MM, x_out, y1 + 1.0 * MM, 0.35, color)
        for y in ys:
            yo = Y(y); self.tick(x_out, yo, color)
            if ext and y in ext:
                xs_ = X(ext[y]); gap = 0.8 * MM
                if xs_ > x_out: self.oline(xs_ - gap, yo, x_out - ext_over, yo, 0.25, color)
                else: self.oline(xs_ + gap, yo, x_out + ext_over, yo, 0.25, color)
        last1 = -1e9
        for i, (a, b) in enumerate(zip(ys[:-1], ys[1:])):
            s = self.fmt((b - a) / S) if not values else values[i]
            if s == "": continue
            sz = size * self.FS
            w = self.text_w(s, sz); mid = (Y(a) + Y(b)) / 2; L = Y(b) - Y(a)
            lvl = 0
            if stagger and w + 1.5 > L:
                lvl = 1
                if mid - w / 2 < last1 + 1.0: lvl = 2
            if lvl == 1: last1 = mid + w / 2
            if narrow_h and lvl > 0:
                xh = x_out - 1.5 * MM - w if text_side < 0 else x_out + 1.5 * MM
                self.otext(xh, mid + sz * 0.36, s, size=size, color=color, mask=mask); continue
            dx = 0.6 * MM + lvl * (sz * 0.72 + 1.6)
            xb = x_out - dx if text_side < 0 else x_out + dx + sz * 0.72
            self.otext(xb, mid + w / 2, s, size=size, rot=90, color=color, mask=mask)

    def idim_h(self, xs, y_src, side=-1, ext_to=None, size=6.8, values=None):
        self.hchain(xs, self.Y(y_src), side, size=size, ext=ext_to, ext_over=0.8 * MM, values=values)
    def idim_v(self, ys, x_src, side=-1, ext_to=None, narrow_h=True, size=6.8, values=None):
        self.vchain(ys, self.X(x_src), side, size=size, ext=ext_to, ext_over=0.8 * MM, narrow_h=narrow_h, values=values)

    def dim_generic(self, x0, y0, x1, y1, value, text_side=-1, size=6.8, ext=None, narrow_h=True, tpos=None, trot=0, mask=False):
        """single dimension between two source points (horizontal or vertical), value string given (designer's).
        tpos=(x,y) source: write the value there (baseline-left) instead of the automatic position."""
        v = [value] if tpos is None else [""]
        if abs(y1 - y0) < 0.5:
            self.hchain([x0, x1], self.Y(y0), text_side, size=size, values=v, ext=ext, ext_over=0.8 * MM, mask=mask)
        else:
            self.vchain([y0, y1], self.X(x0), text_side, size=size, values=v, ext=ext, ext_over=0.8 * MM, narrow_h=narrow_h, mask=mask)
        if tpos is not None: self.stext(tpos[0], tpos[1], value, size=size, rot=trot, mask=mask)

    def dump_texts(self, path):
        """placed texts as source-coordinate rects (for probing)."""
        out = []
        for r, t in self.texts_out:
            out.append(([self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K, self.SX0 + (r.x1 - self.OX) / self.K, self.SY0 + (r.y1 - self.OY) / self.K], t))
        json.dump(out, open(path, "w"))

    # ---------------- labels
    def col_label(self, x, y, s, rot=0, align="left", size=8.4, mask=False): self.stext(x, y, s, size=size, bold=True, rot=rot, align=align, mask=mask)
    def beam_label(self, x, y, s, rot=0, size=7.2, align="left", mask=False): self.stext(x, y, s, size=size, rot=rot, align=align, mask=mask)
    def slab_label(self, cx, cy, name, h, r=3.0 * MM):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.35, BLACK, (1, 1, 1))
        self.oline(c.x - r, c.y, c.x + r, c.y, 0.35)
        self.otext(c.x, c.y - 1.1 * self.FS, name, size=6.8, bold=True, align="center")
        self.otext(c.x, c.y + 5.8 * self.FS, "h=%s" % h, size=6.0, align="center")
    def level_mark(self, cx, cy, s, r=1.5 * MM, color=BLACK, textpos=None, rot=0, size=7.4):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.35, color, (1, 1, 1))
        for a0 in (90, 270):
            pts = [c]
            for kk in range(0, 91, 10):
                a = math.radians(a0 + kk); pts.append(pymupdf.Point(c.x + r * math.cos(a), c.y - r * math.sin(a)))
            self.shape.draw_polyline(pts + [c]); self.shape.finish(width=0, color=color, fill=color)
        self.oline(c.x - r * 1.4, c.y, c.x + r * 1.4, c.y, 0.3, color); self.oline(c.x, c.y - r * 1.4, c.x, c.y + r * 1.4, 0.3, color)
        if textpos is None: textpos = (c.x + r + 1.5, c.y + 2.4)
        self.otext(textpos[0], textpos[1], s, size=size, bold=True, rot=rot, color=color)
    def marker(self, cx, cy, num, r=2.0 * MM):
        c = self.P(cx, cy)
        self.ocircle(c.x, c.y, r, 0.6, BLACK, (1, 1, 1))
        self.otext(c.x, c.y + 2.6, str(num), size=7.2, bold=True, align="center")
    def note(self, x_src, y_src, lines, size=6.2, rot=0, mask=False):
        """lines of text at a source point; mask=True paints a white box behind each line (interrupts crossing lines)."""
        sz = size * self.FS; lh = sz * 1.25
        for i, ln in enumerate(lines):
            w = self.text_w(ln, sz)
            if rot == 0:
                x, y = self.X(x_src), self.Y(y_src) + i * lh
                if mask: self.orect(x - 1.0, y - sz * 0.8, x + w + 1.0, y + sz * 0.28, 0, (1, 1, 1), (1, 1, 1))
                self.otext(x, y, ln, size=size)
            else:
                x, y = self.X(x_src) + i * lh, self.Y(y_src)
                if mask: self.orect(x - sz * 0.8, y - w - 1.0, x + sz * 0.28, y + 1.0, 0, (1, 1, 1), (1, 1, 1))
                self.otext(x, y, ln, size=size, rot=90)

    # ---------------- sheet frame
    def title_block(self, theme_lines, base_lines, number, legend=None, project=None):
        MMv = MM; TB_Y0, TB_Y1 = 262 * MMv, 289 * MMv
        self.orect(10 * MMv, TB_Y0, 410 * MMv, TB_Y1, 0.8)
        cols = [10 * MMv, 140 * MMv, 250 * MMv, 330 * MMv, 370 * MMv, 410 * MMv]
        for cx in cols[1:-1]: self.oline(cx, TB_Y0, cx, TB_Y1, 0.5)
        def cell(x, y, label, lines, lsize=5.6, vsize=7.0, bold=True):
            self.otext(x + 2 * MMv, y + 3.2 * MMv, label, size=lsize, color=GRAY)
            for i, ln in enumerate(lines): self.otext(x + 2 * MMv, y + 7.2 * MMv + i * (vsize + 2.2), ln, size=vsize, bold=bold)
        cell(cols[0], TB_Y0, "ΕΡΓΟ", project or ["ΑΝΕΓΕΡΣΗ ΠΕΝΤΑΟΡΟΦΟΥ ΚΤΗΡΙΟΥ ΚΑΤΟΙΚΙΩΝ ΜΕ ΥΠΟΓΕΙΟ, ΣΟΦΙΤΑ ΚΑΙ ΔΩΜΑ",
                                            "ΟΔΟΣ ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 & ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ – Ο.Τ. 103-15, ΔΗΜΟΣ ΕΛΛΗΝΙΚΟΥ-ΑΡΓΥΡΟΥΠΟΛΗΣ"], vsize=6.6)
        self.otext(cols[0] + 2 * MMv, TB_Y0 + 20.5 * MMv, "ΕΡΓΟΔΟΤΗΣ: ARKAD Ι.Κ.Ε.     ΜΕΛΕΤΗΤΗΣ ΣΤΑΤΙΚΩΝ: ΓΙΩΡΓΟΣ ΚΟΓΙΑΣ, ΠΟΛΙΤΙΚΟΣ ΜΗΧΑΝΙΚΟΣ", size=6.2)
        cell(cols[1], TB_Y0, "ΘΕΜΑ ΣΧΕΔΙΟΥ", theme_lines, vsize=8.0)
        if legend: self.otext(cols[1] + 2 * MMv, TB_Y0 + 22.5 * MMv, legend, size=5.4, color=GRAY)
        cell(cols[2], TB_Y0, "ΒΑΣΗ", base_lines, vsize=6.6, bold=False)
        cell(cols[3], TB_Y0, "ΚΛΙΜΑΚΑ", ["1:%d" % self.SCALE, "A3"], vsize=11.0)
        cell(cols[4], TB_Y0, "ΑΡ. ΣΧΕΔΙΟΥ / ΗΜΕΡΟΜΗΝΙΑ", [number, datetime.date.today().strftime("%d/%m/%Y")], vsize=8.6)
        # scale bar
        sbx, sby = 336 * MMv, 254 * MMv; u = S * self.K
        for i in range(5): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.6 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(6): self.otext(sbx + i * u, sby - 1.2 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx + 5.4 * u, sby + 1.4 * MMv, "m  (1:%d)" % self.SCALE, size=5.5)

    def save(self, path, meta=None):
        self.flush()
        if meta: self.doc.set_metadata(meta)
        self.doc.save(path, garbage=4, deflate=True)
        json.dump(dict(K=self.K, OX=self.OX, OY=self.OY, SX0=self.SX0, SY0=self.SY0), open(path + ".meta.json", "w"))

    # ---------------- checks
    def check(self, exclude_y_above=None):
        """text/text overlaps and text over solid structural lines or columns (output coords)."""
        import itertools
        from shapely.geometry import box
        def shrink(r, f=0.12):
            h = min(r.width, r.height) * f; return pymupdf.Rect(r.x0 + h, r.y0 + h, r.x1 - h, r.y1 - h)
        spans = self.texts_out
        n = 0
        for (r1, t1), (r2, t2) in itertools.combinations(spans, 2):
            if shrink(r1).intersects(shrink(r2)): n += 1; print("TEXT OVERLAP:", t1, "|", t2, [round(v) for v in r1])
        lines = [(LineString([(self.X(l["x0"]), self.Y(l["y0"])), (self.X(l["x1"]), self.Y(l["y1"]))]), l) for l in self.G["lines"] if l["w"] >= 0.85 and not l.get("dashed")]
        cols = [Polygon([(self.X(x), self.Y(y)) for x, y in c]) for c in self.G["columns"]]
        bad = 0
        for r, t in spans:
            if exclude_y_above and r.y0 > exclude_y_above: continue
            h = min(r.width, r.height) * 0.2
            bb = box(r.x0 + h, r.y0 + h, r.x1 - h, r.y1 - h)
            hit = [l for ln, l in lines if ln.intersects(bb)]
            if hit:
                bad += 1; l = hit[0]
                print("|%s| crosses a solid structural line at src (%.0f,%.0f): line (%.1f,%.1f)-(%.1f,%.1f) w=%s%s" % (t, self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K, l["x0"], l["y0"], l["x1"], l["y1"], l["w"], " blue" if l["blue"] else ""))
            if any(bb.intersects(c) for c in cols): bad += 1; print("|%s| over a column at src (%.0f,%.0f)" % (t, self.SX0 + (r.x0 - self.OX) / self.K, self.SY0 + (r.y0 - self.OY) / self.K))
        print("text overlaps:", n, " structural conflicts:", bad)
        return n, bad

    def title_box(self, x0_mm, y0_mm, w_mm, title_lines, address_lines, scale_label=None, bar_m=2):
        """minimal title box (top-left corner at x0,y0 in mm): drawing title, scale (+ scale bar on its own line), address."""
        MMv = MM; x0, x1 = x0_mm * MMv, (x0_mm + w_mm) * MMv
        tsz, asz, ssz = 9.6, 7.6, 10.0
        th, ah, sh_ = tsz * self.FS, asz * self.FS, ssz * self.FS
        y0 = y0_mm * MMv
        y = y0 + 3.5 * MMv + th * 0.75
        for ln in title_lines: self.otext(x0 + 3 * MMv, y, ln, size=tsz, bold=True); y += th + 3
        y_sep1 = y - th * 0.75 - 1.0 * MMv + th * 0.75 - 2.0
        y_sep1 = y - 1.0 * MMv - 3
        y = y_sep1 + 3.0 * MMv + sh_ * 0.75
        self.otext(x0 + 3 * MMv, y, scale_label or ("ΚΛΙΜΑΚΑ 1:%d" % self.SCALE), size=ssz, bold=True)
        u = S * self.K; sbx = x0 + 3 * MMv; sby = y + 2.2 * MMv
        n = min(bar_m, int((x1 - 4 * MMv - sbx) / u))
        for i in range(n): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.8 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(n + 1): self.otext(sbx + i * u, sby + 1.8 * MMv + 2.8 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx + n * u + 2.0 * MMv, sby + 1.8 * MMv + 2.8 * MMv, "m", size=5.5)
        y_sep2 = sby + 1.8 * MMv + 2.8 * MMv + 2.0 * MMv
        y = y_sep2 + 3.0 * MMv + ah * 0.75
        for ln in address_lines: self.otext(x0 + 3 * MMv, y, ln, size=asz, bold=False); y += ah + 2.5
        y1 = y - ah - 2.5 + ah * 0.3 + 3.0 * MMv
        self.orect(x0, y0, x1, y1, 0.8); self.oline(x0, y_sep1, x1, y_sep1, 0.4); self.oline(x0, y_sep2, x1, y_sep2, 0.4)
        return (x0, y0, x1, y1)

    def title_column(self, x0_mm, theme_lines, base_lines, number, legend=None, width_mm=50, y0_mm=10, y1_mm=287):
        """vertical title block at the right edge (for wide plans)."""
        MMv = MM; x0, x1 = x0_mm * MMv, (x0_mm + width_mm) * MMv; y0, y1 = y0_mm * MMv, y1_mm * MMv
        self.orect(x0, y0, x1, y1, 0.8)
        def block(y, label, lines, vsize=6.4, bold=True, lh=None):
            self.otext(x0 + 2 * MMv, y + 3.0 * MMv, label, size=5.4, color=GRAY)
            lh = lh or (vsize + 2.0)
            for i, ln in enumerate(lines): self.otext(x0 + 2 * MMv, y + 6.6 * MMv + i * lh, ln, size=vsize, bold=bold)
            return y + 6.6 * MMv + len(lines) * lh + 1.5 * MMv
        y = y0
        y = block(y, "ΕΡΓΟ", ["ΑΝΕΓΕΡΣΗ ΠΕΝΤΑΟΡΟΦΟΥ ΚΤΗΡΙΟΥ", "ΚΑΤΟΙΚΙΩΝ ΜΕ ΥΠΟΓΕΙΟ,", "ΣΟΦΙΤΑ ΚΑΙ ΔΩΜΑ"], vsize=6.6)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΘΕΣΗ", ["ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 12 &", "ΑΓΙΑΣ ΒΑΡΒΑΡΑΣ – Ο.Τ. 103-15", "ΔΗΜΟΣ ΕΛΛΗΝΙΚΟΥ-ΑΡΓΥΡΟΥΠΟΛΗΣ"], vsize=6.2, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΕΡΓΟΔΟΤΗΣ", ["ARKAD Ι.Κ.Ε."], vsize=6.6)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΜΕΛΕΤΗΤΗΣ ΣΤΑΤΙΚΩΝ", ["ΓΙΩΡΓΟΣ ΚΟΓΙΑΣ", "ΠΟΛΙΤΙΚΟΣ ΜΗΧΑΝΙΚΟΣ"], vsize=6.4, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΘΕΜΑ ΣΧΕΔΙΟΥ", theme_lines, vsize=7.4)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΒΑΣΗ", base_lines, vsize=6.2, bold=False)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΚΛΙΜΑΚΑ", ["1:%d   (A3)" % self.SCALE], vsize=11.0)
        self.oline(x0, y, x1, y, 0.4)
        y = block(y, "ΑΡ. ΣΧΕΔΙΟΥ / ΗΜΕΡΟΜΗΝΙΑ", [number, datetime.date.today().strftime("%d/%m/%Y")], vsize=8.0)
        self.oline(x0, y, x1, y, 0.4)
        if legend:
            yy = y + 3.0 * MMv
            for ln in legend: self.otext(x0 + 2 * MMv, yy, ln, size=5.4, color=GRAY); yy += 6.6
            y = yy + 1 * MMv
            self.oline(x0, y, x1, y, 0.4)
        # scale bar
        sbx, sby = x0 + 3 * MMv, y1 - 9 * MMv; u = S * self.K
        n = int((width_mm - 8) * MMv / u)
        for i in range(n): self.orect(sbx + i * u, sby, sbx + (i + 1) * u, sby + 1.6 * MMv, 0.3, fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1))
        for i in range(n + 1): self.otext(sbx + i * u, sby - 1.2 * MMv, str(i), size=5.5, align="center")
        self.otext(sbx, sby + 5.5 * MMv, "m  (1:%d)" % self.SCALE, size=5.5)


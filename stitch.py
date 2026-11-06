"""Generates a drifting, gently undulating baseball-stitch divider (light + dark) for the profile README."""
import math, os

W, H = 820, 100
MID = H / 2
WAVELEN = 700                       # main curve wavelength = loop distance (multiple of SPACING)
SPACING = 25                        # px between stitches
DRIFT_SECONDS = 40                  # time to drift one wavelength
SWELL_SECONDS = 7                   # time for one full undulation cycle
ARM, SPREAD, GAP = 8, 18.75, 6.5    # stitch slant, outer reach, seam gap
STROKE, SEAM_STROKE = 4, 2.5

# Undulation keyframes: (main amplitude, ripple amplitude). The ripple is a half-wavelength
# harmonic, so blending between frames makes the seam flex like a rope instead of just sliding.
FRAMES = [(12.5, 4.0), (9.0, -4.5), (12.5, 4.0)]

THEMES = {
    "light": dict(stitch="#d23c3c", seam="#e4e4e7"),
    "dark":  dict(stitch="#e5534b", seam="#30363d"),
}

K = 2 * math.pi / WAVELEN
XS = range(-WAVELEN, W + WAVELEN + 1, SPACING)


def y(x, a1, a2):
    return MID + a1 * math.sin(K * x) + a2 * math.sin(2 * K * x + 0.9)


def dy(x, a1, a2):
    return a1 * K * math.cos(K * x) + a2 * 2 * K * math.cos(2 * K * x + 0.9)


def seam_d(a1, a2):
    return "M" + " L".join(f"{x},{y(x, a1, a2):.2f}" for x in range(-WAVELEN, W + WAVELEN + 1, 5))


def stitches_d(a1, a2):
    parts = []
    for x in XS:
        cx, cy = x, y(x, a1, a2)
        ang = math.atan(dy(x, a1, a2))
        c, s = math.cos(ang), math.sin(ang)
        rot = lambda px, py: (cx + px * c - py * s, cy + px * s + py * c)
        (ax, ay), (bx, by) = rot(-ARM, -SPREAD), rot(0, -GAP)
        (ex, ey), (fx, fy) = rot(-ARM, SPREAD), rot(0, GAP)
        parts.append(f"M{ax:.1f},{ay:.1f}L{bx:.1f},{by:.1f}M{ex:.1f},{ey:.1f}L{fx:.1f},{fy:.1f}")
    return "".join(parts)


def morph(fn):
    n = len(FRAMES) - 1
    values = ";".join(fn(*f) for f in FRAMES)
    splines = ";".join(["0.45 0 0.55 1"] * n)
    key_times = ";".join(f"{i / n:g}" for i in range(n + 1))
    return (f'<animate attributeName="d" dur="{SWELL_SECONDS}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="{key_times}" keySplines="{splines}" values="{values}"/>')


def build(t):
    mask = ('<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask>')
    css = (f".d{{animation:drift {DRIFT_SECONDS}s linear infinite;}}"
           f"@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX({-WAVELEN}px)}}}}"
           "@media (prefers-reduced-motion:reduce){.d{animation:none}}")
    a1, a2 = FRAMES[0]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="baseball stitch divider">'
        f'<defs>{mask}</defs><style>{css}</style><g mask="url(#m)"><g class="d">'
        f'<path d="{seam_d(a1, a2)}" fill="none" stroke="{t["seam"]}" stroke-width="{SEAM_STROKE}">{morph(seam_d)}</path>'
        f'<path d="{stitches_d(a1, a2)}" fill="none" stroke="{t["stitch"]}" stroke-width="{STROKE}" '
        f'stroke-linecap="round">{morph(stitches_d)}</path>'
        f'</g></g></svg>\n'
    )


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    for name, theme in THEMES.items():
        open(f"assets/stitch-{name}.svg", "w").write(build(theme))
    print("wrote assets/stitch-light.svg, assets/stitch-dark.svg")

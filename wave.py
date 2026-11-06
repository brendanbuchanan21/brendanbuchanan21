"""Generates a thin, slowly rippling wave divider (light + dark) for the profile README."""
import math, os

W, H = 820, 36

def wave_path(wavelength, amp, mid, extra):
    pts = []
    for x in range(-extra, W + extra + 1, 2):
        y = mid + amp * math.sin(2 * math.pi * x / wavelength)
        pts.append(f"{x},{y:.2f}")
    return "M" + " L".join(pts)

LAYERS = [  # (wavelength, amplitude, seconds per wavelength, opacity, direction)
    (120, 5.0, 4.0, 1.0, 1),
    (180, 3.5, 7.0, 0.45, -1),
]

THEMES = {"light": "#9a9aa2", "dark": "#7d8590"}

def build(color):
    css, paths = [], []
    for i, (wl, amp, sec, op, d) in enumerate(LAYERS):
        css.append(f".w{i}{{animation:m{i} {sec}s linear infinite;}}"
                   f"@keyframes m{i}{{from{{transform:translateX(0)}}to{{transform:translateX({-d * wl}px)}}}}")
        paths.append(f'<path class="w{i}" d="{wave_path(wl, amp, H / 2, 2 * wl)}" fill="none" '
                     f'stroke="{color}" stroke-width="1.4" stroke-linecap="round" opacity="{op}"/>')
    fade = ('<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="wave divider">'
            f'<defs>{fade}</defs><style>{"".join(css)}'
            '@media (prefers-reduced-motion:reduce){path{animation:none}}</style>'
            f'<g mask="url(#m)">{"".join(paths)}</g></svg>\n')

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    for name, color in THEMES.items():
        open(f"assets/wave-{name}.svg", "w").write(build(color))
    print("wrote assets/wave-light.svg, assets/wave-dark.svg")

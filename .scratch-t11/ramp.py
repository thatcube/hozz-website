"""Find the purple ramp that is c45's ramp in another hue.

c45, measured: 6 stops, total rim->centre ΔE 26.07, mean step ΔE 5.21, ΔL 20.0,
rim near-neutral and the centre carrying the chroma.

The step size is the thing the eye reacts to, so that is what is held. Anchor:
the middle of the ramp should land on Twozz's own #8f52f6, so the bubble still
reads as the purple it ships as, with the rim lighter and the core deeper.
"""


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def unlin(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def to_lab(hexstr):
    r, g, b = (lin(int(hexstr[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return xyz_to_lab(r * 0.4124 + g * 0.3576 + b * 0.1805,
                      r * 0.2126 + g * 0.7152 + b * 0.0722,
                      r * 0.0193 + g * 0.1192 + b * 0.9505)


def xyz_to_lab(X, Y, Z):
    Xn, Yn, Zn = 0.95047, 1.0, 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = f(X / Xn), f(Y / Yn), f(Z / Zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lab_to_rgb(L, a, b):
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def g(t):
        return t ** 3 if t ** 3 > 216 / 24389 else (t - 4 / 29) * 108 / 841
    X, Y, Z = g(fx) * 0.95047, g(fy), g(fz) * 1.08883
    r = X * 3.2406 + Y * -1.5372 + Z * -0.4986
    gg = X * -0.9689 + Y * 1.8758 + Z * 0.0415
    bb = X * 0.0557 + Y * -0.2040 + Z * 1.0570
    out = [unlin(max(0.0, min(1.0, v))) for v in (r, gg, bb)]
    clipped = any(v < -0.001 or v > 1.001 for v in (r, gg, bb))
    return '#%02x%02x%02x' % tuple(round(v * 255) for v in out), clipped


def de(a, b):
    return sum((x - y) ** 2 for x, y in zip(to_lab(a), to_lab(b))) ** 0.5


BRAND = '#8f52f6'
L0, a0, b0 = to_lab(BRAND)
C0 = (a0 ** 2 + b0 ** 2) ** 0.5
print(f'{BRAND}  L {L0:.1f}  a {a0:.1f}  b {b0:.1f}  C {C0:.1f}')
print(f"{'#7243c3':8} {to_lab('#7243c3')}")
print(f"{'#ad84ec':8} {to_lab('#ad84ec')}")

TARGET_TOTAL, TARGET_STEP = 26.07, 5.21

print('\n  up   down  krim  kcore   ramp                                            '
      'total  step  clip')
best = None
for up in (10, 11, 12, 13, 14):
    for down in (6, 7, 8, 9, 10):
        for krim in (0.72, 0.78, 0.84, 0.90, 1.0):
            for kcore in (1.0, 1.06, 1.12):
                rim = (L0 + up, a0 * krim, b0 * krim)
                core = (L0 - down, a0 * kcore, b0 * kcore)
                stops, clip = [], False
                for i in range(6):
                    t = i / 5
                    lab = tuple(rim[c] + (core[c] - rim[c]) * t for c in range(3))
                    h, cl = lab_to_rgb(*lab)
                    clip |= cl
                    stops.append(h)
                total = de(stops[0], stops[-1])
                steps = [de(x, y) for x, y in zip(stops, stops[1:])]
                mean = sum(steps) / len(steps)
                spread = max(steps) - min(steps)
                score = abs(total - TARGET_TOTAL) + abs(mean - TARGET_STEP) * 2 + spread + clip * 5
                row = (score, up, down, krim, kcore, stops, total, mean, spread, clip)
                if best is None or score < best[0]:
                    best = row
                if abs(total - TARGET_TOTAL) < 1.2 and not clip and spread < 1.2:
                    print(f'  {up:4} {down:5} {krim:5.2f} {kcore:6.2f}   {" ".join(stops)}  '
                          f'{total:5.2f} {mean:5.2f}  spread {spread:.2f}')

print('\nbest by score:')
_, up, down, krim, kcore, stops, total, mean, spread, clip = best
print(f'  up {up} down {down} krim {krim} kcore {kcore}')
print(f'  {" ".join(stops)}  total {total:.2f} mean {mean:.2f} spread {spread:.2f} clip {clip}')

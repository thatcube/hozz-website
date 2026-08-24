"""Pick the ramp: interpolate in Oklab, and compare step sizes against Plozz's."""
import math


def srgb_to_lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


def to_oklab(hexs):
    r, g, b = (srgb_to_lin(int(hexs[i:i + 2], 16)) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def from_oklab(lab):
    L, A, B = lab
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return '#%02x%02x%02x' % (lin_to_srgb(r), lin_to_srgb(g), lin_to_srgb(b))


def de(a, b):
    p, q = to_oklab(a), to_oklab(b)
    return math.dist(p, q)


def ramp(a, b, n):
    p, q = to_oklab(a), to_oklab(b)
    return [from_oklab(tuple(p[i] + (q[i] - p[i]) * k / (n - 1) for i in range(3)))
            for k in range(n)]


print('Plozz screen ramp, measured:')
P = ['#97e3fe', '#82deff', '#72daff']
for a, b in zip(P, P[1:]):
    print(f'  {a} -> {b}   dE {de(a, b):.4f}')
print(f'  span {P[0]} -> {P[-1]}  dE {de(P[0], P[-1]):.4f}')
print()

for a, b in (('#f2f9fd', '#a9cfe8'), ('#f2f9fd', '#9dc8e5'), ('#f4fafd', '#a2cbe6')):
    for n in (7,):
        r = ramp(a, b, n)
        steps = [de(x, y) for x, y in zip(r, r[1:])]
        print(f'{a} -> {b}, {n} tones')
        print('  ', ' '.join(r))
        print(f'   step dE min {min(steps):.4f} max {max(steps):.4f} '
              f'| span dE {de(r[0], r[-1]):.4f} '
              f'| vs Plozz step {de(P[0], P[1]):.4f}')
        print(f'   nearest existing: LIT #eaf5fb dE to r1 {de("#eaf5fb", r[1]):.4f}; '
              f'FIELD #cfe3ef dE to r3 {de("#cfe3ef", r[3]):.4f}')
        print()

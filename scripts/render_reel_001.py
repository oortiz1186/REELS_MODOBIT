from PIL import Image, ImageDraw, ImageFont
import os, math, wave, struct, subprocess, textwrap
import numpy as np

W, H = 1080, 1920
NAVY = (4, 18, 36)
NAVY2 = (8, 30, 57)
WHITE = (245, 248, 252)
YELLOW = (255, 190, 0)
CYAN = (45, 160, 255)
MUTED = (175, 188, 204)

OUTDIR = "output/reel001"
os.makedirs(OUTDIR, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def gradient_bg():
    img = Image.new("RGB", (W, H), NAVY)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(NAVY[i] * (1 - t) + NAVY2[i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = c

    d = ImageDraw.Draw(img)
    for x in range(70, W, 95):
        for y in range(80, H, 110):
            r = 2 if (x + y) // 50 % 2 else 3
            d.ellipse((x-r, y-r, x+r, y+r), fill=(25, 72, 112))

    d.line((60, 120, 220, 120), fill=YELLOW, width=10)
    d.line((60, 120, 60, 270), fill=YELLOW, width=10)
    d.line((W-60, H-120, W-220, H-120), fill=YELLOW, width=10)
    d.line((W-60, H-120, W-60, H-270), fill=YELLOW, width=10)
    return img


def center_text(draw, lines, y, sizes, colors, gaps=10):
    yy = y
    for txt, sz, color in zip(lines, sizes, colors):
        f = font(sz, True)
        bbox = draw.textbbox((0, 0), txt, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, yy), txt, font=f, fill=color)
        yy += sz + gaps


def brand_footer(draw):
    f = font(42, True)
    txt = "MODO BIT"
    bbox = draw.textbbox((0, 0), txt, font=f)
    draw.text(((W-(bbox[2]-bbox[0]))/2, H-230), txt, font=f, fill=WHITE)

    f2 = font(26, False)
    txt2 = "TECNOLOGÍA QUE SÍ TE SIRVE"
    bbox2 = draw.textbbox((0, 0), txt2, font=f2)
    draw.text(((W-(bbox2[2]-bbox2[0]))/2, H-175), txt2, font=f2, fill=YELLOW)


slides = [
    ("01", ["¿PAGAR", "CHATGPT?"], [112, 150], [WHITE, YELLOW], "Antes de pagar todos los meses… mira esto."),
    ("02", ["GRATIS", "≠ INÚTIL"], [132, 132], [WHITE, YELLOW], "Para muchas tareas del día a día, la versión gratuita puede ser suficiente."),
    ("03", ["IDEAS · TEXTOS", "APRENDIZAJE", "TAREAS DIARIAS"], [78, 88, 78], [WHITE, WHITE, CYAN], "No necesitas pagar solo para empezar a aprovechar la IA."),
    ("04", ["¿LO USAS PARA", "TRABAJAR?"], [92, 132], [WHITE, YELLOW], "Programar, analizar archivos y trabajar todos los días cambia la decisión."),
    ("05", ["¿ES CHATGPT", "LA MEJOR IA?"], [98, 120], [WHITE, YELLOW], "La pregunta interesante no es solo si pagar… sino cuál IA elegir."),
    ("06", ["CHATGPT", "VS GEMINI VS", "DEEPSEEK"], [110, 74, 110], [WHITE, YELLOW, WHITE], "Mismas pruebas. Mismas tareas. ¿Cuál gana?"),
    ("07", ["SÍGUENOS", "PARA VER", "CUÁL GANA"], [118, 90, 108], [YELLOW, WHITE, WHITE], "Entiende · Prueba · Decide"),
]

slide_files = []
for sid, lines, sizes, colors, sub in slides:
    img = gradient_bg()
    d = ImageDraw.Draw(img)

    chip = "MODO IA"
    cf = font(30, True)
    cb = d.textbbox((0, 0), chip, font=cf)
    cw = cb[2] - cb[0] + 52
    d.rounded_rectangle((60, 55, 60+cw, 112), radius=20, fill=(39, 77, 145))
    d.text((86, 68), chip, font=cf, fill=WHITE)

    center_text(d, lines, 430, sizes, colors, gaps=28)

    sf = font(42, False)
    yy = 1100
    for ln in textwrap.wrap(sub, width=34):
        bb = d.textbbox((0, 0), ln, font=sf)
        d.text(((W-(bb[2]-bb[0]))/2, yy), ln, font=sf, fill=MUTED)
        yy += 58

    d.rounded_rectangle((220, 1000, 860, 1012), radius=6, fill=YELLOW)
    brand_footer(d)

    path = os.path.join(OUTDIR, f"slide_{sid}.png")
    img.save(path)
    slide_files.append(path)

# Audio ambiente sintético simple. Para publicación final se recomienda sustituirlo
# por música con licencia adecuada y agregar la narración de Modo Bit.
sr = 44100
duration = 35.0
t = np.linspace(0, duration, int(sr * duration), endpoint=False)
audio = (
    0.05 * np.sin(2 * np.pi * 110 * t) +
    0.03 * np.sin(2 * np.pi * 220 * t) +
    0.02 * np.sin(2 * np.pi * 330 * t)
)
pulse = 0.55 + 0.45 * (0.5 * (1 + np.sin(2 * np.pi * 0.5 * t)))
audio *= pulse
fade = int(sr * 1.2)
env = np.ones_like(audio)
env[:fade] = np.linspace(0, 1, fade)
env[-fade:] = np.linspace(1, 0, fade)
audio *= env

wav_path = os.path.join(OUTDIR, "ambient.wav")
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    for s in (np.clip(audio, -0.95, 0.95) * 32767).astype(np.int16):
        wf.writeframes(struct.pack("<h", int(s)))

inputs = []
for p in slide_files:
    inputs += ["-loop", "1", "-t", "5", "-i", p]
inputs += ["-i", wav_path]

filters = []
for idx in range(len(slide_files)):
    filters.append(f"[{idx}:v]scale={W}:{H},format=yuv420p,setsar=1[v{idx}]")

prev = "v0"
offset = 4.7
for idx in range(1, len(slide_files)):
    out = f"x{idx}"
    filters.append(f"[{prev}][v{idx}]xfade=transition=fade:duration=0.3:offset={offset:.1f}[{out}]")
    prev = out
    offset += 4.7

mp4_path = os.path.join(OUTDIR, "MODOBIT_REEL_001_CHATGPT_DRAFT.mp4")
cmd = [
    "ffmpeg", "-y", *inputs,
    "-filter_complex", ";".join(filters),
    "-map", f"[{prev}]",
    "-map", f"{len(slide_files)}:a",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
    "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "128k",
    "-shortest", mp4_path
]
subprocess.run(cmd, check=True)
print(mp4_path)

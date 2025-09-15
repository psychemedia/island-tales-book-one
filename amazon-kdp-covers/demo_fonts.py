import subprocess
from pathlib import Path


def is_usable_font(name):
    # Basic ASCII check
    if not all(ord(c) < 128 for c in name):
        return False
    # Skip known problematic fonts
    skip_keywords = [
        "Emoji",
        "Apple Color",
        "Symbol",
        "LastResort",
        "Bitmap",
        "Last Resort",
        "System Font",
        "Aqua",
    ]
    if any(keyword in name for keyword in skip_keywords):
        return False
    # Skip hidden/system fonts
    if name.startswith("."):
        return False
    return True


# -----------------------------
# Configuration
# -----------------------------
latex_filename = "mac_fonts_catalog.tex"
sample_text = "A Legend of Puckaster Cove"

# -----------------------------
# 1. Get full font names (fc-list :full)
# -----------------------------
try:
    result = subprocess.run(
        ["fc-list", ":full"], capture_output=True, text=True, check=True
    )
    fonts = set()
    for line in result.stdout.splitlines():
        # fc-list output format: /path/to/font.ttf: Font Name:style=Regular
        parts = line.split(":")
        if len(parts) >= 2:
            name = parts[1].strip()
            # skip hidden/system fonts starting with dot
            if not name.startswith(".") and name:
                fonts.add(name)
    fonts = sorted(fonts)
except FileNotFoundError:
    print("fc-list not found. Install fontconfig via Homebrew: brew install fontconfig")
    exit(1)
except subprocess.CalledProcessError:
    print("Error running fc-list")
    exit(1)

if not fonts:
    print("No usable fonts found.")
    exit(1)

print(f"Found {len(fonts)} fonts.")

# -----------------------------
# 2. Generate LaTeX file
# -----------------------------
latex_file = Path(latex_filename)
with latex_file.open("w", encoding="utf-8") as f:
    f.write(r"\documentclass{article}" + "\n")
    f.write(r"\usepackage{fontspec}" + "\n")
    f.write(r"\usepackage[margin=1in]{geometry}" + "\n")
    f.write(r"\begin{document}" + "\n")
    f.write(r"\raggedright" + "\n")  # prevent underfull \hbox warnings
    f.write(r"\section*{macOS System Font Catalog}" + "\n\n")

    for font in fonts:
        font_name = font.split(",")[0].strip()
        if not is_usable_font(font_name):
            continue

        font_esc = (
            font_name.replace("_", r"\_")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("#", r"\#")
        )

        f.write(
            r"\noindent {\fontspec{"
            + font_esc
            + "} "
            + font_esc
            + ": "
            + sample_text
            + r"}\\"
            + "\n\n"
        )

    f.write(r"\end{document}" + "\n")

print(f"Generated {latex_file}")

# -----------------------------
# 3. Compile with XeLaTeX
# -----------------------------
try:
    subprocess.run(["xelatex", str(latex_file)], check=True)
    print(f"Compilation finished: {latex_file.with_suffix('.pdf')}")
except FileNotFoundError:
    print("xelatex not found. Make sure XeLaTeX is installed.")
except subprocess.CalledProcessError:
    print("XeLaTeX compilation failed.")

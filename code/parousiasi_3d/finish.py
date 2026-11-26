"""ΠΑΡΟΥΣΙΑΣΗ 3D – τελικά αρχεία: οι εικόνες PNG του Blender → JPG (ποιότητα 93) στον φάκελο παραδοτέων, με ελληνικά ονόματα, μία εικόνα ανά αρχείο.

    python3 finish.py <φάκελος με τα PNG> [<φάκελος παραδοτέων>]"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ_12_ΑΡΓΥΡΟΥΠΟΛΗ", "ΠΑΡΟΥΣΙΑΣΗ_3D")
NAMES = {
    "01_saloni_apo_eisodo": "ΣΑΛΟΝΙ_01_από_την_είσοδο",
    "02_saloni_pros_kouzina": "ΣΑΛΟΝΙ_02_προς_τραπεζαρία_και_κουζίνα",
    "03_kanapes": "ΣΑΛΟΝΙ_03_καναπές",
    "04_trapezaria": "ΣΑΛΟΝΙ_04_τραπεζαρία",
    "05_kouzina": "ΚΟΥΖΙΝΑ_05",
    "06_kouzina_pros_saloni": "ΚΟΥΖΙΝΑ_06_προς_το_σαλόνι",
}


def main(src, dst=OUT):
    os.makedirs(dst, exist_ok=True)
    done = []
    for key, name in NAMES.items():
        p = os.path.join(src, key + ".png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        q = os.path.join(dst, name + ".jpg")
        im.save(q, "JPEG", quality=93, subsampling=0, optimize=True)
        done.append((name, im.size, os.path.getsize(q) // 1024))
    for n, s, kb in done:
        print("%-45s %d × %d  %d KB" % (n, s[0], s[1], kb))
    return done


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else OUT)

"""ΠΑΡΟΥΣΙΑΣΗ 3D – κατεβάζει τις υφές / τον ουρανό / τα μοντέλα της σκηνής στην αποθήκη (εκτός repo).

    python3 fetch_assets.py --dest <φάκελος> [--tex 2k] [--hdri 4k] [--model 2k]      # ό,τι λείπει, από το assets_manifest.json
    python3 fetch_assets.py --resolve                                                # ξαναφτιάχνει το manifest από τη λίστα WANT (μόνο όταν αλλάζει)

Τρέχει με απλή python3 (όχι Blender). Χρειάζεται curl ή πρόσβαση στο δίκτυο. Τίποτα από το έργο δεν στέλνεται προς τα έξω."""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assets as A

# Ό,τι χρησιμοποιεί η σκηνή (βλ. scene.py / furniture.py / decor.py / exterior.py)
WANT = dict(
    textures=["oak_veneer_01", "oak_veneer_05", "curly_teddy_natural", "hessian_230", "rough_linen", "velour_velvet",
              "poly_wool_herringbone", "leather_white", "white_stucco"],
    hdris=["qwantani_late_afternoon_puresky", "table_mountain_1_puresky", "autumn_field_puresky"],
    models=["island_tree_01", "island_tree_02", "island_tree_03", "potted_plant_01", "potted_plant_02", "potted_plant_04", "throw_pillows_01",
            "mid_century_lounge_chair", "ceramic_vase_01", "ceramic_vase_02", "ceramic_vase_03", "ceramic_vase_04", "wooden_bowl_01"],
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest")
    ap.add_argument("--tex", default="2k")
    ap.add_argument("--hdri", default="4k")
    ap.add_argument("--model", default="2k")
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--add-models", nargs="*", default=[])
    a = ap.parse_args()
    if a.resolve:
        M = A.resolve(WANT["textures"], WANT["hdris"], WANT["models"] + a.add_models)
        print("manifest:", {k: len(v) for k, v in M.items()})
        return
    A.configure(a.dest, a.tex, a.hdri, a.model)
    bad = A.fetch(only=a.only)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

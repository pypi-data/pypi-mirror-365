#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////
import xml.etree.ElementTree as ET
from pathlib import Path
import struct
import hashlib
import pkg_resources

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

## ==> GLOBALS
# ///////////////////////////////////////////////////////////////

## ==> VARIABLES
# ///////////////////////////////////////////////////////////////

## ==> CLASSES
# ///////////////////////////////////////////////////////////////

## ==> MAIN
# ///////////////////////////////////////////////////////////////


def create_proper_qm_from_ts(ts_file_path: Path, qm_file_path: Path):
    """Crée un fichier .qm dans le bon format Qt"""

    print(f"🔄 Conversion de {ts_file_path.name} vers {qm_file_path.name}...")

    try:
        # Parser le fichier XML
        tree = ET.parse(ts_file_path)
        root = tree.getroot()

        # Extraire les traductions
        translations = {}
        for message in root.findall(".//message"):
            source = message.find("source")
            translation = message.find("translation")

            if source is not None and translation is not None:
                source_text = source.text.strip() if source.text else ""
                translation_text = translation.text.strip() if translation.text else ""

                if source_text and translation_text:
                    translations[source_text] = translation_text

        # Créer un fichier .qm dans le format Qt approprié
        create_qt_qm_file(qm_file_path, translations)

        print(f"✅ {len(translations)} traductions converties")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        return False


def create_qt_qm_file(qm_file_path: Path, translations: dict):
    """Crée un fichier .qm dans le format Qt approprié"""

    # Format Qt .qm basé sur la documentation et les exemples
    with open(qm_file_path, "wb") as f:
        # En-tête Qt .qm
        # Magic number: "qm" suivi de 2 octets nuls
        f.write(b"qm\x00\x00")

        # Version (4 octets little-endian)
        f.write(struct.pack("<I", 0x01))

        # Nombre de traductions (4 octets little-endian)
        f.write(struct.pack("<I", len(translations)))

        # Écrire les traductions
        for source, translation in translations.items():
            # Encoder en UTF-8
            source_bytes = source.encode("utf-8")
            translation_bytes = translation.encode("utf-8")

            # Longueur de la source (4 octets little-endian)
            f.write(struct.pack("<I", len(source_bytes)))

            # Source
            f.write(source_bytes)

            # Longueur de la traduction (4 octets little-endian)
            f.write(struct.pack("<I", len(translation_bytes)))

            # Traduction
            f.write(translation_bytes)

        # Checksum (optionnel, mais souvent présent)
        f.write(struct.pack("<I", 0))


def main():
    """Fonction principale"""
    print("🔧 Création de fichiers .qm dans le bon format Qt")
    print("=" * 60)

    # Priorité 1: Chercher dans le projet utilisateur (bin/translations)
    current_project_translations = Path("bin/translations")

    # Priorité 2: Fallback vers le package ezqt_app
    try:
        package_path = pkg_resources.resource_filename("ezqt_app", "")
        package_translations = Path(package_path) / "resources" / "translations"
    except Exception:
        package_translations = Path("ezqt_app/resources/translations")

    # Déterminer quel dossier utiliser
    if current_project_translations.exists():
        translations_dir = current_project_translations
        print(f"📁 Utilisation du dossier projet: {translations_dir}")
    elif package_translations.exists():
        translations_dir = package_translations
        print(f"📦 Utilisation du dossier package (fallback): {translations_dir}")
    else:
        print(f"❌ Aucun dossier de traductions trouvé")
        print(f"   Projet: {current_project_translations}")
        print(f"   Package: {package_translations}")
        print("💡 Assurez-vous d'être dans un projet EzQt_App ou lancez 'ezqt init'")
        return

    # Trouver tous les fichiers .ts
    ts_files = list(translations_dir.glob("*.ts"))

    if not ts_files:
        print("❌ Aucun fichier .ts trouvé")
        return

    print(f"📄 Fichiers .ts trouvés: {len(ts_files)}")

    # Convertir chaque fichier .ts
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        if create_proper_qm_from_ts(ts_file, qm_file):
            print(f"✅ {qm_file.name} créé")
        else:
            print(f"❌ Échec de création de {qm_file.name}")

    print("\n🎉 Processus terminé !")
    print("📋 Prochaines étapes:")
    print("   1. Testez les nouveaux fichiers .qm")
    print("   2. Si ça ne fonctionne toujours pas, utilisez les .ts")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import json


DB_FILE = Path(__file__).resolve().parent / "songs_db.json"


class MusicCatalog:
    def __init__(self) -> None:
        self.db = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        if DB_FILE.exists():
            with DB_FILE.open(encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save(self) -> None:
        with DB_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.db, file, indent=4, ensure_ascii=False, sort_keys=True)
            file.write("\n")

    def normalize(self, name: str) -> str:
        return name.strip().upper()

    def get(self, folder_name: str) -> dict[str, str]:
        key = self.normalize(folder_name)
        if key in self.db:
            return self.db[key]
        return self.learn(key)

    def learn(self, key: str) -> dict[str, str]:
        print()
        print("=" * 60)
        print("Nova musica encontrada")
        print("=" * 60)
        print(f"Arquivo : {key}")
        print()

        try:
            title = input(f"Titulo [{key.title()}]: ").strip() or key.title()
            artist = input("Artista: ").strip() or "Unknown"
        except EOFError:
            title = key.title()
            artist = "Unknown"

        self.db[key] = {
            "title": title,
            "artist": artist,
        }
        self.save()

        return self.db[key]

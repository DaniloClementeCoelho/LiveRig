from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "liverig"))

from lyrics import LyricItem, LyricsTimeline
from models import Song
from network.http_server import HttpServer
from playback.playback_state import PlaybackState
from song_manager import SongManager


class SongManagerTest(unittest.TestCase):
    def test_loads_valid_song_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            song_dir = root / "Song A"
            song_dir.mkdir()
            (song_dir / "project.rpp").write_text("<REAPER_PROJECT>\n", encoding="utf-8")
            (song_dir / "lyrics.md").write_text("line one\n", encoding="utf-8")
            (song_dir / "notes.md").write_text("notes\n", encoding="utf-8")
            (song_dir / "config.json").write_text(
                """
                {
                    "title": "Song A",
                    "artist": "Artist",
                    "project": "project.rpp",
                    "lyrics": "lyrics.md",
                    "notes": "notes.md",
                    "bpm": "120",
                    "patch": "32",
                    "tuning": "Eb",
                    "duration": "185",
                    "custom": "value"
                }
                """,
                encoding="utf-8",
            )

            songs = SongManager(root).load_songs()

        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, "Song A")
        self.assertEqual(songs[0].artist, "Artist")
        self.assertEqual(songs[0].bpm, 120)
        self.assertEqual(songs[0].patch, 32)
        self.assertEqual(songs[0].tuning, "Eb")
        self.assertEqual(songs[0].duration, 185)
        self.assertEqual(songs[0].lyrics, "line one\n")
        self.assertEqual(songs[0].notes, "notes\n")
        self.assertEqual(songs[0].extra, {"custom": "value"})

    def test_ignores_package_without_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            song_dir = root / "Broken"
            song_dir.mkdir()
            (song_dir / "config.json").write_text(
                '{"title": "Broken", "project": "missing.rpp"}',
                encoding="utf-8",
            )

            songs = SongManager(root).load_songs()

        self.assertEqual(songs, [])


class PlaybackStateTest(unittest.TestCase):
    def test_version_changes_only_when_values_change(self) -> None:
        state = PlaybackState()

        self.assertFalse(state.set_playing(False))
        self.assertTrue(state.set_playing(True))
        self.assertEqual(state.version, 1)

        self.assertFalse(state.set_position(0.0))
        self.assertTrue(state.set_position(12.5))
        self.assertEqual(state.version, 2)

        self.assertTrue(state.set_current_song("song-a", "Song A"))
        self.assertFalse(state.set_current_song("song-a", "Song A"))
        self.assertEqual(state.version, 3)
        self.assertEqual(
            state.to_dict(),
            {
                "playing": True,
                "current_song": "Song A",
                "current_song_id": "song-a",
                "current_song_title": "Song A",
                "position": 12.5,
                "version": 3,
            },
        )


class LyricsTimelineTest(unittest.TestCase):
    def test_current_returns_latest_started_item(self) -> None:
        timeline = LyricsTimeline(
            [
                LyricItem(index=0, start=1.0, end=2.0, text="first"),
                LyricItem(index=1, start=3.0, end=4.0, text="second"),
            ]
        )

        self.assertIsNone(timeline.current(0.5))
        self.assertEqual(timeline.current(1.5).text, "first")
        self.assertEqual(timeline.current(5.0).text, "second")


class HttpServerTest(unittest.TestCase):
    def test_song_sync_payload_returns_registered_song_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_path = root / "project.rpp"
            project_path.write_text(
                """
                <REAPER_PROJECT
                  <TRACK
                    NAME Lyrics
                    <ITEM
                      POSITION 1
                      LENGTH 2
                      <NOTES
                        |first line
                      >
                    >
                    <ITEM
                      POSITION 3
                      LENGTH 1.5
                      <NOTES
                        |second line
                      >
                    >
                  >
                >
                """,
                encoding="utf-8",
            )
            media_path = root / "Media" / "video.mp4"
            media_path.parent.mkdir()
            media_path.write_bytes(b"video")
            visual_media = media_path.parent
            (visual_media / "foto.jpg").write_bytes(b"image")
            (visual_media / "loop.mp4").write_bytes(b"video")
            song = Song(
                title="Song A",
                artist="Artist",
                folder=root,
                project_path=project_path,
                bpm=120,
                duration=180,
                notes="notes",
                extra={
                    "videos": [
                        {
                            "start": 0,
                            "end": 30,
                            "file": "Media/video.mp4",
                        }
                    ],
                    "visual_cues": [
                        {
                            "start": 30,
                            "end": 45,
                            "type": "message",
                            "text": "CANTA COM A GENTE",
                            "background": "Media/foto.jpg",
                        },
                        {
                            "start": 45,
                            "end": 60,
                            "type": "lyrics",
                        },
                        {
                            "start": 60,
                            "end": 75,
                            "type": "media",
                            "file": "Media/loop.mp4",
                        },
                    ],
                },
            )
            server = HttpServer()

            server.register_song("Song A", song)
            payload = server.song_sync_payload("Song A")

        self.assertIsNotNone(payload)
        self.assertEqual(payload["id"], "Song A")
        self.assertEqual(payload["title"], "Song A")
        self.assertEqual(payload["artist"], "Artist")
        self.assertEqual(payload["bpm"], 120)
        self.assertEqual(payload["duration"], 180)
        self.assertEqual(payload["notes"], "notes")
        self.assertEqual(payload["lyrics"][0]["text"], "first line")
        self.assertEqual(payload["lyrics"][1]["start"], 3.0)
        self.assertEqual(payload["videos"][0]["file"], "Media/video.mp4")
        self.assertEqual(payload["videos"][0]["src"], "/api/songs/Song%20A/media/Media/video.mp4")
        self.assertEqual(payload["visual"]["mode"], "auto")
        self.assertEqual(payload["visual"]["shuffle_interval"], 12)
        self.assertEqual(
            payload["visual"]["media"],
            [
                {
                    "type": "image",
                    "file": "Media/foto.jpg",
                    "src": "/api/songs/Song%20A/media/Media/foto.jpg",
                },
                {
                    "type": "video",
                    "file": "Media/loop.mp4",
                    "src": "/api/songs/Song%20A/media/Media/loop.mp4",
                },
                {
                    "type": "video",
                    "file": "Media/video.mp4",
                    "src": "/api/songs/Song%20A/media/Media/video.mp4",
                },
            ],
        )
        self.assertEqual(payload["visual"]["cues"][0]["type"], "message")
        self.assertEqual(payload["visual"]["cues"][0]["background_media"]["type"], "image")
        self.assertEqual(
            payload["visual"]["cues"][0]["background_media"]["src"],
            "/api/songs/Song%20A/media/Media/foto.jpg",
        )
        self.assertEqual(payload["visual"]["cues"][1]["type"], "lyrics")
        self.assertEqual(payload["visual"]["cues"][2]["type"], "media")
        self.assertEqual(payload["visual"]["cues"][2]["media"]["type"], "video")
        self.assertEqual(
            payload["visual"]["cues"][2]["media"]["src"],
            "/api/songs/Song%20A/media/Media/loop.mp4",
        )

    def test_song_media_path_stays_inside_song_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            media_path = root / "media" / "video.mp4"
            media_path.parent.mkdir()
            media_path.write_bytes(b"video")
            song = Song(
                title="Song A",
                artist="Artist",
                folder=root,
                project_path=root / "project.rpp",
            )
            server = HttpServer()

            server.register_song("song-a", song)

            valid = server.song_media_path("song-a", "media/video.mp4")
            invalid = server.song_media_path("song-a", "../outside.mp4")

        self.assertEqual(valid, media_path)
        self.assertIsNone(invalid)


if __name__ == "__main__":
    unittest.main()

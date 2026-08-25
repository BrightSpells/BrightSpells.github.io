import unittest

from scripts.sync_neodb import merge_entries


class MergeEntriesTest(unittest.TestCase):
    def test_adds_new_updates_changed_and_preserves_missing_records(self) -> None:
        existing = [
            {
                "guid": "neodb:changed",
                "date": "2021-12-16",
                "timestamp": "2021-12-17T00:00:00+00:00",
                "score": 3,
                "cover": "cached.jpg",
            },
            {
                "guid": "neodb:missing-from-response",
                "date": "2022-01-01",
                "timestamp": "2022-01-02T00:00:00+00:00",
                "score": 4,
            },
        ]
        refreshed = [
            {
                "guid": "neodb:changed",
                "date": "2026-05-19",
                "timestamp": "2026-05-20T00:00:00+00:00",
                "score": 5,
                "cover": "",
            },
            {
                "guid": "neodb:new",
                "date": "2026-05-21",
                "timestamp": "2026-05-22T00:00:00+00:00",
                "score": 4,
            },
        ]

        merged = merge_entries(existing, refreshed)
        by_guid = {entry["guid"]: entry for entry in merged}

        self.assertEqual(len(merged), 3)
        self.assertEqual(by_guid["neodb:changed"]["date"], "2026-05-19")
        self.assertEqual(by_guid["neodb:changed"]["score"], 5)
        self.assertEqual(by_guid["neodb:changed"]["cover"], "cached.jpg")
        self.assertIn("neodb:new", by_guid)
        self.assertIn("neodb:missing-from-response", by_guid)


if __name__ == "__main__":
    unittest.main()

import unittest
from github_domain_scraper.extractor import UserProfileBackend


class TestUserProfileExtractor(unittest.TestCase):
    def test_extract(self) -> None:
        backend = UserProfileBackend()
        usernames = ["Parth971"]
        result = backend.process(usernames=usernames)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)
        self.assertIn("Parth971", result)
        self.assertEqual(result["Parth971"].username, "Parth971")
        self.assertEqual(result["Parth971"].fullname, "Parth")
        self.assertEqual(
            result["Parth971"].avatar,
            "https://avatars.githubusercontent.com/u/58165487?v=4",
        )


if __name__ == "__main__":
    unittest.main()

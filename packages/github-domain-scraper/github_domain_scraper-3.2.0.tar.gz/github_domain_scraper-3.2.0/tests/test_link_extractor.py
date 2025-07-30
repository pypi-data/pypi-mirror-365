import unittest
from github_domain_scraper.extractor import LinkExtractor


class TestLinkExtractor(unittest.TestCase):
    def test_extract_links_for_search_result(self) -> None:
        # Define a test GitHub search link
        test_link = "https://github.com/search?q=test+python&type=users"

        # Create an instance of the LinkExtractor class with the test link and a specified link count
        extractor = LinkExtractor(initial_link=test_link, total_links_to_download=5)

        # Extract links using the extract method
        links = extractor.extract()

        # Check if the number of extracted links matches the specified count
        self.assertEqual(
            len(links), 5, "Search results is not having at least 5 results!"
        )

    def test_extract_links_for_user_repository(self) -> None:
        # Define a test GitHub search link
        test_link = "https://github.com/Parth971"

        # Create an instance of the LinkExtractor class with the test link and a specified link count
        extractor = LinkExtractor(initial_link=test_link, total_links_to_download=5)

        # Extract links using the extract method
        links = extractor.extract()

        # Check if the number of extracted links matches the specified count
        self.assertEqual(
            len(links), 5, "User Parth971 does not contains at least 5 repositories!"
        )


if __name__ == "__main__":
    unittest.main()

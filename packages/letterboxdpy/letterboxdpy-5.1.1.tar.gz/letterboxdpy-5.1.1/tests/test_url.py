import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.url import Url


class TestUrl(unittest.TestCase):
    """Test cases for Url class to verify slug functionality."""

    def setUp(self):
        """Set up test fixtures with different URL types."""
        # List URL - should have slug
        self.list_url = "https://letterboxd.com/fastfingertips/list/test-list/"
        self.list_url_instance = Url(self.list_url)
        
        # Watchlist URL - should not have slug
        self.watchlist_url = "https://letterboxd.com/fastfingertips/watchlist/"
        self.watchlist_url_instance = Url(self.watchlist_url)
        
        # User profile URL - should not have slug
        self.profile_url = "https://letterboxd.com/fastfingertips/"
        self.profile_url_instance = Url(self.profile_url)

    def test_list_url_has_slug(self):
        """Test that list URLs correctly extract slug."""
        self.assertIsNotNone(self.list_url_instance.slug)
        self.assertEqual(self.list_url_instance.slug, "test-list")

    def test_watchlist_url_no_slug(self):
        """Test that watchlist URLs do not have slug."""
        self.assertIsNone(self.watchlist_url_instance.slug)

    def test_profile_url_no_slug(self):
        """Test that profile URLs do not have slug."""
        self.assertIsNone(self.profile_url_instance.slug)

    def test_slug_extraction_with_different_list_names(self):
        """Test slug extraction with various list name formats."""
        test_cases = [
            ("https://letterboxd.com/user/list/simple/", "simple"),
            ("https://letterboxd.com/user/list/multi-word-list/", "multi-word-list"),
            ("https://letterboxd.com/user/list/list_with_underscores/", "list_with_underscores"),
            ("https://letterboxd.com/user/list/123-numbers/", "123-numbers"),
        ]
        
        for url, expected_slug in test_cases:
            with self.subTest(url=url):
                url_instance = Url(url)
                self.assertEqual(url_instance.slug, expected_slug)

    def test_slug_functionality_removal(self):
        """Test what happens if we remove the slug functionality."""
        # Create a modified version without slug logic
        class UrlWithoutSlug(Url):
            def __init__(self, url, url_dom=None):
                self.url = url
                self.detail_url = url + 'detail/'
                self.page_url = self.detail_url + 'page/'
                self._url_dom = url_dom
                self._detail_url_dom = None
                # Removed slug logic - always None
                self.slug = None

        # Test the modified version
        modified_instance = UrlWithoutSlug(self.list_url)
        self.assertIsNone(modified_instance.slug)
        
        # This test shows that removing slug functionality would
        # make all URLs have None slug, which might break functionality
        # that depends on slug being available for list URLs

    def test_slug_usage_scenarios(self):
        """Test scenarios where slug might be used."""
        # Test if slug is used for building other URLs
        list_instance = self.list_url_instance
        
        # Check if slug could be useful for:
        # 1. Identifying list type
        self.assertTrue('/list/' in list_instance.url)
        self.assertIsNotNone(list_instance.slug)
        
        # 2. Reconstructing URLs
        if list_instance.slug:
            # This shows slug could be useful for URL reconstruction
            self.assertIn(list_instance.slug, list_instance.url)

    def test_edge_cases(self):
        """Test edge cases for slug extraction."""
        # URL with trailing slash
        url_with_slash = "https://letterboxd.com/user/list/test/"
        instance_with_slash = Url(url_with_slash)
        self.assertEqual(instance_with_slash.slug, "test")
        
        # URL without trailing slash
        url_without_slash = "https://letterboxd.com/user/list/test"
        instance_without_slash = Url(url_without_slash)
        self.assertEqual(instance_without_slash.slug, "test")

    def test_performance_impact(self):
        """Test if slug extraction has significant performance impact."""
        import time
        
        # Test with slug extraction (current implementation)
        start_time = time.time()
        for _ in range(1000):
            Url("https://letterboxd.com/user/list/test/")
        with_slug_time = time.time() - start_time
        
        # Test without slug extraction
        class UrlWithoutSlugExtraction(Url):
            def __init__(self, url, url_dom=None):
                self.url = url
                self.detail_url = url + 'detail/'
                self.page_url = self.detail_url + 'page/'
                self._url_dom = url_dom
                self._detail_url_dom = None
                self.slug = None
        
        start_time = time.time()
        for _ in range(1000):
            UrlWithoutSlugExtraction("https://letterboxd.com/user/list/test/")
        without_slug_time = time.time() - start_time
        
        # Performance difference should be minimal
        performance_difference = with_slug_time - without_slug_time
        print(f"Performance difference: {performance_difference:.6f} seconds")
        
        # If performance difference is significant (>10ms), it might be worth optimizing
        self.assertLess(performance_difference, 0.01, 
                       "Slug extraction has significant performance impact")


if __name__ == '__main__':
    unittest.main()

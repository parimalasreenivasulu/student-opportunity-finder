import unittest
import database

class SampleDataTests(unittest.TestCase):
    def test_sample_listings_have_required_fields(self):
        required = {"title", "category", "organization", "description",
                    "eligibility", "location", "source_url", "status"}
        for listing in database.SAMPLE_LISTINGS:
            self.assertTrue(required.issubset(listing))
            self.assertTrue(listing["title"])
            self.assertTrue(listing["source_url"].startswith("https://"))

if __name__ == "__main__":
    unittest.main()

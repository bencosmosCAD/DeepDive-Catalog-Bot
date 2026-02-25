import json
import re

def parse_gemini_response(text):
    # Simulate the logic in app_v2.py
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text)
        return data
    except Exception as e:
        return str(e)

import unittest

response_1 = """
[
  {
    "brand": "Suunto",
    "model": "D5",
    "sku": "SS050190000",
    "prices": {
        "rrp": 900.00
    }
  }
]
"""

response_2 = """
Here is the data:
```json
[
  {
    "brand": "Oceanic",
    "model": "Vortex V16",
    "prices": {"rrp": 150.00}
  }
]
```
"""

response_3 = """
I found these products:
- Suunto Zoop (RRP $400)
- Oceanic Geo (RRP $500)
"""

class TestParsing(unittest.TestCase):
    def test_perfect_json(self):
        result = parse_gemini_response(response_1)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["brand"], "Suunto")
        
    def test_markdown_wrapped(self):
        result = parse_gemini_response(response_2)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["brand"], "Oceanic")
        
    def test_messy_text(self):
        result = parse_gemini_response(response_3)
        # Should return an error string, not a list
        self.assertIsInstance(result, str)
        self.assertTrue("Expecting value" in result)

if __name__ == '__main__':
    unittest.main()

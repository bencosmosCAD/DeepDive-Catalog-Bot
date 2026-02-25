import json
text = """[
  {"brand": "Suunto"}
]
Trailing text"""

start = text.find('[')
end = text.rfind(']')
if start != -1 and end != -1:
    text = text[start:end+1]
    
data = json.loads(text)
print(data)

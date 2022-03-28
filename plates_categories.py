import csv

categories = [
  ('shipper_name1', ['ab123cd', 'ab456cd', 'ab789cd', 'ab321cd']),
  ('shipper_name2', ['ba123cd', 'ba456cd']),
  ('shipper_name3', ['aa123cd']),
  ('shipper_name4', ['bb123cd']),
  ('shipper_name5', ['cc123cd', 'cc456cd', 'cc789cd', 'cc321cd', 'cc123ef',\
   'cc456cd', 'cc789cd', 'cc123gh', 'cc456gh'])
]

def classify(text):
  for category, matches in categories:
    if any(match in text for match in matches):
      return category
  return None

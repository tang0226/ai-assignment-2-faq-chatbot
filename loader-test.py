from langchain_community.document_loaders import WebBaseLoader
import bs4
import re

import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def clean_whitespace(text):
  text = re.sub(r'\n{3,}', '\n\n', text)
  text = re.sub(r'[ \t]{2,}', ' ', text)
  return text.strip()

apple_strainer = bs4.SoupStrainer(id='main')
google_strainer = bs4.SoupStrainer('main')
samsung_strainer = bs4.SoupStrainer(id='content')
url_config = [
  # Samsung
  # Galaxy S25|S25+
  {
    'url': 'https://www.samsung.com/ca/smartphones/galaxy-s25/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 Edge
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-edge/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 Ultra
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-ultra/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 FE
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-fe/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Flip7 FE
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-flip7-fe/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Flip7
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-flip7/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Fold7
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-fold7/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z TriFold
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-trifold/',
    'strainer': samsung_strainer,
  },
  
  # Apple
  # iPhone 17
  {
    'url': 'https://www.apple.com/iphone-17/',
    'strainer': apple_strainer
  },
  # iPhone 17 Pro
  {
    'url': 'https://www.apple.com/iphone-17-pro/',
    'strainer': apple_strainer
  },
  # iPhone Air
  {
    'url': 'https://www.apple.com/iphone-air/',
    'strainer': apple_strainer
  },
  # iPhone 16e
  {
    'url': 'https://www.apple.com/iphone-16e/',
    'strainer': apple_strainer
  },

  # Google
  # Google Pixel 10
  {
    'url': 'https://store.google.com/product/pixel_10?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 specs
  {
    'url': 'https://store.google.com/product/pixel_10_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 tech specs:\n'
  },
  # Google Pixel 10 Pro
  {
    'url': 'https://store.google.com/product/pixel_10_pro?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 Pro specs
  {
    'url': 'https://store.google.com/product/pixel_10_pro_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 Pro tech specs:\n'
  },
  # Google Pixel 10 Pro Fold
  {
    'url': 'https://store.google.com/product/pixel_10_pro_fold?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 Pro Fold specs
  {
    'url': 'https://store.google.com/product/pixel_10_pro_fold_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 Pro Fold tech specs:\n'
  },
  # Google Pixel 10a
  {
    'url': 'https://store.google.com/product/pixel_10a?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10a specs
  {
    'url': 'https://store.google.com/product/pixel_10a_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10a tech specs:\n'
  },
]

docs = []
for config in url_config:
  loader = WebBaseLoader(
    web_paths=(config['url'],),
    bs_kwargs={'parse_only': config['strainer']},
    # bypass SSL verification errors during fetching
    requests_kwargs={'verify': False}
  )
  doc = loader.load()[0]
  if 'context' in config:
    doc.page_content = config['context'] + doc.page_content
  docs.append(doc)

for d in docs:
  print(len(d.page_content))
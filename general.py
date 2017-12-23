import io
import os
import sys

from google.cloud import vision
from google.cloud.vision import types

import requests
import json
base_api_path = "https://api.cognitive.microsoft.com/bing/v7.0/search"
cog_key = "8d2c22839407465db555e76f25b9ee1b"

import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
#setFormatter(logging.Formatter("%(asctime)s | %(message)s"))

client = vision.ImageAnnotatorClient()

file_name = os.path.join(os.path.dirname(__file__),sys.argv[1]);

logger.info("File Open -> %s" % file_name)

with open(file_name, 'rb') as image_file:
	content = image_file.read()

image = types.Image(content = content)

response = client.annotate_image({'image':image,})
#labels = response.annotations

#logger.info("Data:");
#logger.info(response)

#logger.info("Labels:");

#for label in response.label_annotations:
#	logger.info("%5.3lf -> %s" % (label.score,label.description))

logger.info("TEXT:")
logger.info(response.full_text_annotation.text)


question = response.full_text_annotation.text.split("?")[0].replace("\n","")
logger.info("Question: %s" % question)

answers = response.full_text_annotation.text.split("?")[1].split("\n")

answers = [x for x in answers if not x.isdigit()]

for i in range(1,4):
	logger.info("Answer #%d: %s" % (i,answers[i]))

answers = answers[1:-1]

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko','Ocp-Apim-Subscription-Key':cog_key,'Accept-Language':'en-US'}
logger.info("Query Sending: %s" % base_api_path+"?q=%s?cc=us?count=30" % question.replace(" ","+"))
result = requests.get(base_api_path+"?q=%s?cc=us?count=50?responseFilter=Webpages" % question.replace(" ","+"),headers = headers)

counts = [0,0,0]
try:
	for entry in result.json()["webPages"]["value"]:
		logger.info(entry['name'])
		i=0;
		for ans in answers:
			i=i+1
			count = 0;
			for word in ans.split(" "):
				count += entry['name'].count(word);
				count += entry['snippet'].count(word);
			logger.info("#%d: %s -> %d" % (i,ans,count))
			counts[i-1]+=count
except:
	print "ERROR\n" + result.text

best = answers[counts.index(max(counts))]
logger.info("Most Probable Answer: %s" % (best))


# search_service = PyMsCognitiveWebSearch('8d2c22839407465db555e76f25b9ee1b',question)
# first_fifty_results = search_service.search(limit=50,format='json')

# logger.info first_fifty_results
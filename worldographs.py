import urllib.request
from bs4 import BeautifulSoup
import re
import json
req = urllib.request.urlopen('https://www.worldometers.info/coronavirus/country/us')
page = BeautifulSoup(req.read().decode('utf8'), 'html.parser')

countries = []
# print(page.find('div', class_ = 'graph_row').script.text)
# jsonl = json.loads(
# print(page.find_all(re.compile("\[(.*?)\]")))
print(page.find('div', class_ = 'graph_row').script.text.replace("Highcharts.chart('coronavirus-cases-linear',", "").split("Highcharts.chart('coronavirus-cases-log',")[0].rstrip('\n').replace(");",""))
jsonl = json.dumps(page.find('div', class_ = 'graph_row').script.text.replace("Highcharts.chart('coronavirus-cases-linear',", "").split("Highcharts.chart('coronavirus-cases-log',")[0].rstrip('\n').replace(");","").replace("\'", "\""))
print(jsonl)

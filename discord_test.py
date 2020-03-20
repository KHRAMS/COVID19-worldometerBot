import discord
import os

TOKEN = os.environ.get('DISCTOKEN')

client = discord.Client()
import pandas as pd
import requests as r
from bs4 import BeautifulSoup
import urllib.request
import re
import datetime

req = urllib.request.urlopen('https://www.worldometers.info/coronavirus')
page = BeautifulSoup(req.read().decode('utf8'), 'html.parser')
country_name = ""
states = []
df_state_dict = {}
count = 0
countries = []
for i in page.table.thead.find_all('tr'):
    data = [j.text.lstrip().rstrip() for j in i.find_all('th')]

    countries.append(data)

for i in page.table.tbody.find_all('tr'):
    row = i.find_all('td')

    data = []

    data.append(row[0].text.lstrip().rstrip())

    for j in row[1:-1]:
        if not j.text.strip():
            data.append(None)
        else:
            data.append(int(re.sub('[\s+,]', '', j.text)))

    if not row[-1].text:
        data.append(None)
    else:
        data.append(float(re.sub('[\s+,]', '', row[-1].text)))

    country_name = data[0]
    countries.append(data)

    if(i.a != None):
      req = urllib.request.urlopen("https://www.worldometers.info/coronavirus/" + i.a.get('href'))
     # soup_det =  BeautifulSoup(y.text, 'html.parser')


      page = BeautifulSoup(req.read().decode('utf8'), 'html.parser')

      if page.table is not None:
        for i in page.table.thead.find_all('tr'):
            data = [j.text.lstrip().rstrip() for j in i.find_all('th')]
            states.append(data)

        for i in page.table.tbody.find_all('tr'):
            state = i.find_all('td')[0].text.lstrip().rstrip()
            data = []
            for j in i.find_all('td')[1:]:
                if not j.text.strip():
                    data.append(None)
                else:
                    data.append(re.sub('[^0123456789]', '', j.text))
                    #                  '[^0123456789]' to remove non-digits
                    #                  '[\s+,]' to remove whitespace, plus, comma
                    #                  '[\s+]' to remove whitespace, plus

            states.append([state] + data)

        df_state = pd.DataFrame(states)
        new_header = df_state.iloc[0] #grab the first row for the header
        df_state = df_state[1:] #take the data less the header row
        df_state.columns = new_header #set the header row as the df header
        df_state.set_index(df_state.columns[0],inplace=True)
        df_state.reset_index(inplace=True)
       # print(df_state)
        df_state_dict[country_name.lower()] = df_state


df_countr = pd.DataFrame(countries)
new_header = df_countr.iloc[0]
df_countr = df_countr[1:]
df_countr.columns = new_header
df_countr.set_index(df_countr.columns[0], inplace=True)
# This would also work, but keeps it as series
  # total_countr = df_countr.sum(0).to_frame()
  # total_countr.iat[0,0] = 'World'
  # print(total_countr)
  # total_countr.at["Country,Other", 0] = "World"
  # print(total_countr)
temp = df_countr.sum(0).tolist()
temp[len(temp)-1] = None
df_countr.loc["World"]  = temp
df_countr.reset_index(inplace=True)
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))
abbrev_us_state ={key.lower() if type(key) == str else key: value for key, value in abbrev_us_state.items()}


# Use this if necessary -->
# df_countr.index = [x.lower() for x in df_countr.index.tolist()]

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('$c'):
        # cmd = ['!c', 'stat', 'usa']
        cmd=message.content.split(" ")
        print(cmd)
        embed = None
        msg = "That's not an available command!"
        to_send = ""
        if(cmd[1].lower() == 'stat'):

            if(len(cmd) ==3):
                temp = df_countr[pd.Series(df_countr['Country,Other']).str.match(cmd[2], case=False).values]
                embed = discord.Embed(title = 'CoVID19 data for ' + temp['Country,Other'].item(),
                                        colour =discord.Colour.blue())
                embed.set_footer(text="This data was taken from https://www.worldometers.info/coronavirus. Numbers in the (+...) show new cases in that category. Nones aren't necessarily 0s! There just might not be data for a category.")
                print(temp)
                # embed.set_author(name= 'CoVID19-Analytics')
                embed.add_field(name = 'Total Cases', value= str(temp['TotalCases'].item())+ "(+"+ str(temp['NewCases'].item()) + ")")
                embed.add_field(name = 'Total Deaths', value= str(temp['TotalDeaths'].item())+ "(+"+ str(temp['NewDeaths'].item()) + ")")
                embed.add_field(name = 'Total Recovered', value= str(temp['TotalRecovered'].item()))
                embed.add_field(name = 'Active Cases', value= str(temp['ActiveCases'].item()))
                embed.add_field(name = 'Critical Cases', value= str(temp['Serious,Critical'].item()))
                embed.add_field(name = 'Total Cases per million', value= str(temp['Tot Cases/1M pop'].item()))
                embed.add_field(name = 'Closed Cases', value= str(temp['TotalCases'].item() - temp['ActiveCases'].item()))
                embed.add_field(name = 'Death/Closed Case%', value= "{0:.2f}".format((temp['TotalDeaths'].item()/(temp['TotalCases'].item() - temp['ActiveCases'].item()))*100)+ "%")
                embed.add_field(name = 'Recovered/Closed Case%', value= "{0:.2f}".format(((temp['TotalRecovered'].item()/(temp['TotalCases'].item() - temp['ActiveCases'].item()))*100)) + "%")
                # to_send+= "There are " + str(temp['NewCases'].item()) + " new cases in " + temp['Country,Other'].item()
                msg =  ""
                await message.channel.send(msg, embed = embed)
                response = r.get("https://api.newsriver.io/v2/search?query=text%3A%22coronavirus%20" + temp['Country,Other'].item() + "%22&sortBy=discoverDate&sortOrder=DESC&limit=2", headers={"Authorization":"sBBqsGXiYgF0Db5OV5tAw3BRlHPKxnhbzMtWmJE8q2KoXUsZ0bCbO-rG-wzTnwsnn2pHZrSf1gT2PUujH1YaQA"})
                # print(response.text)
                jsonFile = response.json()
                # print(jsonFile[0])
                # print(jsonFile)
                for i in jsonFile:
                    print(i['url'])
                    # print(i[])mport datetime


                    tempbed=discord.Embed(timestamp= datetime.datetime.strptime(i['publishDate'], "%Y-%m-%dT%H:%M:%S"), title="Breaking News", description= "["+i['title']+"]("+i['url']+")", url= i['url'], author=i['website']['name'], colour =discord.Colour.blue())
                    # tempbed.set_footer(text=i['highlight'])

                    await message.channel.send(msg, embed =tempbed )
                # await message.channel.send(msg, embed = embed)
                # await message.channel.send(msg, embed = embed)
                # await message.channel.send(msg, embed = embed)

            elif(len(cmd) == 4):
                df_st = df_state_dict.get(cmd[2].lower())
                state_string = abbrev_us_state.get(cmd[3].lower())
                print(df_st)
                print(state_string)
                print(df_st.iloc[:,0])
                temp = df_st.loc[df_st.iloc[:,0] == state_string]

                print(temp)
                embed = discord.Embed(title = 'CoVID19 data for ' + state_string,
                                        colour =discord.Colour.blue())
                embed.set_footer(text="This data was taken from https://www.worldometers.info/coronavirus. Numbers in the (+...) show new cases in that category. Nones aren't necessarily 0s! There just might not be data for a category.")
                print(temp)
                # embed.set_author(name= 'CoVID19-Analytics')
                embed.add_field(name = 'Total Cases', value= str(temp['TotalCases'].item())+ "(+"+ str(temp['NewCases'].item()) + ")")
                embed.add_field(name = 'Total Deaths', value= str(temp['TotalDeaths'].item())+ "(+"+ str(temp['NewDeaths'].item()) + ")")
                embed.add_field(name = 'Total Recovered', value= str(temp['TotalRecovered'].item()))
                embed.add_field(name = 'Active Cases', value= str(temp['ActiveCases'].item()))
                msg =  ""
                await message.channel.send(msg, embed = embed)

            else:
                embed=None
                await message.channel.send(msg, embed = embed)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)

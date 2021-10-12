import json
from datetime import  datetime
# print(pytz.all_timezones)
import pytz

# print(datetime.time("2021-10-19 23:59:59", pytz.timezone('Asia/Kolkata')))
# a = (datetime.strptime("2021-10-19 23:59:59", "%Y-%m-%d %H:%M:%S"))


# b = pytz.timezone('Asia/Kolkata').localize(a)
# print(b)

import requests

url = 'https://codexweb.netlify.app/.netlify/functions/enforceCode'
myobj = {
           "code":"public class program{public static void main(String [] args){System.out.println(5+5+6);}}",
           "language":"java",
           "input":""
           }

x = requests.post(url, data = json.dumps(myobj), headers={
    'Content-Type': 'application/json'
  })

print(x.text)
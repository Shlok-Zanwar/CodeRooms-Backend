# import json
# from datetime import  datetime
# # print(pytz.all_timezones)
# import pytz
#
# # print(datetime.time("2021-10-19 23:59:59", pytz.timezone('Asia/Kolkata')))
# # a = (datetime.strptime("2021-10-19 23:59:59", "%Y-%m-%d %H:%M:%S"))
#
#
# # b = pytz.timezone('Asia/Kolkata').localize(a)
# # print(b)
#
#
# url = 'https://codexweb.netlify.app/.netlify/functions/enforceCode'
# myobj = {
#            "code":"public class program{public static void main(String [] args){System.out.println(5+5+6);}}",
#            "language":"java",
#            "input":""
#            }
#
# x = requests.post(url, data = json.dumps(myobj), headers={
#     'Content-Type': 'application/json'
#   })
#
# print(x.text)

# a = 123
# def funccc():
#     print("here")
#     return True
#
# if a == 123 or funccc():
#     print("yesssss")
# import os
import json
#
# print(json.dumps({}))
#
# print(os.getcwd())
# C:\Users\princ\Documents\GitHub\CodeRooms-Backend


import requests
from concurrent.futures import ThreadPoolExecutor


urls = ["https://api.smart-iam.com/api/coderooms/auth/change_username"]*500
count = 0
def doSomething(url):
    global count

    count += 1
    # payload = {"questionId": "21",
    #            "code": "#include <iostream>\r\nusing namespace std;\r\n\r\nint main()\r\n{\r\n    int firstNumber, secondNumber, sumOfTwoNumbers;\r\n    \r\n    cin >> firstNumber >> secondNumber;\r\n\r\n    // sum of two numbers in stored in variable sumOfTwoNumbers\r\n    sumOfTwoNumbers = firstNumber + secondNumber;\r\n\r\n    cout << sumOfTwoNumbers;     \r\n\r\n    return 0;\r\n}",
    #            "language": "cpp"}
    payload = {"userName": f"Parag_{str(1)}"}
    print(payload)

    x = requests.post(url, data=json.dumps(payload), headers={
        'Content-Type': 'application/json',
        'Authorization': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyTmFtZSI6IlBhcmFnXzEiLCJ1c2VySWQiOjUsImZpcnN0TmFtZSI6IlBhcmFnIiwibGFzdE5hbWUiOiJKYWRoYXYiLCJlbWFpbCI6InBhcmFnMjgwNEBnbWFpbC5jb20iLCJhY2NvdW50VHlwZSI6bnVsbCwiZXhwIjoxNjM3NDU1ODY0fQ.cEPd5PlaJW8XQgQsvPuPl93qhbIWxXPG7N-O523aqc4"
    })
    return (json.loads(x.text)["token_type"])

# for i in range(100):
#     doSomething()

with ThreadPoolExecutor(max_workers=100) as pool:
    response_list = list(pool.map(doSomething, urls))
    print(response_list)
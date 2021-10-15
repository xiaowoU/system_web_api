'''==================================================
@IDE: PyCharm
@Time : 2021/10/12 14:37
@Author : wyp
@File : common.py
=================================================='''
import requests
import json
import time
from flask import make_response, jsonify


# 封装一个response函数，“*”代表响应头里允许全部域名访问
def make_new_response(data):
    res = make_response(jsonify(data))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Method'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res

# 地理坐标
def get_geo(address):
    '''
    {
	"status": "1",
	"info": "OK",
	"infocode": "10000",
	"count": "1",
	"geocodes": [{
		"formatted_address": "四川省成都市温江区",
		"country": "中国",
		"province": "四川省",
		"citycode": "028",
		"city": "成都市",
		"district": "温江区",
		"township": [],
		"neighborhood": {
			"name": [],
			"type": []
		},
		"building": {
			"name": [],
			"type": []
		},
		"adcode": "510115",
		"street": [],
		"number": [],
		"location": "103.837104,30.690460",
		"level": "区县"
	}]
}
    '''
    url = 'https://restapi.amap.com/v3/geocode/geo?key=864c853f3ad0f0a878d7ad7670a8019c&address=%s' % address
    res = requests.get(url)
    try:
        while True:
            if(200 == res.status_code):
                # bytes
                content = json.loads(res.content)
                # print(content)
                geocodes = content.get("geocodes", None)
                if geocodes:
                    location = geocodes[0]["location"]
                    location = location.split(',')
                    # ['103.837104', '30.690460']
                    return location
            else:
                print("Try geturl again")
                time.sleep(2)
    except:
        print("Exception!")


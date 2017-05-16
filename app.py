#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from SharePrice import SharePrice

import json
import os
import ystockquote

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res
    elif req.get("result").get("action") == "sharePriceAction":
        result = req.get("result")
        parameters = result.get("parameters")
        speech = "This is a current price: " + ystockquote.get_today_open(parameters.get("enterprise-name"))

        return {
            "speech": speech,
            "displayText": speech,
            # "data": data,
            # "contextOut": [],
            "source": "ai-project"
        }
    elif req.get("result").get("action") == "getEbitdaAction":
        result = req.get("result")
        parameters = result.get("parameters")
        speech = "This is a ebitda of enterprise: " + ystockquote.get_ebitda(parameters.get("enterprise-name"))
        return {
            "speech": speech,
            "displayText": speech,
            # "data": data,
            # "contextOut": [],
            "source": "ai-project"
        }
    elif req.get("result").get("action") == "getMarketCapAction":
        result = req.get("result")
        parameters = result.get("parameters")
        speech = "This is a market capitalization of enterprise: " + ystockquote.get_market_cap(parameters.get("enterprise-name"))
        return {
            "speech": speech,
            "displayText": speech,
            # "data": data,
            # "contextOut": [],
            "source": "ai-project"
        }
    elif req.get("result").get("action") == "compareEnterprisesAction":
        result = req.get("result")
        parameters = result.get("parameters")
        enterprise1 = parameters.get("enterprise-name1")
        enterprise2 = parameters.get("enterprise-name2")
        speech = enterprise1 + " market capitalization: " + ystockquote.get_market_cap(enterprise1)
        + " ebitda: " + ystockquote.get_ebitda(parameters.get(enterprise1)) + " volume: " + ystockquote.get_volume(enterprise1)
        + " " + enterprise2 + " market capitalization: " + ystockquote.get_market_cap(enterprise2)
        + " ebitda: " + ystockquote.get_ebitda(parameters.get(enterprise2)) + " volume: " + ystockquote.get_volume(enterprise2)
        return {
            "speech": speech,
            "displayText": speech,
            # "data": data,
            # "contextOut": [],
            "source": "ai-project"
        }
    else:
        return {}


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))
    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "ai-project"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
#1 define intents fror share:
#current price
#open
#close
#interval
#some growth
#ebitda
#cap_value
#2 define currency
#get exchange rate: ask, bid
#calculate how much money can you get for value in another currency
#
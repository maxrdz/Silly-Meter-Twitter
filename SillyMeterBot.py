import requests
import json
import tweepy
from pytz import timezone
import time

global jsonFile

# Parse JSON Save File
try:
	print("Opening json...")
	with open("settings.json", "r") as save:
		fullJson = ""
		for line in save:
			fullJson = fullJson + line
		try:
			jsonFile = json.loads(fullJson)
		except:
			print("Could not parse json.")
except:
	print("Could not open json.")

pacific = timezone('America/Los_Angeles')
apiURL = jsonFile["SillyMeterAPI"]

maxedImg = "maxed.jpg"
usualImg = "silly_meter.jpg"

sendHeaders = {
	"User-Agent": jsonFile['Headers']['User-Agent'],
	"From": jsonFile['Headers']['From'],
	"Accept-Language": jsonFile['Headers']['Accept-Language'],
	"Server": jsonFile['Headers']['Server']
}


# Twitter API Authentication
consumer_key = jsonFile["AppKeys"]["consumer_key"]
consumer_secret = jsonFile["AppKeys"]["consumer_secret"]
access_token = jsonFile["AppKeys"]["access_token"]
access_secret = jsonFile["AppKeys"]["access_secret"]

authentication = tweepy.OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_secret)

api = tweepy.API(authentication, wait_on_rate_limit=True)


def get_silly_points():
	def get_response():
		try:
			request = requests.get(url=apiURL, params=None, headers=sendHeaders)
		except Exception:
			time.sleep(30)
			request = get_response()
			# Recurse infinitely with intervals of 30 seconds until it gets a response.
		finally:
			return request
	response = get_response()
	received = response.json()
	return received


def send_tweet(text, img):
	api.update_with_media(img, text)


class Main:
	def __init__(self):
		while True:
			meter_status = get_silly_points()
			self.particles = meter_status["hp"]
			self.rewards = [meter_status["rewards"][1], meter_status["rewards"][2], meter_status["rewards"][3]]
			self.winner = str(meter_status["winner"])
			self.state = meter_status["state"]
			if self.state == "Reward":
				message = f"Gadzooks! The silly meter had maxed!! All of Toontown now has the active reward, {self.winner}!"
				send_tweet(message, maxedImg)
			if self.state == "Inactive":
				message = f"The silly meter is currently cooling down."
				send_tweet(message, usualImg)
			time.sleep(meter_status["nextUpdateTimestamp"] - meter_status["asOf"])


Main()

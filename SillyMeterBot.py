import requests
import json
import tweepy
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

apiURL = jsonFile["SillyMeterAPI"]

maxedImg = "maxed.jpg"
usualImg = "silly_meter.jpg"
inactiveImg = "inactive.jpg"
rewardImg = "reward_in_progress.jpg"

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


def authenticate():
	for retry in range(10):
		try:
			authentication = tweepy.OAuthHandler(consumer_key, consumer_secret)
			authentication.set_access_token(access_token, access_secret)
			twitter_api = tweepy.API(authentication, wait_on_rate_limit=True)
			print("Successfully Authenticated to Twitter API!")
			return twitter_api
		except Exception:
			time.sleep(10)
	return False


api = authenticate()

if not api:
	print("Could not authenticate to Twitter API, returning Exit code 1.")
	exit(1)
	# Exit code 1: Error


def get_silly_points():
	for retry in range(10):
		try:
			request = requests.get(url=apiURL, params=None, headers=sendHeaders)
			print("Successfully got data from API, www.toontownrewritten.com/api/sillymeter.")
			break
		except Exception:
			time.sleep(30)
			# Intervals of 30 seconds until it gets a response.

	received = request.json()
	return received


def send_tweet(text, img):
	try:
		api.update_with_media(img, text)
		print("Successfully sent tweet!")
		time.sleep(10)
		# ^^ Just in case, Preventing spam.
	except Exception:
		time.sleep(10)
		send_tweet(text, img)


def convert_to_hours(value):
	return round((value / 60) / 60, 1)


class Main:
	def __init__(self):
		checked_max = False
		checked_reward_end = False
		checked_active = False
		checked_points = 1
		checked_inactive = False
		checked_inactive_end = False

		while True:
			meter_status = get_silly_points()

			self.particles = meter_status["hp"]
			self.rewards = [meter_status["rewards"]]
			self.winner = str(meter_status["winner"])
			self.state = meter_status["state"]
			self.nextUpdate = int(meter_status["nextUpdateTimestamp"]) - int(meter_status["asOf"])

			# Check for new updates in data, if so then tweet.
			if self.state == "Reward":
				if not checked_max:
					checked_active = False
					message = f"Gadzooks! The silly meter had maxed!! All of Toontown now has the active reward, {self.winner}!"
					message = message + f" The reward will last {convert_to_hours(self.nextUpdate)} hours!"
					send_tweet(message, maxedImg)
					checked_max = True

				elif convert_to_hours(self.nextUpdate) <= 2 and (not checked_reward_end):
					message = "The silly meter reward is ending in less than 2 hours!"
					message = message + " Reap the last bit of the reward in Toontown before it ends!"
					send_tweet(message, rewardImg)
					checked_reward_end = True

			elif self.state == "Inactive":
				if not checked_inactive:
					checked_max = False
					checked_reward_end = False
					message = f"The silly meter is currently cooling down! "
					message = message + f"The meter will return to functional in {convert_to_hours(self.nextUpdate)} hours!"
					send_tweet(message, inactiveImg)
					checked_inactive = True

				elif convert_to_hours(self.nextUpdate) <= 2 and (not checked_inactive_end):
					message = f"The silly meter is about to return to its operations in {convert_to_hours(self.nextUpdate)}"
					message = message + " hours! Get ready to defeat some cogs and collect silly points!"
					send_tweet(message, inactiveImg)
					checked_inactive_end = True

			elif self.state == "Active":
				if not checked_active:
					checked_inactive = False
					checked_inactive_end = False
					message = f"The silly meter is back to operational!! Get in Toontown and defeat some cogs!"
					send_tweet(message, usualImg)
					checked_active = True

				elif self.particles >= 1600000 and checked_points == 1:
					checked_points += 1
					message = f"The silly meter has reached {self.particles} particles!!"
					message = message + " The meter is now one third full until it reaches maximum silly particles!"
					send_tweet(message, usualImg)

				elif self.particles >= 2500000 and checked_points == 2:
					checked_points += 1
					message = f"The silly meter has reached {self.particles} particles!!"
					message = message + " The meter is now half way full until it reaches maximum silly particles!"
					send_tweet(message, usualImg)

				elif self.particles >= 4500000 and checked_points == 3:
					checked_points = 1
					message = f"The silly meter has reached {self.particles} particles!!"
					message = message + " The silly meter is about to reach maximum silly particles!!"
					send_tweet(message, usualImg)

			print(f"Requesting API again in {convert_to_hours(self.nextUpdate) * 60} minutes.")
			time.sleep(self.nextUpdate + 5)
			# Gives API 5 secs to update when (updateTime - asOf) = 0 secs.


Main()

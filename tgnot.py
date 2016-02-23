#!/usr/bin/env python3

import argparse
import os.path
import sys

import telegram

CONFIG_FILE = '~/.tgnot.conf'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--token', nargs=1, help="bot auth token")
	parser.add_argument('-s', '--setup', action='store_true', help="enter setup mode")
	parser.add_argument('message', nargs='*')
	args = parser.parse_args()

	configFile = os.path.expanduser(CONFIG_FILE)
	config = loadConfig(configFile)

	if args.token is not None:
		config['token'] = args.token[0]
		saveConfig(configFile, config)

	if args.setup:
		configCheckToken(parser.prog, config)
		print("Entering setup mode. Please find me on Telegram and message \"/start\"")
		config = botSetup(config)
		saveConfig(configFile, config)
	else:
		configCheckToken(parser.prog, config)
		configCheckChatId(parser.prog, config)
		if len(args.message) == 0:
			messageString = sys.stdin.read()
		else:
			messageString = ' '.join(args.message)
		botMessage(config, messageString)

def loadConfig(filename):
	config = {}
	try:
		with open(filename, 'r') as cf:
			for line in cf.readlines():
				key, val = line.split('=', 1)
				config[key.strip()] = val.strip()
	except FileNotFoundError:
		pass

	return config

def saveConfig(filename, config):
	print("Saving config file " + filename)
	with open(filename, 'w') as cf:
		for k in config:
			cf.write('%s = %s\n' % (str(k), str(config[k])))

def configCheckToken(prog, config):
	if 'token' not in config:
		print("Bot auth token not set. Please run %s -t" % (prog,))
		sys.exit(3)

def configCheckChatId(prog, config):
	if 'chatId' not in config:
		print("Chat ID not set. Please run %s -s" % (prog,))
		sys.exit(4)

def botMessage(config, msg):
	telegram.makeRequest(config['token'], 'sendMessage', { 'chat_id': config['chatId'], 'text': msg })

def botSetup(config):
	while True:
		update = telegram.getOneUpdate(config['token'])

		if 'message' in update:
			message = update['message']
			if 'chat' in message and message['text'] == '/start':
				chatId = message['chat']['id']
				message = "Hey there. Our chat id is %i. I'm saving this." % (chatId,)
				telegram.makeRequest(config['token'], 'sendMessage', { 'chat_id': chatId, 'text': message })
				config['chatId'] = chatId
				return config

if __name__ == '__main__':
	main()

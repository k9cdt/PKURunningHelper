#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: runner.py

import json
from optparse import OptionParser
from util.utilclass import Config

config = Config()


parser = OptionParser(usage="PKU running helper ! Check your config first, then enjoy yourself !")
parser.add_option("-c", "--check", help="show 'config.ini' file", action="store_false")
parser.add_option("-s", "--start", help="run the runner's client", action="store_false")

options, args = parser.parse_args()


if options.check is not None:

	for section in config.sections():
		print("Section [%s]" % section)
		print(json.dumps(dict(config[section]), indent=4))
		print("\n")


elif options.start is not None:

	software = config.get('Base', 'software')

	if software == 'PB':

		from PB.client import PBclient
		client = PBclient()
		client.run()

	else:
		raise ValueError("unregistered running software -- %s !" % software)


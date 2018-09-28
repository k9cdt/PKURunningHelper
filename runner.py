#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: runner.py

from optparse import OptionParser
from util import (
        Config, Logger,
        json,
    )

config = Config()
logger = Logger("runner")


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

    app = config.get('Base', 'APP')

    if app == 'PB':
        from PB import PBClient as Client
    elif app == "PKURunner":
        from PKURunner import PKURunnerClient as Client
    else:
        raise ValueError("unsupported running APP -- %s !" % app)

    try:
        client = Client()
        client.run()
    except Exception as err:
        logger.error("upload record failed !")
        raise err
    else:
        logger.info("upload record success !")


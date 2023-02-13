import json


def reformat_config(config):
    return {
        "server": config['server'],
        "listener": config['listener'],
        "nimplant": {
            "useragent": config['nimplant']['userAgent'],
            "sleep": config['nimplant']['sleepTimeSeconds'],
            "jitter": config['nimplant']['sleepJitterPercent'],
            "killAfter": config['nimplant']['killTimeHours'],
        }
    }
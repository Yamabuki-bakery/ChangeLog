#!/usr/bin/python3
import requests, json, datetime, pytz

RECENT_URL = 'https://bestdori.com/api/news/dynamic/recent.json'
BIRTHDAY_URL = 'https://bestdori.com/api/characters/main.birthday.json'
EVENT_URL = 'https://bestdori.com/api/events/'  # number.json
CARD_URL = "https://bestdori.com/api/cards/all.5.json"
get_name = ["戸山香澄", "花園たえ", "牛込りみ", "山吹沙綾", "市ヶ谷有咲",
            "美竹蘭", "青葉もか", "上原ひまり", "宇田川巴", "羽沢つぐみ",
            "弦卷こころ", "濑田薰", "北沢はぐみ", "松原花音", "奥沢美咲",
            "丸山彩", "氷川日菜", "白鷺千聖", "大和麻弥", "若宮イヴ",
            "湊友希那", "氷川紗夜", "今井リサ", "宇田川あこ", "白金燐子",
            "倉田ましろ", "桐ケ谷透子", "広町七深", "二葉つくし", "八潮瑠唯",
            "和奏レイ", "朝日六花", "佐藤ますき", "鳰原令王那", "珠手ちゆ"]

jptz = pytz.timezone('Asia/Tokyo')


def start():
    session = requests.session()
    recents = session.get(RECENT_URL, timeout=15).json()

    latest_event_id = sorted(recents['events'].keys())[-1]
    latest_event = session.get(EVENT_URL + str(latest_event_id) + '.json', timeout=15).json()
    card_dict = session.get(CARD_URL, timeout=15).json()

    event_dict = {}
    event_dict.update(
        {
            'name': latest_event['eventName'][0],
            'start_time': int(latest_event['startAt'][0])/1000,
            'end_time': int(latest_event['endAt'][0])/1000,
            'reward_cards': latest_event['rewardCards'],
            'story0_synopsis': latest_event['stories'][0]['synopsis'][0]
        }
    )
    result = '【Latest Event】\n'
    result += event_dict['name'] + '\n'

    now = datetime.datetime.now(tz=jptz)
    start_time = datetime.datetime.fromtimestamp(event_dict['start_time'], tz=jptz)
    end_time = datetime.datetime.fromtimestamp(event_dict['end_time'], tz=jptz)

    if now < start_time:
        result += 'Event coming soon, starts at ' + start_time.strftime("%H:%M %a %d. %b %Y, %Z") + '\n'
    elif now > end_time:
        result += 'Event is over.\n'
    else:
        result += 'Ongoing, ends at ' + end_time.strftime("%H:%M %a %d. %b %Y, %Z") + '\n'

    result += '\n【Story】\n' + event_dict['story0_synopsis'] + '\n'
    result += '\n【Reward Cards】\n'

    for id_ in event_dict['reward_cards']:
        one_id = str(id_)
        char_id = card_dict[one_id].get("characterId")
        char_name = get_name[char_id - 1]
        stars = card_dict[one_id].get("rarity")

        server_id = 0  # jp is 0, us is 1, etc
        title = ''
        while True:
            try:
                release_time = card_dict[one_id].get("releasedAt")[server_id]
                int(release_time)
                title = card_dict[one_id].get("prefix")[server_id]
                break
            except TypeError:
                server_id += 1
                continue
            except IndexError:
                break
        result += title + '（' + char_name + ' ' + '⭐' * stars + '）\n'

    result += '\nI\'m a bot, and this message is automatically generated.\nUpdate time: ' \
              + now.strftime("%H:%M %a %d. %b %Y, %Z")

    print(result)
    f = open('change_log.json', 'w')
    mdict = {}
    mdict.update({"msg": result})
    json.dump(mdict, f, indent=4, separators=(',', ': '))
    f.close()


if __name__ == '__main__':
    start()

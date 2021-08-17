#!/usr/bin/python3
import requests, json, datetime, pytz

RECENT_URL = 'https://bestdori.com/api/news/dynamic/recent.json'
BIRTHDAY_URL = 'https://bestdori.com/api/characters/main.birthday.json'
EVENT_URL = 'https://bestdori.com/api/events/'  # number.json
CARD_URL = "https://bestdori.com/api/cards/all.5.json"
get_name = ["placeholder",
            "戸山 香澄", "花園 たえ", "牛込 りみ", "山吹 沙綾", "市ヶ谷 有咲",
            "美竹 蘭", "青葉 モカ", "上原 ひまり", "宇田川 巴", "羽沢 つぐみ",
            "弦卷 こころ", "濑田 薰", "北沢 はぐみ", "松原 花音", "奥沢 美咲",
            "丸山 彩", "氷川 日菜", "白鷺 千聖", "大和 麻弥", "若宮 イヴ",
            "湊 友希那", "氷川 紗夜", "今井 リサ", "宇田川 あこ", "白金 燐子",
            "倉田 ましろ", "桐ケ谷 透子", "広町 七深", "二葉 つくし", "八潮 瑠唯",
            "和奏 レイ", "朝日 六花", "佐藤 ますき", "鳰原 令王那", "珠手 ちゆ"]

jptz = pytz.timezone('Asia/Tokyo')

BIRTHDAY_ARR = [0,
                963500400, 975855600, 953737200, 958662000, 972572400,
                955292400, 967906800, 972226800, 955724400, 947170800,
                965660400, 951663600, 964882800, 957970800, 970326000,
                977842800, 953478000, 954946800, 973177200, 962031600,
                972486000, 953478000, 967129200, 962550000, 971708400,
                950886000, 976892400, 961081200, 968943600, 974559600,
                947689200, 963759600, 958057200, 953910000, 976114800]

BIRTHDAY_DATETIME = []


def gen_birthday_datetime():
    global BIRTHDAY_DATETIME
    now = datetime.datetime.now(tz=jptz)
    for timestamp in BIRTHDAY_ARR:
        dt = datetime.datetime.fromtimestamp(timestamp, tz=jptz)
        dt = dt.replace(year=now.year)
        BIRTHDAY_DATETIME.append(dt)


def get_birthday():
    birthdict = requests.get(BIRTHDAY_URL).json()
    for i in range(35):
        int_ = int(birthdict[str(i + 1)]['profile']['birthday']) / 1000
        BIRTHDAY_ARR.append(int(int_))

    print(BIRTHDAY_ARR)


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
        char_name = get_name[char_id]
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

    gen_birthday_datetime()
    remain_sec = []
    # check remaining days
    for i in range(35):
        char_id = i + 1
        if now > BIRTHDAY_DATETIME[char_id] + datetime.timedelta(days=1):  # birthday has passed
            BIRTHDAY_DATETIME[char_id] = BIRTHDAY_DATETIME[char_id].replace(year=BIRTHDAY_DATETIME[char_id].year + 1)
        remain = BIRTHDAY_DATETIME[char_id] - now
        remain_sec.append({'id': char_id, 'remain': int(remain.total_seconds())})
        # print(remain.days)
    remain_sec.sort(key=lambda record: record['remain'])
    # print(remain_sec)
    result += '\n【Birthday】\n'
    for i in range(3):  # show first 3 birthdays
        char_id = remain_sec[i]['id']
        result += get_name[char_id]
        result += ' (' + BIRTHDAY_DATETIME[char_id].strftime("%d %b, %Y") + ') '
        if remain_sec[i]['remain'] <= 0:
            result += 'Happy Birthday🎂️'
        result += '\n'

    result += '\nI\'m a bot, and this message is automatically generated.\nLast update: ' \
              + now.strftime("%H:%M %a %d. %b %Y, %Z")

    # print(result)
    f = open('change_log.json', 'w')
    mdict = {}
    mdict.update({"msg": result})
    json.dump(mdict, f, indent=4, separators=(',', ': '))
    f.close()


if __name__ == '__main__':
    start()

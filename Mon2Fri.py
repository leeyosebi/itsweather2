from datetime import datetime
import requests
import json
import asyncio
import telegram
import nest_asyncio
import emoji

nest_asyncio.apply()

async def get_weather_data():
    today_date = datetime.today().strftime('%Y%m%d')
    print(today_date)
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    params = {
        'serviceKey': '',
        'pageNo': '1',
        'numOfRows': '100000',
        'dataType': 'JSON',
        'base_date': today_date,
        'base_time': '0000',
        'nx': '61',
        'ny': '125'
    }

    response = requests.get(url, params=params)
    return response.json()["response"]["body"]["items"]["item"]

def get_weather_status(pty_value):
    weather_statuses = {
        '0': "아무것도 안내려요",
        '1': "비와요 \U0001F327",
        '2': "눈도 오고 비도와요 \U0001F327 \U0001F328",
        '3': "눈와요 \U0001F328",
        '4': "소나기에요 \U0001F302"
    }
    return weather_statuses.get(pty_value, "알 수 없는 날씨")

def get_wind_speed_status(wsd_value):
    wsd_value = float(wsd_value)
    if wsd_value < 4:
        return "약하게 불어요"
    elif 4 <= wsd_value < 9:
        return "약간 강해요"
    elif 9 <= wsd_value < 14:
        return "강해요"
    else:
        return "엄청 강해요"

def calculate_wind_chill_temperature(t1h_value, wsd_value):
    num0_1 = float(t1h_value)
    num0_2 = float(wsd_value)
    return round(13.12 + 0.6215 * num0_1 - 11.37 * (3.6 * num0_2) ** 0.16 + 0.3965 * (3.6 * num0_2) ** 0.16 * num0_1)

async def send_daily_message():
    today_date_message = datetime.today().strftime('%dth %b, %Y (%a)')
    print(today_date_message)
    
    weather_data = await get_weather_data()

    pty_value = weather_data[0]["obsrValue"]  # 강수형태 코드값
    reh_value = weather_data[1]["obsrValue"]  # 습도 %
    rn1_value = weather_data[2]["obsrValue"]  # 1시간 강수량 mm
    t1h_value = weather_data[3]["obsrValue"]  # 기온 C
    wsd_value = weather_data[7]["obsrValue"]  # 풍속 m/s

    wind_chill_tmp = calculate_wind_chill_temperature(t1h_value, wsd_value)

    pty_status = get_weather_status(pty_value)
    wsd_status = get_wind_speed_status(wsd_value)

    token = ":"
    chat_id = 
    bot = telegram.Bot(token=token)

    #emoji blog.limcm.kr/148
    man_raising_hand = emoji.emojize(':man_raising_hand:')
    woman_raising_hand = emoji.emojize(':woman_raising_hand:')
    round_pushpin = emoji.emojize(':round_pushpin:')
    man_bowing = emoji.emojize(':man_bowing:')
    woman_bowing = emoji.emojize(':woman_bowing:')

    message = (
        f"{today_date_message}\n"
        f"\n"
        f"{man_raising_hand}안녕하세요, 퇴근날씨입니다{woman_raising_hand}\n"
        f"\n"
        f"{round_pushpin}현재날씨에요{round_pushpin}\n"
        f"------------------------------\n"
        f"ㅤㅤ온도ㅤ:ㅤ{t1h_value}°C\n"
        f"체감온도ㅤ:ㅤ{wind_chill_tmp}°C\n"
        f"ㅤㅤ습도ㅤ:ㅤ{reh_value}%\n"
        f"바람세기ㅤ:ㅤ{wsd_status}\n"
        f"ㅤ강수량ㅤ:ㅤ{rn1_value}%\n"
        f"강수형태ㅤ:ㅤ{pty_status}\n"
        f"------------------------------\n"
        f"\n"
        f"{round_pushpin}날씨는 매일 6:00pm에 안내돼요\n"
        f"{man_bowing}얼른 퇴근하세요{woman_bowing}"
    )

    await bot.send_message(chat_id, message)

async def main():
    while True:
        await send_daily_message()
        await asyncio.sleep(86400)  # 24시간 대기

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

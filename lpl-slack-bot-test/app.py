from requests_html import HTMLSession
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 환경 변수 로드
load_dotenv()

# 슬랙 봇 토큰과 URL을 환경 변수에서 가져옴
slack_token = os.getenv('SLACK_BOT_TOKEN')
target_url = os.getenv('TARGET_URL')

# 슬랙 클라이언트 설정
client = WebClient(token=slack_token)

# HTMLSession 생성
session = HTMLSession()

# 웹페이지 요청 및 자바스크립트 렌더링
response = session.get(target_url)
response.html.render()

# BeautifulSoup과 유사한 방식으로 HTML 파싱
rows = response.html.find('tbody > tr')
message_text = ""

for row in rows:
    tds = row.find('td')
    if len(tds) >= 4:
        second_td_text = tds[1].text.strip()
        third_td_text = tds[2].text.strip()
        fourth_td_text = tds[3].text.strip()

        if third_td_text != '-':
            message_text = f"{second_td_text} {third_td_text} {fourth_td_text}"
            break

# 메시지 처리 로직은 이전 코드와 동일
last_message_file = "last_message.txt"

if os.path.exists(last_message_file):
    with open(last_message_file, 'r') as file:
        last_message = file.read().strip()
else:
    last_message = ""

if message_text and message_text == last_message:
    try:
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response['channels']

        for channel in channels:
            channel_id = channel['id']
            try:
                client.chat_postMessage(channel=channel_id, text=message_text)
                print(f"Message sent to {channel['name']} successfully")
            except SlackApiError as e:
                print(f"Error sending message to {channel['name']}: {e.response['error']}")

        with open(last_message_file, 'w') as file:
            file.write(message_text)

    except SlackApiError as e:
        print(f"Error fetching channels or sending messages: {e.response['error']}")
else:
    print("No new data to send or message is the same as last one.")
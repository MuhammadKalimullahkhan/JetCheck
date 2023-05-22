import requests

cookies = {
    '_ga': 'GA1.1.1711508791.1683038799',
    '_ga_0YHYR2F422': 'GS1.1.1683038799.1.1.1683040205.0.0.0',
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://www.zerogpt.com',
    'Referer': 'https://www.zerogpt.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64',
    'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def detect(input_text) -> dict:
    json_data = {
        'input_text': input_text,
    }

    res = requests.post('https://api.zerogpt.com/api/detect/detectText', cookies=cookies, headers=headers, json=json_data)
    return res.json()


def mark_changes(input_text: str, chaged_sentances: list):
    replaced_text = input_text
    for i in chaged_sentances:
        replaced_text = replaced_text.replace(i, f"<mark>{i}</mark>")
    return replaced_text

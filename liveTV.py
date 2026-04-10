import requests, yaml, os, configparser
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 현재 .py파일이 존재하는 경로를 작업 경로로 설정
app_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(app_path)

# liveTV.ini에서 설정 불러오기
config = configparser.ConfigParser()
config.optionxform = str
config.read(f'{app_path}/liveTV.ini', encoding='UTF8')

settings = config['ALIVE']
alive_m3u_url   = settings["alive_m3u_url"]
alive_m3U_path  = settings["alive_m3U_path"]
alive_yaml_path = settings["alive_yaml_path"]

settings = config['SPOTV']
spotv_m3u_url   = settings["spotv_m3u_url"]
spotv_m3u_path  = settings["spotv_m3u_path"]
spotv_yaml_path = settings["spotv_yaml_path"]

settings = config['PLEX']
plex_url   = settings["plex_url"]
plex_token = settings["plex_token"]
section_id = settings["section_id"]

# url로부터 파일을 저장(m3u, yaml)
def save_response_to_file(url, file_path):
    try:
        response = requests.get(url)

        # 요청이 성공적으로 완료된 경우
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"응답이 {file_path}에 성공적으로 저장되었습니다.")
            return True
        else:
            print(f"요청이 실패했습니다. 상태 코드: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"요청중 오류가 발생했습니다: {e}")
        return False

# data를 yaml파일로 작성
def make_yaml(show_data, target_path):
    with open(target_path, 'w', encoding="utf-8") as outfile:
        yaml.dump(show_data, outfile, sort_keys=False, allow_unicode=True)

# 스포티비 썸네일 얻기
def get_spotv_thumb(param):
    base = 'https://raw.githubusercontent.com/zeliit/PlexLiveTV/main/thumb'
    if 'ch=spotv2' in param:
        return f'{base}/spotv2.jpg'
    elif 'ch=spotvgnh' in param:
        return f'{base}/spotvgnh.jpg'
    elif 'ch=spotv' in param:
        return f'{base}/spotv.png'
    elif 'ch=primeplus' in param:
        return f'{base}/primeplus.jpg'
    elif 'ch=prime2' in param:
        return f'{base}/prime2.jpg'
    elif 'ch=prime' in param:
        return f'{base}/prime.jpg'
    else:
        return None

# # 스포티비 채널 ID 추출 (요청 속도나 서버상태에 따라 오류 잦음)
# def get_spotv_ch_id(param):    
#     parsed = urlparse(param)
#     query_params = parse_qs(parsed.query)
#     return query_params['ch_id'][0]

# # 스포티비 썸네일 얻기2 (요청이 속도나 서버상태에 따라 오류 잦음)
# def get_spotv_thumb(param):    
#     ch_id = get_spotv_ch_id(param)
#     get_thumb_from_url(ch_id, param)
#     return f'{image_server_url}/{ch_id}.jpg'    

# 스포티비 m3u를 plex용 yaml로 변환
def get_yaml_from_spotv_m3u(m3u_path, yaml_path):
    extra_data = []
    with open(m3u_path, "r", encoding='utf-8') as m3u_file:
        lines = m3u_file.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("#EXTINF:-1"):
                start_index = line.find("tvg-name=")
                if start_index != -1:
                    end_index = line.find('"', start_index + 10)
                    title = line[start_index + 10 : end_index].strip()
                    param = lines[i + 1].strip()
                    content = {
                        'mode': 'm3u8',
                        'type': 'featurette',
                        'param': param,
                        'title': title,
                        'thumb': get_spotv_thumb(param),
                    }
                    extra_data.append(content)

    show_data = {
        'primary': True,
        'code': 'spotv',
        'title': '스포티비',
        'posters': 'https://raw.githubusercontent.com/zeliit/PlexLiveTV/main/poster/SPOTV.webp',
        'summary': f'SPOTV 채널\n{current_time}',
        'extras': extra_data
    }
    make_yaml(show_data, yaml_path)



# Alive m3u를 plex용 yaml로 변환
def get_yaml_from_alive_m3u(m3u_path, yaml_path):
    extra_data = []
    with open(m3u_path, "r", encoding='utf-8') as m3u_file:
        lines = m3u_file.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("#EXTINF:-1"):
                start_index = line.find("tvg-name=")
                if start_index != -1:
                    end_index = line.find('"', start_index + 10)
                    title = line[start_index + 10 : end_index].strip()
                    param = lines[i + 1].strip()
                    content = {
                        'mode': 'm3u8',
                        'type': 'featurette',
                        'param': param,
                        'title': title,
                    }
                    extra_data.append(content)
    show_data = {
        'primary': True,
        'code': 'alive',
        'title': 'ALIVE',
        'posters': 'https://raw.githubusercontent.com/zeliit/PlexLiveTV/main/poster/Alive.webp',
        'summary': f'ALIVE 채널\n{current_time}',
        'extras': extra_data
    }
    make_yaml(show_data, yaml_path)

# Plex 특정 섹션 리프레시
def refresh_section_metadata(plex_url, plex_token, section_id):
    headers = {"X-Plex-Token": plex_token}
    url = f"{plex_url}/library/sections/{section_id}/refresh?force=1"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while refreshing metadata: {e}")


# Alive yaml 작성
if alive_m3u_url:
    if save_response_to_file(alive_m3u_url, alive_m3U_path):
        get_yaml_from_alive_m3u(alive_m3U_path, alive_yaml_path)

# 스포티비 yaml 작성
if save_response_to_file(spotv_m3u_url, spotv_m3u_path):
    get_yaml_from_spotv_m3u(spotv_m3u_path, spotv_yaml_path)


# Plex 실시간 TV 리프레시
if plex_url and plex_token and section_id:
    refresh_section_metadata(plex_url, plex_token, section_id)   

import requests, yaml, os, configparser
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timestamp = datetime.now().strftime("?v=%Y%m%d%H%M%S")

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

# 스포티비 썸네일 얻기(klive_plus용)
def get_spotv_thumb(param):    
    if 'ch_id=9' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/710e7a39f7910d4d828047e1222e2dce.png'
    elif 'ch_id=10' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/55509fff870629e4db8865ed79988c56.png'
    elif 'ch_id=15' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/dfc390d3df155cbaf02be7da5c9a92af.png'
    elif 'ch_id=11' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/0011057bb69a02e3b3827ab82b57b849.png'
    elif 'ch_id=1' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/452e738814aba6b8dbe3688929368a6d.png'
    elif 'ch_id=2' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/3daa55ea25c6274dea97f35e170de79d.png'
    elif 'ch_id=3' in param:
        return 'https://cdn.spotvnow.co.kr/src/upload/image/20211215/0bc2fb062edbd8f2a05b64e291b148b8.png'
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
        'posters': f'{app_path}/poster/SPOTV.webp',
        'summary': f'SPOTV 채널\n{current_time}',
        'extras': extra_data
    }
    make_yaml(show_data, yaml_path)



# 채널 이름에서 Alive 썸네일 얻기
def get_alive_thumb(ch_name):
    # 지상파        
    if ch_name == 'SBS':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/S01.jpg{timestamp}'
    elif ch_name == '1TV':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K01.jpg{timestamp}'
    elif ch_name == '2TV':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K02.jpg{timestamp}'    
    elif ch_name == 'MBC':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/M01.jpg{timestamp}'
    # 연예/오락
    elif ch_name == 'KBS Joy':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K04.jpg{timestamp}'
    elif ch_name == 'MBC every1':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/M03.jpg{timestamp}'
    elif ch_name == 'KBS WORLD':
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/K03.jpg'
    elif ch_name == 'SBS funE':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/S04.jpg{timestamp}'
    # 스포츠
    elif ch_name == 'SBS Sports':
        return f'https://program-image.cloud.sbs.co.kr/espn.jpg{timestamp}'
    elif ch_name == 'SBS Golf':
        return f'https://program-image.cloud.sbs.co.kr/golf.jpg{timestamp}'    
    elif ch_name == 'SBS Golf2':
        return f'https://program-image.cloud.sbs.co.kr/golf2.jpg{timestamp}'
    # 드라마
    elif ch_name == 'MBC 드라마':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/M02.jpg{timestamp}'
    elif ch_name == 'SBS Plus':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/S03.jpg{timestamp}'
    elif ch_name == 'KBS Drama':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K06.jpg{timestamp}'
    elif ch_name == 'MBC ON':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/M14.jpg{timestamp}'
    # 음악
    elif ch_name == 'MBC M':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/M06.jpg{timestamp}'
    elif ch_name == 'SBS M':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/S09.jpg{timestamp}'
    elif ch_name == 'K POP':
        return 'https://program-image.cloud.sbs.co.kr/kpop.jpg'
    # 어린이
    elif ch_name == 'KBS KIDS':
        return 'https://img.kbs.co.kr/kbs/232x130/padmin.static.kbs.co.kr/live/2021/5/28/1622175270598_252287.jpg'
    # 여성/패션
    elif ch_name == 'KBS Story':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K09.jpg{timestamp}'
    # 공공/교양/종교
    elif ch_name == '독도':
        return f'https://img.kbs.co.kr/kbs/232x130/padmin.static.kbs.co.kr/live/2021/8/6/1628236007412_271532.jpg{timestamp}'
    # 뉴스/경제
    elif ch_name == 'KBS NEWS D':
        return 'https://img.kbs.co.kr/kbs/232x130/padmin.static.kbs.co.kr/live/2021/11/5/1636096742321_283901.jpg'
    elif ch_name == 'SBS BIZ':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/S06.jpg{timestamp}'
    # 다큐
    elif ch_name == 'KBS LIFE':
        return f'https://image.wavve.com/v1/thumbnails/480_270_20_80/live/thumbnail/K05.jpg{timestamp}'    
    # 라디오
    elif ch_name == '1FM': # KBS 클래식 FM
        return 'https://padmin.static.kbs.co.kr/live/2021/5/28/1622175310040_252323.jpg' 
    elif ch_name == '2FM': # KBS Cool FM
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/K08.jpg' 
    elif ch_name == 'FM4U': # MBC FM4U
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/M08.jpg' 
    elif ch_name == '표준FM': # MBC 표준FM
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/M07.jpg' 
    elif ch_name == 'POWER FM': # SBS 파워FM
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/S07.jpg' 
    elif ch_name == 'LOVE FM': # SBS 러브FM
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/S08.jpg' 
    elif ch_name == '1라디오': # KBS 1라디오
        return 'https://image.wavve.com/v1/thumbnails/480_270_20_80/BMS/Channelimage30/image/K07.jpg' 
    elif ch_name == '2라디오': # KBS 2라디오 (해피FM)
        return 'https://i.ytimg.com/vi/iWQ4E4ztzPg/maxresdefault.jpg' 
    elif ch_name == '3라디오': # KBS 3라디오
        return 'https://padmin.static.kbs.co.kr/live/2021/5/28/1622175309962_252312.jpg' 
    elif ch_name == '한민족방송': # KBS 한민족
        return 'https://padmin.static.kbs.co.kr/live/2021/5/28/1622175310180_252345.jpg' 
    elif ch_name == 'GorealraM': # SBS 고릴라라디오M
        return 'https://img2.sbs.co.kr/img/sbs_cms/PG/2018/03/29/PG47583773_w640_h360.jpg'
    elif ch_name == '올댓뮤직': # 올댓뮤직
        return 'https://scf.static.kbs.co.kr/image/NBCONTENTSMYLOVEKBS/NBCONTENTSMYLOVEKBS_70000000386706_20200818_20200818163500___EDITOR_01.jpg'     
    # MBC 라디오
    elif ch_name == 'POWER FM (보는 라디오)':
        return 'https://program-image.cloud.sbs.co.kr/power.jpg'
    elif ch_name == 'LOVE FM (보는 라디오)':
        return 'https://program-image.cloud.sbs.co.kr/love.jpg'
    # KBS 라디오
    elif ch_name == 'KBS WORLD MULTILINGUAL':
        return 'https://img.kbs.co.kr/kbs/232x130/padmin.static.kbs.co.kr/live/2022/11/18/1668733711236_319754.jpg'
    elif ch_name == 'KBS WORLD ENGLISH':
        return 'https://img.kbs.co.kr/kbs/232x130/programres.kbs.co.kr/i0000-2103/2022/5/2/1651479309808_381557.jpg'                                                                                                                     
    else:
        return None

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
                        'thumb': get_alive_thumb(title),
                    }
                    extra_data.append(content)
    show_data = {
        'primary': True,
        'code': 'alive',
        'title': 'ALIVE',
        'posters': f'{app_path}/poster/Alive.webp',
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

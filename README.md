# 개요
Plex에서 부가영상 기능을 통해 실시간 TV 시청

## 설정 파일
liveTV.ini.sample 파일 참조하여 ini 파일을 수정하여 사용  
YOUR_SECTION_ID 값은 실제 라이브러리의 ID(숫자)를 입력해야함  
아래 라이브러리 주소 뒷부분 ID 부분만 가져오면 됨 (12)  
예) localhost:32400/web/index.html#!/media/104/com.plexapp.plugins.library?source=12  


# 설치 경로(추천)
```
/mnt/PlexLiveTV
```

# 실행 방법
## 기본(약 5분 후 종료됨)
```
python3 /mnt/PlexLiveTV/liveTV.py
```

## 크론탭 5분 세팅 할 경우
```
* */5 * * * /usr/bin/python3 /mnt/PlexLiveTV/liveTV.py
```
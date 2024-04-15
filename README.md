# 개요
Plex에서 부가영상 기능을 통해 실시간 TV 시청

# 설치 경로(추천)
```
/mnt/PlexLiveTV
```

# 실행 방법
## 기본(약 5분 후 종료됨)
```
python3 /mnt/PlexLiveTV/liveTV.py
```

## 크론탭
```
* */5 * * * /usr/bin/python3 /mnt/PlexLiveTV/liveTV.py
```

## 스크린으로 실행 및 종료5초 후 재실행
```
/usr/bin/screen -dmS LiveTV sh -c "while true; do /usr/bin/python3 /mnt/PlexLiveTV/liveTV.py; sleep 5; done"
```
- 스크린 접속
```
screen -r LiveTV
```


## 크론탭에서 부팅 후 실행.(스크린으로 실행 및 종료5초 후 재실행)
```
@reboot /usr/bin/screen -dmS LiveTV sh -c "while true; do /usr/bin/python3 /mnt/PlexLiveTV/liveTV.py; sleep 5; done"
```
- 스크린 접속
```
screen -r LiveTV
```
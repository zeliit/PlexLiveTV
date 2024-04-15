# 개요
Plex에서 부가영상 기능을 통해 실시간 TV 시청

# 실행 방법
```
/usr/bin/screen -dmS LiveTV sh -c "while true; do /usr/bin/python3 /mnt/PlexLiveTV/liveTV.py; sleep 5; done"
```

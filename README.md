# 슬랙봇
`fastapi` 기반의 슬랙봇

## 설치 및 실행
1. git clone
    ```shell
    git clone git@github.com:olivahn/slackbot-fastapi.git && cd slackbot-fastapi
    ```
2. 파이썬 가상환경 생성
    ```shell
    python3 -m venv .venv
    ```
3. 파이썬 가상환경 활성화
    ```shell
    source .venv/bin/activate
    ```
4. 파이썬 패키지 설치
    ```shell
    pip3 install --upgrade pip && pip3 install -r requirements.txt
    ```
5. 환경설정
  - `.env` 파일 생성 후 아래 내용 기입
    ```text
    SLACK_TOKEN=
    SLACK_SIGNING_SECRET=

    CHATGPT_EMAIL=
    CHATGPT_PASSWORD=
    ```
  - `distributors.txt` 파일 생성 후 배포 권한을 줄 사람의 슬랙 ID를 다음과 같이 줄 단위로 기입
  
    ```text
    U01A2B3C4D5
    U01A2B3C4D6
    U01A2B3C4D7
    ```
  
6. 실행
    > **NOTE**
    >
    > `uvicorn main:app --reload` 로 실행할 경우 Chat-GPT 로그인이 빈번하게 발생하여 일시적으로 IP가 차단당할 수도 있습니다. 

    ```shell
    # basic
    uvicorn main:app
    
    # specific port 
    uvicorn main:app --port=45678
    ```

## 기능

### 봇 멘션
- Chat-GPT에게 질문

### 슬래쉬 명령어
- `/release` : 배포를 시작합니다. 배포 권한이 있는 사람만 사용할 수 있으며, 정말로 배포를 시작할 것인지 한번 더 묻습니다.


## 실행 로그
- `slackbot.log`를 확인하세요.
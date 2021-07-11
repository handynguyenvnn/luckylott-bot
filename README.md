# Crypto Lotto Bot


### Create telegram bot chat by BotFather

Return telegram bot token

See [Create a Telegram bot using BotFather and Get the Api Token](https://medium.com/shibinco/create-a-telegram-bot-using-botfather-and-get-the-api-token-900ba00e0f39)

### Python 3.7.2

### Python PIP

### Python virtualenv
```
pip3 install -U pip virtualenv
```

### Create virtualenv
```
virtualenv -p python ./env
```

### Create virtualenv
Window
```
.\env\Scripts\activate
```
Ubuntu
```
source env/bin/activate
```
### Install packages
```
pip3 install -r requirements.txt
```

### Deploy
```

Server: 206.189.33.52
Kill process

ps -aux | grep python

Check process id and kill old process

pkill -9 PID

cd bot

source env/bin/activate

nohup python3 crypto_lotto_bot_prod.py &


```

# supper-service
```bash
docker build . -t supper-service:latest && docker run --rm -it -p 3000:3000 -p 4040:4040 --name supper-service supper-service
./ngrok http 3000
# Add http://<ngrok_id>.ngrok.io/slack/events to https://api.slack.com/apps/<app_id>/event-subscriptions?
```

```bash
docker exec -it supper-service bash
python main.py
```

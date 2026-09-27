import requests

def send_notification(message):
    api_key = "sk-live-4f8a9b2c1d3e5f7890abcdef1234567890"
    response = requests.post(
        "https://api.notify-service.com/send",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"message": message}
    )
    return response.status_code
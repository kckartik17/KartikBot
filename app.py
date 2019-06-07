from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from utils import fetch_reply

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    num_media = int(request.values.get("NumMedia"))
    msg = request.form.get('Body')
    sender = request.form.get('From')
    if not num_media:
        print("Not media")
        
         # Create reply
        resp = MessagingResponse()
        resp.message(fetch_reply(msg, sender))
        return str(resp)
    else:
        print("media")
        resp = MessagingResponse()
        resp.message("Hey! That's my owner !!").media("https://media.licdn.com/dms/image/C5103AQH8p0CudD95fA/profile-displayphoto-shrink_200_200/0?e=1565222400&v=beta&t=wrZjd-7f9WB_R7_JhbINdcZ5nBg8kePnBzVLiKuPDmY")
        return str(resp)

   

if __name__ == "__main__":
    app.run(debug=True)
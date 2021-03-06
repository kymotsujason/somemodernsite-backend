# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
#from chat.models.message import Message
#from chat.models.user import User

class ChatConsumer(WebsocketConsumer):
    
    def new_message(self, data):
        author = data['from']
        text = data['text']
        message = {
            "author": author,
            "content": text,
        }
        content = {
            'command': 'chat-new_message',
            'message': message
        }
        self.send_chat_message(content)

    def new_event(self, data):
        author = data['from']
        text = data['text']
        message = {
            "author": author,
            "content": text,
        }
        content = {
            'command': 'chat-event',
            'message': message
        }
        self.send_chat_message(content)

    commands = {
        'chat-new_message': new_message,
        'chat-event': new_event,
    }

    def connect(self):
        self.room_name = 'global'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave group room
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
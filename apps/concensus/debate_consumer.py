from channels.generic.websocket import JsonWebsocketConsumer

class NotificationConsumer(JsonWebsocketConsumer):
    group_name = str
    def connect(self):
        self.group_name = f"user_{self.scope['user'].id}"
        self.channel_layer.group_add(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    def notify(self, event):
        self.send_json({"message": event["message"]})

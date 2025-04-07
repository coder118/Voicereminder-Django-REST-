import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer

class TTSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        print(f"Connected user_id: {self.user_id}")  # 콘솔 출력
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(f"user_{self.user_id}_tts")
        
        await self.accept()
        
        # 메시지 수신 루프
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                await self.send(text_data=message['data'].decode('utf-8'))

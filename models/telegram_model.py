import schedule
import time
from datetime import datetime
from typing import Optional, Callable
from telegram import Bot
from telegram.error import TelegramError


class TelegramModel:
    """텔레그램 API와 메시지 스케줄링을 담당하는 Model 클래스"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.chat_ids: list = []  # 여러 채팅방 ID를 저장하는 리스트
        self.scheduled_messages = []
        self.is_running = False
        self._callback: Optional[Callable] = None
    
    def set_callback(self, callback: Callable):
        """ViewModel에서 상태 변경을 알리기 위한 콜백 설정"""
        self._callback = callback
    
    def set_bot_token(self, token: str) -> bool:
        """봇 토큰 설정"""
        try:
            self.bot = Bot(token=token)
            return True
        except Exception as e:
            print(f"봇 토큰 설정 실패: {e}")
            return False
    
    def set_chat_ids(self, chat_ids: list):
        """채팅방 ID 목록 설정"""
        self.chat_ids = [chat_id.strip() for chat_id in chat_ids if chat_id.strip()]
    
    def add_chat_id(self, chat_id: str):
        """채팅방 ID 추가"""
        chat_id = chat_id.strip()
        if chat_id and chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
    
    def remove_chat_id(self, chat_id: str):
        """채팅방 ID 제거"""
        if chat_id in self.chat_ids:
            self.chat_ids.remove(chat_id)
    
    def send_message(self, message: str) -> dict:
        """메시지 전송 (동기 방식) - 모든 채팅방에 전송"""
        if not self.bot or not self.chat_ids:
            return {"success": False, "sent_count": 0, "total_count": 0, "errors": []}
        
        results = {"success": True, "sent_count": 0, "total_count": len(self.chat_ids), "errors": []}
        
        for chat_id in self.chat_ids:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(self._async_send_message(message, chat_id))
                loop.close()
                
                if success:
                    results["sent_count"] += 1
                else:
                    results["errors"].append(f"채팅방 {chat_id}: 전송 실패")
                    results["success"] = False
            except Exception as e:
                results["errors"].append(f"채팅방 {chat_id}: {str(e)}")
                results["success"] = False
        
        return results
    
    async def _async_send_message(self, message: str, chat_id: str) -> bool:
        """비동기 메시지 전송"""
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            return True
        except TelegramError as e:
            print(f"텔레그램 API 오류 (채팅방 {chat_id}): {e}")
            return False
    
    def add_scheduled_message(self, message: str, time_str: str, interval: str = "daily"):
        """스케줄된 메시지 추가"""
        schedule_id = len(self.scheduled_messages)
        
        def job():
            self._send_scheduled_message(message, schedule_id)
        
        # 스케줄 설정
        if interval == "daily":
            schedule.every().day.at(time_str).do(job)
        elif interval == "hourly":
            schedule.every().hour.at(f":{time_str.split(':')[1]}").do(job)
        elif interval == "weekly":
            schedule.every().monday.at(time_str).do(job)
        
        self.scheduled_messages.append({
            'id': schedule_id,
            'message': message,
            'time': time_str,
            'interval': interval,
            'enabled': True
        })
        
        if self._callback:
            self._callback('message_added', self.scheduled_messages[-1])
    
    def _send_scheduled_message(self, message: str, schedule_id: int):
        """스케줄된 메시지 전송"""
        results = self.send_message(message)
        
        if self._callback:
            self._callback('message_sent', {
                'schedule_id': schedule_id,
                'message': message,
                'success': results['success'],
                'sent_count': results['sent_count'],
                'total_count': results['total_count'],
                'errors': results['errors'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    def remove_scheduled_message(self, schedule_id: int):
        """스케줄된 메시지 제거"""
        schedule.clear()
        self.scheduled_messages = [msg for msg in self.scheduled_messages if msg['id'] != schedule_id]
        
        if self._callback:
            self._callback('message_removed', schedule_id)
    
    def start_scheduler(self):
        """스케줄러 시작"""
        self.is_running = True
        if self._callback:
            self._callback('scheduler_started', None)
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        import threading
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        schedule.clear()
        if self._callback:
            self._callback('scheduler_stopped', None)
    
    def get_scheduled_messages(self):
        """스케줄된 메시지 목록 반환"""
        return self.scheduled_messages
    
    def get_chat_ids(self):
        """등록된 채팅방 ID 목록 반환"""
        return self.chat_ids

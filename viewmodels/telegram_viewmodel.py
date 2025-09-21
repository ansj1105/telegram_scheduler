from typing import Optional, List, Dict, Any
from models.telegram_model import TelegramModel


class TelegramViewModel:
    """텔레그램 스케줄러의 비즈니스 로직을 담당하는 ViewModel 클래스"""
    
    def __init__(self):
        self.model = TelegramModel()
        self.model.set_callback(self._on_model_callback)
        self._view_callback: Optional[callable] = None
        
        # 상태 관리
        self.bot_token = ""
        self.chat_ids = []  # 여러 채팅방 ID를 저장하는 리스트
        self.is_connected = False
        self.scheduler_running = False
    
    def set_view_callback(self, callback: callable):
        """View에서 UI 업데이트를 위한 콜백 설정"""
        self._view_callback = callback
    
    def _on_model_callback(self, event_type: str, data: Any):
        """Model에서 발생한 이벤트 처리"""
        if self._view_callback:
            self._view_callback(event_type, data)
    
    def set_bot_token(self, token: str) -> bool:
        """봇 토큰 설정"""
        self.bot_token = token
        success = self.model.set_bot_token(token)
        if success:
            self.is_connected = True
        return success
    
    def set_chat_ids(self, chat_ids: list):
        """채팅방 ID 목록 설정"""
        self.chat_ids = [chat_id.strip() for chat_id in chat_ids if chat_id.strip()]
        self.model.set_chat_ids(self.chat_ids)
    
    def add_chat_id(self, chat_id: str) -> bool:
        """채팅방 ID 추가"""
        chat_id = chat_id.strip()
        if not chat_id:
            return False
        
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            self.model.add_chat_id(chat_id)
            return True
        return False
    
    def remove_chat_id(self, chat_id: str):
        """채팅방 ID 제거"""
        if chat_id in self.chat_ids:
            self.chat_ids.remove(chat_id)
            self.model.remove_chat_id(chat_id)
    
    def get_chat_ids(self) -> list:
        """등록된 채팅방 ID 목록 반환"""
        return self.chat_ids
    
    def add_scheduled_message(self, message: str, time_str: str, interval: str = "daily") -> bool:
        """스케줄된 메시지 추가"""
        if not message.strip():
            return False
        
        try:
            self.model.add_scheduled_message(message, time_str, interval)
            return True
        except Exception as e:
            print(f"메시지 추가 실패: {e}")
            return False
    
    def remove_scheduled_message(self, schedule_id: int):
        """스케줄된 메시지 제거"""
        self.model.remove_scheduled_message(schedule_id)
    
    def start_scheduler(self) -> bool:
        """스케줄러 시작"""
        if not self.is_connected or not self.chat_ids:
            return False
        
        try:
            self.model.start_scheduler()
            self.scheduler_running = True
            return True
        except Exception as e:
            print(f"스케줄러 시작 실패: {e}")
            return False
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.model.stop_scheduler()
        self.scheduler_running = False
    
    def get_scheduled_messages(self) -> List[Dict]:
        """스케줄된 메시지 목록 반환"""
        return self.model.get_scheduled_messages()
    
    def validate_time_format(self, time_str: str) -> bool:
        """시간 형식 검증 (HH:MM)"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except ValueError:
            return False
    
    def get_connection_status(self) -> str:
        """연결 상태 반환"""
        if self.is_connected and self.scheduler_running:
            return f"연결됨 (스케줄러 실행 중) - {len(self.chat_ids)}개 채팅방"
        elif self.is_connected:
            return f"연결됨 (스케줄러 중지됨) - {len(self.chat_ids)}개 채팅방"
        else:
            return "연결 안됨"

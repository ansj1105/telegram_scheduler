import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
from viewmodels.telegram_viewmodel import TelegramViewModel


class TelegramView:
    """텔레그램 스케줄러의 GUI를 담당하는 View 클래스"""
    
    def __init__(self):
        self.viewmodel = TelegramViewModel()
        self.viewmodel.set_view_callback(self._on_viewmodel_callback)
        
        # 메인 윈도우 설정
        self.root = tk.Tk()
        self.root.title("텔레그램 메시지 스케줄러")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self):
        """UI 구성 요소 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 봇 토큰 입력 섹션
        token_frame = ttk.LabelFrame(main_frame, text="봇 설정", padding="10")
        token_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(token_frame, text="봇 토큰:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.token_entry = ttk.Entry(token_frame, width=50, show="*")
        self.token_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(token_frame, text="채팅방 ID:").grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        
        # 채팅방 ID 입력 프레임
        chat_id_frame = ttk.Frame(token_frame)
        chat_id_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.chat_id_entry = ttk.Entry(chat_id_frame, width=40)
        self.chat_id_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.add_chat_id_btn = ttk.Button(chat_id_frame, text="추가", command=self._on_add_chat_id_clicked)
        self.add_chat_id_btn.grid(row=0, column=1)
        
        # 채팅방 ID 목록
        ttk.Label(token_frame, text="등록된 채팅방:").grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        
        list_frame = ttk.Frame(token_frame)
        list_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.chat_id_listbox = tk.Listbox(list_frame, height=3, width=50)
        self.chat_id_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 스크롤바
        chat_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.chat_id_listbox.yview)
        self.chat_id_listbox.configure(yscrollcommand=chat_scrollbar.set)
        chat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 삭제 버튼
        self.remove_chat_id_btn = ttk.Button(list_frame, text="선택 삭제", command=self._on_remove_chat_id_clicked)
        self.remove_chat_id_btn.grid(row=1, column=0, pady=(5, 0))
        
        self.connect_btn = ttk.Button(token_frame, text="연결", command=self._on_connect_clicked)
        self.connect_btn.grid(row=6, column=0, pady=(5, 0))
        
        # 상태 표시
        self.status_label = ttk.Label(token_frame, text="상태: 연결 안됨", foreground="red")
        self.status_label.grid(row=7, column=0, sticky=tk.W, pady=(5, 0))
        
        # 메시지 추가 섹션
        message_frame = ttk.LabelFrame(main_frame, text="메시지 추가", padding="10")
        message_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(message_frame, text="메시지 내용:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.message_text = scrolledtext.ScrolledText(message_frame, height=3, width=50)
        self.message_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 시간 설정
        time_frame = ttk.Frame(message_frame)
        time_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 5))
        
        ttk.Label(time_frame, text="시간 (HH:MM):").grid(row=0, column=0, sticky=tk.W)
        self.time_entry = ttk.Entry(time_frame, width=10)
        self.time_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(time_frame, text="반복:").grid(row=0, column=2, sticky=tk.W)
        self.interval_var = tk.StringVar(value="daily")
        interval_combo = ttk.Combobox(time_frame, textvariable=self.interval_var, 
                                    values=["daily", "hourly", "weekly"], width=10, state="readonly")
        interval_combo.grid(row=0, column=3, padx=(5, 0))
        
        self.add_message_btn = ttk.Button(message_frame, text="메시지 추가", command=self._on_add_message_clicked)
        self.add_message_btn.grid(row=3, column=0, pady=(10, 0))
        
        # 스케줄러 제어 섹션
        control_frame = ttk.LabelFrame(main_frame, text="스케줄러 제어", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="스케줄러 시작", command=self._on_start_clicked)
        self.start_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="스케줄러 중지", command=self._on_stop_clicked)
        self.stop_btn.grid(row=0, column=1, padx=(5, 0))
        
        # 스케줄된 메시지 목록
        list_frame = ttk.LabelFrame(main_frame, text="스케줄된 메시지", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 트리뷰 설정
        columns = ("시간", "반복", "메시지")
        self.message_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.message_tree.heading(col, text=col)
            self.message_tree.column(col, width=100)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.message_tree.yview)
        self.message_tree.configure(yscrollcommand=scrollbar.set)
        
        self.message_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 삭제 버튼
        self.remove_btn = ttk.Button(list_frame, text="선택된 메시지 삭제", command=self._on_remove_clicked)
        self.remove_btn.grid(row=1, column=0, pady=(5, 0))
        
        # 로그 섹션
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        token_frame.columnconfigure(0, weight=1)
        chat_id_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        message_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _setup_bindings(self):
        """이벤트 바인딩 설정"""
        self.message_tree.bind("<Double-1>", self._on_tree_double_click)
    
    def _on_add_chat_id_clicked(self):
        """채팅방 ID 추가 버튼 클릭 이벤트"""
        chat_id = self.chat_id_entry.get().strip()
        
        if not chat_id:
            messagebox.showerror("오류", "채팅방 ID를 입력해주세요.")
            return
        
        success = self.viewmodel.add_chat_id(chat_id)
        if success:
            self.chat_id_entry.delete(0, tk.END)
            self._update_chat_id_list()
            self._log(f"채팅방 ID 추가됨: {chat_id}")
        else:
            messagebox.showwarning("경고", "이미 등록된 채팅방 ID입니다.")
    
    def _on_remove_chat_id_clicked(self):
        """채팅방 ID 삭제 버튼 클릭 이벤트"""
        selection = self.chat_id_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 채팅방 ID를 선택해주세요.")
            return
        
        chat_id = self.chat_id_listbox.get(selection[0])
        if messagebox.askyesno("확인", f"채팅방 ID '{chat_id}'를 삭제하시겠습니까?"):
            self.viewmodel.remove_chat_id(chat_id)
            self._update_chat_id_list()
            self._log(f"채팅방 ID 삭제됨: {chat_id}")
    
    def _on_connect_clicked(self):
        """연결 버튼 클릭 이벤트"""
        token = self.token_entry.get().strip()
        chat_ids = self.viewmodel.get_chat_ids()
        
        if not token:
            messagebox.showerror("오류", "봇 토큰을 입력해주세요.")
            return
        
        if not chat_ids:
            messagebox.showerror("오류", "최소 하나의 채팅방 ID를 추가해주세요.")
            return
        
        success = self.viewmodel.set_bot_token(token)
        if success:
            self._log(f"봇 연결 성공 - {len(chat_ids)}개 채팅방 등록됨")
            messagebox.showinfo("성공", f"봇 연결이 완료되었습니다.\n{len(chat_ids)}개 채팅방이 등록되었습니다.")
        else:
            self._log("봇 연결 실패")
            messagebox.showerror("오류", "봇 연결에 실패했습니다. 토큰을 확인해주세요.")
    
    def _on_add_message_clicked(self):
        """메시지 추가 버튼 클릭 이벤트"""
        message = self.message_text.get("1.0", tk.END).strip()
        time_str = self.time_entry.get().strip()
        interval = self.interval_var.get()
        
        if not message:
            messagebox.showerror("오류", "메시지 내용을 입력해주세요.")
            return
        
        if not time_str:
            messagebox.showerror("오류", "시간을 입력해주세요.")
            return
        
        if not self.viewmodel.validate_time_format(time_str):
            messagebox.showerror("오류", "시간 형식이 올바르지 않습니다. (HH:MM)")
            return
        
        success = self.viewmodel.add_scheduled_message(message, time_str, interval)
        if success:
            self.message_text.delete("1.0", tk.END)
            self.time_entry.delete(0, tk.END)
            self._log(f"메시지 추가됨: {time_str} ({interval}) - {message[:30]}...")
        else:
            messagebox.showerror("오류", "메시지 추가에 실패했습니다.")
    
    def _on_start_clicked(self):
        """스케줄러 시작 버튼 클릭 이벤트"""
        success = self.viewmodel.start_scheduler()
        if success:
            self._log("스케줄러 시작됨")
            messagebox.showinfo("성공", "스케줄러가 시작되었습니다.")
        else:
            messagebox.showerror("오류", "스케줄러 시작에 실패했습니다. 봇 연결을 확인해주세요.")
    
    def _on_stop_clicked(self):
        """스케줄러 중지 버튼 클릭 이벤트"""
        self.viewmodel.stop_scheduler()
        self._log("스케줄러 중지됨")
        messagebox.showinfo("정보", "스케줄러가 중지되었습니다.")
    
    def _on_remove_clicked(self):
        """메시지 삭제 버튼 클릭 이벤트"""
        selection = self.message_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 메시지를 선택해주세요.")
            return
        
        item = selection[0]
        schedule_id = self.message_tree.item(item, "values")[0]  # 첫 번째 컬럼이 ID라고 가정
        
        if messagebox.askyesno("확인", "선택된 메시지를 삭제하시겠습니까?"):
            self.viewmodel.remove_scheduled_message(int(schedule_id))
            self._log(f"메시지 삭제됨: ID {schedule_id}")
    
    def _on_tree_double_click(self, event):
        """트리뷰 더블클릭 이벤트"""
        selection = self.message_tree.selection()
        if selection:
            item = selection[0]
            values = self.message_tree.item(item, "values")
            messagebox.showinfo("메시지 내용", f"메시지: {values[2]}")
    
    def _on_viewmodel_callback(self, event_type: str, data):
        """ViewModel에서 발생한 이벤트 처리"""
        if event_type == "message_added":
            self._update_message_list()
        elif event_type == "message_removed":
            self._update_message_list()
        elif event_type == "message_sent":
            if data['success']:
                self._log(f"메시지 전송 성공: {data['sent_count']}/{data['total_count']}개 채팅방 - {data['timestamp']}")
                if data['errors']:
                    for error in data['errors']:
                        self._log(f"  오류: {error}")
            else:
                self._log(f"메시지 전송 실패: {data['timestamp']}")
                if data['errors']:
                    for error in data['errors']:
                        self._log(f"  오류: {error}")
        elif event_type == "scheduler_started":
            self._log("스케줄러 시작됨")
        elif event_type == "scheduler_stopped":
            self._log("스케줄러 중지됨")
    
    def _update_chat_id_list(self):
        """채팅방 ID 목록 업데이트"""
        # 기존 항목 삭제
        self.chat_id_listbox.delete(0, tk.END)
        
        # 새 항목 추가
        chat_ids = self.viewmodel.get_chat_ids()
        for chat_id in chat_ids:
            self.chat_id_listbox.insert(tk.END, chat_id)
    
    def _update_message_list(self):
        """메시지 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.message_tree.get_children():
            self.message_tree.delete(item)
        
        # 새 항목 추가
        messages = self.viewmodel.get_scheduled_messages()
        for msg in messages:
            self.message_tree.insert("", "end", values=(
                msg['id'],
                msg['time'],
                msg['interval'],
                msg['message'][:50] + "..." if len(msg['message']) > 50 else msg['message']
            ))
    
    def _log(self, message: str):
        """로그 메시지 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TelegramView()
    app.run()

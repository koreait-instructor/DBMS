import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("학생 명부 관리 시스템")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        
        # 데이터베이스 연결
        self.conn = sqlite3.connect('students.db')
        self.cursor = self.conn.cursor()
        self.create_table()
        
        # UI 생성
        self.create_widgets()
        self.load_data()
    
    def create_table(self):
        """학생 테이블 생성"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                attendance INTEGER DEFAULT 0,
                homework_score INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """UI 구성 요소 생성"""
        # 제목
        title_label = tk.Label(self.root, text="🎓 학생 명부 관리 시스템", 
                              font=("맑은 고딕", 20, "bold"), bg="#4a90e2", fg="white", pady=15)
        title_label.pack(fill=tk.X)
        
        # 입력 프레임
        input_frame = tk.LabelFrame(self.root, text="학생 정보 입력", 
                                   font=("맑은 고딕", 12, "bold"), padx=20, pady=15)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 입력 필드
        fields = [
            ("이름:", "name"),
            ("주소:", "address"),
            ("전화번호:", "phone"),
            ("출석일수:", "attendance"),
            ("과제점수:", "homework_score")
        ]
        
        self.entries = {}
        for idx, (label, field) in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 4
            
            tk.Label(input_frame, text=label, font=("맑은 고딕", 10)).grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=5)
            
            entry = tk.Entry(input_frame, font=("맑은 고딕", 10), width=20)
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            self.entries[field] = entry
        
        # 버튼 프레임
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=8, pady=10)
        
        buttons = [
            ("추가", self.add_student, "#4CAF50"),
            ("수정", self.update_student, "#FFA726"),
            ("삭제", self.delete_student, "#EF5350"),
            ("초기화", self.clear_fields, "#78909C")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(button_frame, text=text, command=command,
                          font=("맑은 고딕", 10, "bold"), bg=color, fg="white",
                          width=10, height=1, relief=tk.RAISED, bd=3)
            btn.pack(side=tk.LEFT, padx=5)
        
        # 검색 프레임
        search_frame = tk.Frame(self.root, padx=20)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="🔍 검색:", font=("맑은 고딕", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("맑은 고딕", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_student())
        
        tk.Button(search_frame, text="전체보기", command=self.load_data,
                 font=("맑은 고딕", 9), bg="#2196F3", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        
        # 테이블 프레임
        table_frame = tk.Frame(self.root, padx=20, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # 트리뷰 (테이블)
        columns = ("ID", "이름", "주소", "전화번호", "출석일수", "과제점수")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=scrollbar_y.set,
                                xscrollcommand=scrollbar_x.set, height=12)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 컬럼 설정
        widths = [50, 120, 250, 130, 100, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self.select_record)
        
        # 통계 프레임
        stats_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=10)
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = tk.Label(stats_frame, text="", font=("맑은 고딕", 10),
                                    bg="#f0f0f0", fg="#333")
        self.stats_label.pack()
        
        self.update_statistics()
    
    def add_student(self):
        """학생 추가"""
        name = self.entries['name'].get().strip()
        
        if not name:
            messagebox.showwarning("입력 오류", "이름을 입력해주세요!")
            return
        
        try:
            attendance = int(self.entries['attendance'].get() or 0)
            homework_score = int(self.entries['homework_score'].get() or 0)
            
            if not (0 <= attendance <= 365):
                raise ValueError("출석일수는 0~365 사이여야 합니다.")
            if not (0 <= homework_score <= 100):
                raise ValueError("과제점수는 0~100 사이여야 합니다.")
            
            self.cursor.execute('''
                INSERT INTO students (name, address, phone, attendance, homework_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, 
                  self.entries['address'].get().strip(),
                  self.entries['phone'].get().strip(),
                  attendance,
                  homework_score))
            
            self.conn.commit()
            messagebox.showinfo("성공", f"'{name}' 학생이 추가되었습니다!")
            self.clear_fields()
            self.load_data()
            
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
    
    def update_student(self):
        """학생 정보 수정"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("선택 오류", "수정할 학생을 선택해주세요!")
            return
        
        student_id = self.tree.item(selected[0])['values'][0]
        name = self.entries['name'].get().strip()
        
        if not name:
            messagebox.showwarning("입력 오류", "이름을 입력해주세요!")
            return
        
        try:
            attendance = int(self.entries['attendance'].get() or 0)
            homework_score = int(self.entries['homework_score'].get() or 0)
            
            if not (0 <= attendance <= 365):
                raise ValueError("출석일수는 0~365 사이여야 합니다.")
            if not (0 <= homework_score <= 100):
                raise ValueError("과제점수는 0~100 사이여야 합니다.")
            
            self.cursor.execute('''
                UPDATE students 
                SET name=?, address=?, phone=?, attendance=?, homework_score=?
                WHERE id=?
            ''', (name,
                  self.entries['address'].get().strip(),
                  self.entries['phone'].get().strip(),
                  attendance,
                  homework_score,
                  student_id))
            
            self.conn.commit()
            messagebox.showinfo("성공", "학생 정보가 수정되었습니다!")
            self.clear_fields()
            self.load_data()
            
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
    
    def delete_student(self):
        """학생 삭제"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("선택 오류", "삭제할 학생을 선택해주세요!")
            return
        
        student_id = self.tree.item(selected[0])['values'][0]
        student_name = self.tree.item(selected[0])['values'][1]
        
        result = messagebox.askyesno("삭제 확인", 
                                     f"'{student_name}' 학생을 삭제하시겠습니까?")
        
        if result:
            self.cursor.execute('DELETE FROM students WHERE id=?', (student_id,))
            self.conn.commit()
            messagebox.showinfo("성공", "학생이 삭제되었습니다!")
            self.clear_fields()
            self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.cursor.execute('SELECT * FROM students ORDER BY name')
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.tree.insert('', tk.END, values=row)
        
        self.update_statistics()
    
    def search_student(self):
        """학생 검색"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.cursor.execute('''
            SELECT * FROM students 
            WHERE name LIKE ? OR address LIKE ? OR phone LIKE ?
            ORDER BY name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.tree.insert('', tk.END, values=row)
        
        self.update_statistics()
    
    def select_record(self, event):
        """레코드 선택 시 입력 필드에 표시"""
        selected = self.tree.selection()
        
        if selected:
            values = self.tree.item(selected[0])['values']
            
            self.entries['name'].delete(0, tk.END)
            self.entries['name'].insert(0, values[1])
            
            self.entries['address'].delete(0, tk.END)
            self.entries['address'].insert(0, values[2])
            
            self.entries['phone'].delete(0, tk.END)
            self.entries['phone'].insert(0, values[3])
            
            self.entries['attendance'].delete(0, tk.END)
            self.entries['attendance'].insert(0, values[4])
            
            self.entries['homework_score'].delete(0, tk.END)
            self.entries['homework_score'].insert(0, values[5])
    
    def clear_fields(self):
        """입력 필드 초기화"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # 선택 해제
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def update_statistics(self):
        """통계 정보 업데이트"""
        self.cursor.execute('SELECT COUNT(*) FROM students')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT AVG(attendance) FROM students')
        avg_attendance = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT AVG(homework_score) FROM students')
        avg_score = self.cursor.fetchone()[0] or 0
        
        self.stats_label.config(
            text=f"📊 총 학생 수: {total}명  |  평균 출석: {avg_attendance:.1f}일  |  평균 과제점수: {avg_score:.1f}점"
        )
    
    def __del__(self):
        """소멸자 - 데이터베이스 연결 종료"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
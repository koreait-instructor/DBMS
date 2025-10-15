#설치패키지(python 3.12.11)
pip install pyinstaller
conda install tk

#가상환경에 실행
python -m PyInstaller --onefile --windowed --name "학생명부관리" .\source\student_management_system.py

#students.db 보기->https://inloop.github.io/sqlite-viewer/
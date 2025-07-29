import os

if False:
    # หาพาธของไฟล์สคริปต์
    script_path = os.path.abspath(__file__)


    # หาพาธของไดเรคทอรีที่ไฟล์สคริปต์อยู่
    script_dir = os.path.dirname(script_path)


    os.chdir(script_dir)
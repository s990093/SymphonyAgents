import sys
import os
import subprocess
from src.music.music_player import MusicPlayer


def check_python_version():
    """檢查 Python 版本是否大於等於 3.11"""
    version = sys.version_info
    if version >= (3, 11):
        print("Python version is 3.11 or above.")
    else:
        print(f"Warning: Python version is {version.major}.{version.minor}. We recommend Python 3.11 or above.")
    
def check_requirements_file():
    """檢查 requirements.txt 檔案是否存在"""
    if os.path.exists('requirements.txt'):
        print("requirements.txt found.")
        return True
    else:
        print("Error: requirements.txt not found.")
        return False

def check_packages_installed():
    """檢查 requirements.txt 中的套件是否已安裝"""
    if check_requirements_file():
        with open('requirements.txt', 'r') as f:
            packages = f.readlines()
        
        for package in packages:
            package_name = package.split('==')[0].strip()  # 取得套件名稱，不包括版本號
            try:
                # 使用 pip 查詢是否安裝該套件
                result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"{package_name} is installed.")
                else:
                    print(f"Warning: {package_name} is not installed.")
            except subprocess.TimeoutExpired:
                print(f"Timeout: {package_name} check took too long.")
            except subprocess.CalledProcessError:
                print(f"Error: Failed to check {package_name}.")
    
if __name__ == "__main__":
    check_python_version()
    check_packages_installed()
    p = MusicPlayer()
    
    

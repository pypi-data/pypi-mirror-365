#!/usr/bin/env python3
"""
PyPIアップロード用スクリプト（Windows環境対応版）
Windows環境でのエンコーディング問題を回避するバージョン
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """必要なツールがインストールされているかチェック"""
    required_tools = ['twine', 'build']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.check_call([sys.executable, "-m", tool, "--help"], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"Missing required tools: {', '.join(missing_tools)}")
        print("Installing missing tools...")
        for tool in missing_tools:
            subprocess.check_call([sys.executable, "-m", "pip", "install", tool])
        print("✓ All required tools installed")
    else:
        print("✓ All required tools are available")

def clean_dist():
    """distフォルダをクリーンアップ"""
    dist_path = Path("dist")
    if dist_path.exists():
        import shutil
        shutil.rmtree(dist_path)
        print("✓ Cleaned dist directory")

def build_package():
    """パッケージをビルド"""
    print("Building package...")
    try:
        subprocess.check_call([sys.executable, "-m", "build"])
        print("✓ Package built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def check_package():
    """パッケージの整合性をチェック"""
    print("Checking package integrity...")
    try:
        subprocess.check_call([sys.executable, "-m", "twine", "check", "dist/*"])
        print("✓ Package integrity check passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package check failed: {e}")
        return False

def setup_environment_variables():
    """環境変数の設定をガイド"""
    print("\n=== Windows環境でのエンコーディング問題対策 ===")
    print("以下の環境変数を設定してください：")
    print()
    print("TestPyPI用:")
    print("  set TWINE_USERNAME=__token__")
    print("  set TWINE_PASSWORD=your-testpypi-api-token")
    print("  set TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/")
    print()
    print("本番PyPI用:")
    print("  set TWINE_USERNAME=__token__")
    print("  set TWINE_PASSWORD=your-pypi-api-token")
    print("  set TWINE_REPOSITORY_URL=https://upload.pypi.org/legacy/")
    print()
    
    choice = input("環境変数を設定しましたか？ (y/n): ")
    return choice.lower() == 'y'

def upload_with_env_vars(repository_url, repository_name):
    """環境変数を使用してアップロード"""
    print(f"Uploading to {repository_name}...")
    
    # 環境変数の確認
    username = os.environ.get('TWINE_USERNAME')
    password = os.environ.get('TWINE_PASSWORD')
    repo_url = os.environ.get('TWINE_REPOSITORY_URL', repository_url)
    
    if not username or not password:
        print("❌ TWINE_USERNAME または TWINE_PASSWORD が設定されていません")
        return False
    
    try:
        # 環境変数を使用してアップロード
        env = os.environ.copy()
        env['TWINE_USERNAME'] = username
        env['TWINE_PASSWORD'] = password
        
        subprocess.check_call([
            sys.executable, "-m", "twine", "upload",
            "--repository-url", repo_url,
            "dist/*"
        ], env=env)
        
        print(f"✓ Successfully uploaded to {repository_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload to {repository_name} failed: {e}")
        return False

def upload_interactive():
    """対話的アップロード（認証情報を手動入力）"""
    print("\n=== 対話的アップロード ===")
    print("ユーザー名とパスワードを手動で入力します")
    
    repository = input("Repository URL (TestPyPI: https://test.pypi.org/legacy/, PyPI: https://upload.pypi.org/legacy/): ")
    if not repository:
        repository = "https://test.pypi.org/legacy/"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "twine", "upload",
            "--repository-url", repository,
            "dist/*"
        ])
        print("✓ Successfully uploaded")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    """メイン処理"""
    print("=== PyPI Upload Tool for tree-sitter-analyzer (Windows対応版) ===")
    
    # 必要なツールをチェック
    check_requirements()
    
    # distフォルダをクリーンアップ
    clean_dist()
    
    # パッケージをビルド
    if not build_package():
        sys.exit(1)
    
    # パッケージの整合性をチェック
    if not check_package():
        sys.exit(1)
    
    print("\n=== アップロード方法の選択 ===")
    print("1. 環境変数を使用してTestPyPIにアップロード")
    print("2. 環境変数を使用して本番PyPIにアップロード")
    print("3. 対話的アップロード（手動入力）")
    print("4. 終了")
    
    choice = input("選択してください (1-4): ")
    
    if choice == "1":
        if setup_environment_variables():
            upload_with_env_vars("https://test.pypi.org/legacy/", "TestPyPI")
        else:
            print("環境変数を設定してから再実行してください")
    elif choice == "2":
        if setup_environment_variables():
            confirm = input("本番PyPIにアップロードしますか？ (yes/no): ")
            if confirm.lower() == 'yes':
                upload_with_env_vars("https://upload.pypi.org/legacy/", "PyPI")
            else:
                print("アップロードをキャンセルしました")
        else:
            print("環境変数を設定してから再実行してください")
    elif choice == "3":
        upload_interactive()
    elif choice == "4":
        print("終了します...")
    else:
        print("無効な選択です")
        sys.exit(1)

if __name__ == "__main__":
    main()
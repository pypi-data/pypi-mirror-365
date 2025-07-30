# Windows環境でのPyPIアップロードガイド

Windows環境でのエンコーディング問題を解決してPyPIにアップロードする方法

## 問題の概要

Windows環境で`python -m twine upload dist/*`を実行すると、以下のエラーが発生することがあります：

```
UnicodeDecodeError: 'cp932' codec can't decode byte 0x85 in position 13: illegal multibyte sequence
```

これは`.pypirc`ファイルの文字エンコーディングが原因です。

## 解決方法

### 方法1: 環境変数を使用（推奨）

```cmd
# TestPyPI用の環境変数設定
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=your-testpypi-api-token

# TestPyPIにアップロード
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 本番PyPI用の環境変数設定
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=your-pypi-api-token

# 本番PyPIにアップロード
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

### 方法2: Windows対応スクリプトを使用

```cmd
python upload_to_pypi_windows_fix.py
```

このスクリプトは以下の機能を提供します：
- 環境変数の設定ガイド
- 対話的アップロード
- エラーハンドリング

### 方法3: 対話的アップロード

```cmd
# 認証情報を手動で入力
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

実行時にユーザー名とパスワードの入力を求められます。

## API トークンの取得

### TestPyPI
1. [TestPyPI](https://test.pypi.org/account/register/) でアカウント作成
2. Account settings → API tokens → Add API token
3. トークンをコピーして環境変数に設定

### 本番PyPI
1. [PyPI](https://pypi.org/account/register/) でアカウント作成
2. Account settings → API tokens → Add API token
3. トークンをコピーして環境変数に設定

## 完全なアップロード手順

```cmd
# 1. パッケージをビルド
python -m build

# 2. パッケージをチェック
python -m twine check dist/*

# 3. 環境変数を設定
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=your-api-token

# 4. TestPyPIにアップロード（テスト）
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 5. TestPyPIからインストールテスト
pip install --index-url https://test.pypi.org/simple/ tree-sitter-analyzer

# 6. 本番PyPIにアップロード
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

## 確認

アップロード後、以下でインストールできることを確認：

```cmd
# TestPyPIから
pip install --index-url https://test.pypi.org/simple/ tree-sitter-analyzer

# 本番PyPIから
pip install tree-sitter-analyzer
```

## トラブルシューティング

### 認証エラー
- API トークンが正しいか確認
- 環境変数が正しく設定されているか確認

### ネットワークエラー
- インターネット接続を確認
- プロキシ設定が必要な場合は設定

### パッケージエラー
- `python -m twine check dist/*` でパッケージの整合性を確認
- `pyproject.toml` の設定を確認
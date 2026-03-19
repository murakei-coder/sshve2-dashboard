# SSHVE2 Dashboard - クイックスタートガイド

みんながアクセスできるWebアプリとして起動する最も簡単な方法を説明します。

## 🚀 最速デプロイ（3ステップ）

### ステップ1: 依存パッケージをインストール

```bash
pip install -r requirements_production.txt
```

### ステップ2: データファイルを配置

プロジェクトルートに以下のファイルを配置：
- `sshve2_data_new_suppression_20260318_222020.json`

### ステップ3: 起動

**Linux/Mac:**
```bash
chmod +x start_production.sh
./start_production.sh
```

**Windows:**
```cmd
start_production.bat
```

**Docker:**
```bash
docker-compose up -d
```

## 🌐 アクセス方法

起動後、以下のURLでアクセスできます：

- **ローカル**: http://localhost:8000
- **社内ネットワーク**: http://YOUR_SERVER_IP:8000
- **使い方ガイド**: http://YOUR_SERVER_IP:8000/guide

## 📝 YOUR_SERVER_IPの確認方法

**Linux/Mac:**
```bash
# 内部IP
hostname -I
# または
ip addr show

# 外部IP（インターネット経由でアクセスする場合）
curl ifconfig.me
```

**Windows:**
```cmd
ipconfig
```

## 🔧 設定変更が必要な場合

### データファイルのパスを変更

`src/sshve2_dashboard_web_app.py` の52-53行目を編集：

```python
json_file = 'あなたのJSONファイルのパス'
suppression_file = r'あなたのSuppressionファイルのパス'
```

### ポート番号を変更

`gunicorn_config.py` の5行目を編集：

```python
bind = "0.0.0.0:8001"  # 8000から8001に変更
```

## 🛑 停止方法

**Linux/Mac:**
```bash
# Ctrl+C を押す
# または
pkill -f gunicorn
```

**Windows:**
```cmd
# Ctrl+C を押す
```

**Docker:**
```bash
docker-compose down
```

## ❓ トラブルシューティング

### データが読み込まれない
→ ファイルパスを確認してください

### ポートが使用中
→ `gunicorn_config.py` でポート番号を変更してください

### アクセスできない
→ ファイアウォールを確認してください

## 📚 詳細情報

詳しいデプロイ方法は `DEPLOYMENT_GUIDE.md` を参照してください。

---

**最終更新**: 2026年3月19日

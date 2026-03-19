# SSHVE2 Dashboard - 本番環境デプロイメントガイド

このガイドでは、SSHVE2 Dashboardを本番環境にデプロイする方法を説明します。

## 📋 目次

1. [デプロイメント方法の選択](#デプロイメント方法の選択)
2. [方法1: Linux/Mac サーバー（推奨）](#方法1-linuxmac-サーバー推奨)
3. [方法2: Windows サーバー](#方法2-windows-サーバー)
4. [方法3: Docker（最も簡単）](#方法3-docker最も簡単)
5. [方法4: AWS EC2](#方法4-aws-ec2)
6. [トラブルシューティング](#トラブルシューティング)

---

## デプロイメント方法の選択

| 方法 | 難易度 | 推奨環境 | メリット |
|------|--------|----------|----------|
| Docker | ⭐ 簡単 | どこでも | 環境構築不要、移植性高い |
| Linux/Mac | ⭐⭐ 普通 | Linux/Mac | 柔軟性高い、パフォーマンス良い |
| Windows | ⭐⭐ 普通 | Windows | 既存Windows環境で動く |
| AWS EC2 | ⭐⭐⭐ やや難 | クラウド | スケーラブル、高可用性 |

---

## 方法1: Linux/Mac サーバー（推奨）

### 前提条件
- Python 3.7以上
- pip
- 管理者権限（sudo）

### ステップ1: 環境準備

```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/your/project

# 2. 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements_production.txt

# 4. ログディレクトリを作成
mkdir -p logs
```

### ステップ2: データファイルの配置

```bash
# JSONデータファイルをプロジェクトルートに配置
cp /path/to/sshve2_data_new_suppression_20260318_222020.json .

# Suppressionデータファイルのパスを確認
# src/sshve2_dashboard_web_app.py の suppression_file 変数を環境に合わせて修正
```

### ステップ3: 起動スクリプトに実行権限を付与

```bash
chmod +x start_production.sh
```

### ステップ4: アプリケーションを起動

```bash
./start_production.sh
```

アクセスURL: `http://YOUR_SERVER_IP:8000`

### ステップ5: Nginxでリバースプロキシを設定（オプション、推奨）

```bash
# 1. Nginxをインストール
sudo apt-get update
sudo apt-get install nginx

# 2. 設定ファイルをコピー
sudo cp nginx.conf /etc/nginx/sites-available/sshve2-dashboard

# 3. YOUR_DOMAIN_OR_IP を実際のドメインまたはIPに置換
sudo nano /etc/nginx/sites-available/sshve2-dashboard

# 4. シンボリックリンクを作成
sudo ln -s /etc/nginx/sites-available/sshve2-dashboard /etc/nginx/sites-enabled/

# 5. Nginxの設定をテスト
sudo nginx -t

# 6. Nginxを再起動
sudo systemctl restart nginx
```

アクセスURL: `http://YOUR_DOMAIN_OR_IP`（ポート80）

### ステップ6: Systemdサービスとして登録（オプション、推奨）

```bash
# 1. サービスファイルを編集
nano systemd_service.txt
# YOUR_USERNAME, YOUR_GROUP, /path/to/your/app を実際の値に置換

# 2. サービスファイルをコピー
sudo cp systemd_service.txt /etc/systemd/system/sshve2-dashboard.service

# 3. サービスを有効化
sudo systemctl daemon-reload
sudo systemctl enable sshve2-dashboard
sudo systemctl start sshve2-dashboard

# 4. ステータス確認
sudo systemctl status sshve2-dashboard
```

これで、サーバー起動時に自動的にアプリケーションが起動します。

---

## 方法2: Windows サーバー

### 前提条件
- Python 3.7以上
- pip

### ステップ1: 環境準備

```cmd
REM 1. プロジェクトディレクトリに移動
cd C:\path\to\your\project

REM 2. 仮想環境を作成
python -m venv venv
venv\Scripts\activate

REM 3. 依存パッケージをインストール
pip install -r requirements_production.txt
pip install waitress

REM 4. ログディレクトリを作成
mkdir logs
```

### ステップ2: データファイルの配置

```cmd
REM JSONデータファイルをプロジェクトルートに配置
copy C:\path\to\sshve2_data_new_suppression_20260318_222020.json .

REM src\sshve2_dashboard_web_app.py の suppression_file 変数を環境に合わせて修正
```

### ステップ3: アプリケーションを起動

```cmd
start_production.bat
```

アクセスURL: `http://YOUR_SERVER_IP:8000`

### ステップ4: Windowsサービスとして登録（オプション）

NSSM（Non-Sucking Service Manager）を使用：

```cmd
REM 1. NSSMをダウンロード
REM https://nssm.cc/download

REM 2. NSSMでサービスを作成
nssm install SSHVE2Dashboard "C:\path\to\your\project\venv\Scripts\python.exe" "C:\path\to\your\project\wsgi.py"

REM 3. サービスを開始
nssm start SSHVE2Dashboard
```

---

## 方法3: Docker（最も簡単）

### 前提条件
- Docker
- Docker Compose

### ステップ1: データファイルの配置

```bash
# JSONデータファイルをプロジェクトルートに配置
cp /path/to/sshve2_data_new_suppression_20260318_222020.json .
```

### ステップ2: Dockerイメージをビルド

```bash
docker-compose build
```

### ステップ3: コンテナを起動

```bash
docker-compose up -d
```

アクセスURL: `http://YOUR_SERVER_IP:8000`

### ステップ4: ログを確認

```bash
docker-compose logs -f
```

### ステップ5: コンテナを停止

```bash
docker-compose down
```

---

## 方法4: AWS EC2

### ステップ1: EC2インスタンスを作成

1. AWS Management Consoleにログイン
2. EC2 > インスタンスを起動
3. Amazon Linux 2 または Ubuntu を選択
4. インスタンスタイプ: t3.medium 以上を推奨
5. セキュリティグループ:
   - SSH (22): 自分のIPのみ
   - HTTP (80): 0.0.0.0/0
   - Custom TCP (8000): 0.0.0.0/0（テスト用、本番ではNginx経由を推奨）

### ステップ2: インスタンスに接続

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### ステップ3: 環境をセットアップ

```bash
# システムを更新
sudo yum update -y  # Amazon Linux
# または
sudo apt-get update && sudo apt-get upgrade -y  # Ubuntu

# Python 3とpipをインストール
sudo yum install python3 python3-pip git -y  # Amazon Linux
# または
sudo apt-get install python3 python3-pip git -y  # Ubuntu

# プロジェクトをクローンまたはアップロード
git clone YOUR_REPO_URL
# または
scp -i your-key.pem -r /local/path ec2-user@YOUR_EC2_PUBLIC_IP:/home/ec2-user/
```

### ステップ4: 方法1（Linux/Mac サーバー）の手順に従う

上記の「方法1: Linux/Mac サーバー」のステップ1〜6を実行してください。

### ステップ5: Elastic IPを割り当て（オプション、推奨）

1. EC2 > Elastic IP > Elastic IPアドレスを割り当て
2. 作成したElastic IPをインスタンスに関連付け

これで、固定IPでアクセスできるようになります。

---

## データファイルのパス設定

`src/sshve2_dashboard_web_app.py` の以下の行を環境に合わせて修正してください：

```python
# Line 52-53
json_file = 'sshve2_data_new_suppression_20260318_222020.json'
suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
```

### 推奨設定

本番環境では、環境変数を使用することを推奨します：

```python
import os

json_file = os.getenv('SSHVE2_JSON_FILE', 'sshve2_data_new_suppression_20260318_222020.json')
suppression_file = os.getenv('SSHVE2_SUPPRESSION_FILE', '/path/to/suppression/file.txt')
```

---

## セキュリティ設定

### 1. ファイアウォール設定

```bash
# UFW（Ubuntu）
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw enable

# firewalld（CentOS/RHEL）
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2. HTTPS設定（推奨）

Let's Encryptで無料SSL証明書を取得：

```bash
# Certbotをインストール
sudo apt-get install certbot python3-certbot-nginx -y

# SSL証明書を取得
sudo certbot --nginx -d your-domain.com

# 自動更新を設定
sudo certbot renew --dry-run
```

### 3. 基本認証（オプション）

Nginxで基本認証を設定：

```bash
# パスワードファイルを作成
sudo apt-get install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd username

# nginx.confに追加
# location / {
#     auth_basic "Restricted Access";
#     auth_basic_user_file /etc/nginx/.htpasswd;
#     ...
# }
```

---

## モニタリング

### ログの確認

```bash
# Gunicornログ
tail -f logs/access.log
tail -f logs/error.log

# Nginxログ
sudo tail -f /var/log/nginx/sshve2_dashboard_access.log
sudo tail -f /var/log/nginx/sshve2_dashboard_error.log

# Systemdログ
sudo journalctl -u sshve2-dashboard -f
```

### ヘルスチェック

```bash
# アプリケーションの状態確認
curl http://localhost:8000/

# プロセス確認
ps aux | grep gunicorn
```

---

## トラブルシューティング

### 問題1: データが読み込まれない

**原因**: ファイルパスが間違っている

**解決策**:
```bash
# ファイルの存在を確認
ls -la sshve2_data_new_suppression_20260318_222020.json
ls -la /path/to/suppression/file.txt

# パスを修正
nano src/sshve2_dashboard_web_app.py
```

### 問題2: ポート8000が使用中

**原因**: 別のプロセスがポートを使用している

**解決策**:
```bash
# ポートを使用しているプロセスを確認
sudo lsof -i :8000
# または
sudo netstat -tulpn | grep 8000

# プロセスを終了
sudo kill -9 PID

# または gunicorn_config.py でポートを変更
bind = "0.0.0.0:8001"
```

### 問題3: Permission denied

**原因**: ファイルやディレクトリの権限が不足

**解決策**:
```bash
# 権限を確認
ls -la

# 権限を修正
chmod +x start_production.sh
chmod -R 755 logs/
```

### 問題4: Gunicornが起動しない（Windows）

**原因**: GunicornはWindowsで動作しない

**解決策**:
```cmd
REM Waitressを使用
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 wsgi:application
```

### 問題5: メモリ不足

**原因**: データファイルが大きすぎる

**解決策**:
```bash
# ワーカー数を減らす（gunicorn_config.py）
workers = 2  # デフォルトは4

# または、サーバーのメモリを増やす
```

---

## パフォーマンスチューニング

### 1. ワーカー数の最適化

```python
# gunicorn_config.py
# 推奨: (2 x CPU cores) + 1
workers = 5  # 2コアの場合
```

### 2. キャッシュの有効化

Nginxでキャッシュを設定：

```nginx
# nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    ...
}
```

### 3. データの事前読み込み

アプリケーション起動時にデータを読み込むため、初回アクセスが高速化されます。

---

## バックアップ

### データファイルのバックアップ

```bash
# 定期的にバックアップ
cp sshve2_data_new_suppression_20260318_222020.json backup/sshve2_data_$(date +%Y%m%d).json

# cronで自動化
crontab -e
# 毎日午前2時にバックアップ
0 2 * * * cp /path/to/sshve2_data_new_suppression_20260318_222020.json /path/to/backup/sshve2_data_$(date +\%Y\%m\%d).json
```

---

## アップデート手順

```bash
# 1. アプリケーションを停止
sudo systemctl stop sshve2-dashboard
# または
docker-compose down

# 2. コードを更新
git pull
# または新しいファイルをアップロード

# 3. 依存パッケージを更新
pip install -r requirements_production.txt

# 4. アプリケーションを再起動
sudo systemctl start sshve2-dashboard
# または
docker-compose up -d
```

---

## サポート

問題が解決しない場合は、以下の情報を含めて管理者に連絡してください：

1. エラーメッセージ（ログファイルから）
2. 実行環境（OS、Pythonバージョン等）
3. 実行したコマンド
4. 期待される動作と実際の動作

---

**最終更新**: 2026年3月19日

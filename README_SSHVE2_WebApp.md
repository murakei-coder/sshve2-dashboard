# SSHVE2 Opportunity Dashboard - Webアプリ版

## 概要

SSHVE2 Opportunity DashboardのWebアプリケーション版です。**みんながブラウザでアクセスできる**本番環境対応版です。

## 🌟 主な特徴

- ✅ **みんながアクセス可能**: 社内サーバーやクラウドにデプロイして、URLを共有するだけ
- ✅ **HTMLファイル不要**: ブラウザでURLにアクセスするだけで使用可能
- ✅ **ASIN単位のCSVダウンロード**: 各セラーのASINデータを直接ダウンロード
- ✅ **本番環境対応**: Gunicorn + Nginx で安定稼働
- ✅ **Docker対応**: コンテナで簡単デプロイ
- ✅ **使い方ガイド統合**: `/guide` でアクセス可能

## 🚀 クイックスタート

### 最速デプロイ（3ステップ）

```bash
# 1. 依存パッケージをインストール
pip install -r requirements_production.txt

# 2. データファイルを配置
# sshve2_data_new_suppression_20260318_222020.json をプロジェクトルートに配置

# 3. 起動
./start_production.sh  # Linux/Mac
# または
start_production.bat   # Windows
# または
docker-compose up -d   # Docker
```

### アクセス

- **ダッシュボード**: http://YOUR_SERVER_IP:8000
- **使い方ガイド**: http://YOUR_SERVER_IP:8000/guide

詳細は `QUICKSTART.md` を参照してください。

## 📚 ドキュメント

- **[QUICKSTART.md](QUICKSTART.md)** - 最速で起動する方法（初心者向け）
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - 詳細なデプロイメント手順（全環境対応）
- **[README_SSHVE2_Dashboard.md](README_SSHVE2_Dashboard.md)** - 機能説明と使い方

## 🎯 主な機能

### 1. フィルター機能
- Team / Mgr / Alias / MCID / Merchant Name で絞り込み
- カスケード型フィルター（階層的に絞り込み）

### 2. ASIN単位のCSVダウンロード
各セラーの行から直接ダウンロード可能：
- **📥 All**: 全ASINのデータ
- **📥 Sourcing**: Sourcing対象ASIN（SSHVE2 Sourced = Y）
- **📥 Suppression**: Suppression対象ASIN（No suppression以外）

### 3. 改善シミュレーション
- Sourcing改善幅の入力
- OOS改善率、Price Error削減率、その他Suppression削減率の入力
- Projected OPSの自動計算

### 4. Action Focus
各セラーの推奨アクションを自動判定：
- 🎯 Sourcing: Sourcing施策が必要
- 🔧 Suppression: Suppression施策が必要
- 📊 Both: 両方の施策が必要
- ✅ Maintain: 現状維持でOK

## 🏗️ デプロイメント方法

### 方法1: Linux/Mac サーバー（推奨）

```bash
# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements_production.txt

# 起動
./start_production.sh
```

### 方法2: Windows サーバー

```cmd
REM 仮想環境を作成
python -m venv venv
venv\Scripts\activate

REM 依存パッケージをインストール
pip install -r requirements_production.txt

REM 起動
start_production.bat
```

### 方法3: Docker（最も簡単）

```bash
# ビルドして起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

### 方法4: AWS EC2 / クラウド

詳細は `DEPLOYMENT_GUIDE.md` の「方法4: AWS EC2」を参照してください。

## 🔧 設定

### データファイルのパス

`src/sshve2_dashboard_web_app.py` の52-53行目を環境に合わせて修正：

```python
json_file = 'sshve2_data_new_suppression_20260318_222020.json'
suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
```

### ポート番号の変更

`gunicorn_config.py` の5行目を編集：

```python
bind = "0.0.0.0:8000"  # 任意のポート番号に変更可能
```

## 📊 システム要件

### 最小要件
- Python 3.7以上
- メモリ: 2GB以上
- ディスク: 1GB以上

### 推奨要件
- Python 3.9以上
- メモリ: 4GB以上
- ディスク: 5GB以上
- CPU: 2コア以上

## 🔒 セキュリティ

### 本番環境での推奨設定

1. **Nginxでリバースプロキシ**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/sshve2-dashboard
   sudo ln -s /etc/nginx/sites-available/sshve2-dashboard /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

2. **HTTPS設定（Let's Encrypt）**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **基本認証**
   ```bash
   sudo htpasswd -c /etc/nginx/.htpasswd username
   ```

詳細は `DEPLOYMENT_GUIDE.md` の「セキュリティ設定」を参照してください。

## 📁 ファイル構成

```
.
├── src/
│   └── sshve2_dashboard_web_app.py  # メインアプリケーション
├── templates/
│   ├── sshve2_dashboard.html        # ダッシュボードHTML
│   └── sshve2_guide.html            # 使い方ガイドHTML
├── wsgi.py                          # WSGI エントリーポイント
├── gunicorn_config.py               # Gunicorn設定
├── requirements_production.txt      # 本番環境用依存パッケージ
├── start_production.sh              # Linux/Mac起動スクリプト
├── start_production.bat             # Windows起動スクリプト
├── Dockerfile                       # Docker設定
├── docker-compose.yml               # Docker Compose設定
├── nginx.conf                       # Nginx設定例
├── systemd_service.txt              # Systemdサービス設定例
├── QUICKSTART.md                    # クイックスタートガイド
├── DEPLOYMENT_GUIDE.md              # 詳細デプロイメントガイド
└── README_SSHVE2_WebApp.md          # このファイル
```

## 🛠️ トラブルシューティング

### データが読み込まれない
→ ファイルパスを確認してください

### ポート8000が使用中
→ `gunicorn_config.py` でポート番号を変更してください

### Permission denied
→ `chmod +x start_production.sh` を実行してください

### アクセスできない
→ ファイアウォール設定を確認してください

詳細は `DEPLOYMENT_GUIDE.md` の「トラブルシューティング」を参照してください。

## 📈 パフォーマンス

### ベンチマーク（参考値）

- **同時接続数**: 100ユーザーまで対応
- **レスポンスタイム**: 平均 < 500ms
- **メモリ使用量**: 約 500MB（ワーカー4つの場合）

### チューニング

ワーカー数を調整（`gunicorn_config.py`）：

```python
# 推奨: (2 x CPU cores) + 1
workers = 5  # 2コアの場合
```

## 🔄 アップデート

```bash
# 1. アプリケーションを停止
sudo systemctl stop sshve2-dashboard

# 2. コードを更新
git pull

# 3. 依存パッケージを更新
pip install -r requirements_production.txt

# 4. 再起動
sudo systemctl start sshve2-dashboard
```

## 📞 サポート

質問や不具合がある場合は、以下の情報を含めて管理者に連絡してください：

1. エラーメッセージ（ログファイルから）
2. 実行環境（OS、Pythonバージョン等）
3. 実行したコマンド
4. 期待される動作と実際の動作

## 📝 変更履歴

### v2.0.0 (2026-03-19)
- 本番環境対応版リリース
- Gunicorn + Nginx対応
- Docker対応
- ASIN単位のCSVダウンロード機能追加
- 使い方ガイド統合

### v1.0.0 (2026-03-18)
- 初回リリース（開発版）

---

**最終更新**: 2026年3月19日

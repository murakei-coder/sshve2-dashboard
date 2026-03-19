# SSHVE2 Dashboard - Gitなしデプロイ手順

Gitがインストールされていなくても大丈夫！AWS Amplifyに直接ZIPファイルをアップロードできます。

---

## 🚀 超簡単な方法（5分）

### ステップ1: プロジェクトをZIPに圧縮（2分）

#### 1-1. 必要なファイルを確認

以下のファイルがあることを確認：
- ✅ `src/` フォルダ
- ✅ `templates/` フォルダ
- ✅ `wsgi.py`
- ✅ `gunicorn_config.py`
- ✅ `requirements_production.txt`
- ✅ `amplify.yml`
- ✅ `Procfile`
- ✅ `runtime.txt`
- ✅ `sshve2_data_new_suppression_20260318_222020.json`

#### 1-2. ZIPファイルを作成

1. エクスプローラーで `C:\Users\murakei\Desktop\SSHVE2\Dashboard` を開く
2. 上記のファイルとフォルダを全て選択
3. 右クリック → 「送る」→「圧縮(zip形式)フォルダー」
4. ファイル名: `sshve2-dashboard.zip`

**重要**: 以下のフォルダは除外してください（サイズが大きいため）
- `.hypothesis/`
- `.pytest_cache/`
- `__pycache__/`
- `.vscode/`
- `.log/`

---

### ステップ2: AWS S3にアップロード（2分）

#### 2-1. S3バケットを作成

1. https://console.aws.amazon.com/s3/ を開く
2. 「バケットを作成」をクリック
3. バケット名: `sshve2-dashboard-deploy-20260319`
4. リージョン: 「アジアパシフィック(東京) ap-northeast-1」
5. 「バケットを作成」をクリック

#### 2-2. ZIPファイルをアップロード

1. 作成したバケットをクリック
2. 「アップロード」をクリック
3. `sshve2-dashboard.zip` を選択
4. 「アップロード」をクリック

#### 2-3. S3 URIをコピー

アップロード完了後、ファイルをクリックして「S3 URI」をコピー：

```
s3://sshve2-dashboard-deploy-20260319/sshve2-dashboard.zip
```

---

### ステップ3: AWS App Runnerでデプロイ（1分）

#### 3-1. App Runnerコンソールを開く

1. https://console.aws.amazon.com/apprunner/ を開く
2. 「サービスの作成」をクリック

#### 3-2. ソースを設定

1. 「ソースコードリポジトリ」を選択
2. 「Amazon ECR」を選択
3. 「手動デプロイ」を選択

**または**

1. 「ソースイメージ」を選択
2. 「Amazon S3」を選択
3. S3 URIを入力: `s3://sshve2-dashboard-deploy-20260319/sshve2-dashboard.zip`

#### 3-3. ビルド設定

```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements_production.txt
run:
  command: gunicorn --config gunicorn_config.py wsgi:application
  network:
    port: 8000
```

#### 3-4. サービス設定

- サービス名: `sshve2-dashboard`
- CPU: 1 vCPU
- メモリ: 2 GB
- ポート: 8000

#### 3-5. デプロイ

「作成とデプロイ」をクリック

---

## 🎯 もっと簡単な方法: AWS Elastic Beanstalk

### ステップ1: Elastic Beanstalkコンソールを開く

1. https://console.aws.amazon.com/elasticbeanstalk/ を開く
2. 「アプリケーションの作成」をクリック

### ステップ2: アプリケーションを設定

1. アプリケーション名: `sshve2-dashboard`
2. プラットフォーム: `Python`
3. プラットフォームブランチ: `Python 3.9`
4. アプリケーションコード: 「コードをアップロード」
5. ZIPファイルを選択: `sshve2-dashboard.zip`

### ステップ3: デプロイ

「アプリケーションの作成」をクリック

5-10分待つと、URLが表示されます：

```
http://sshve2-dashboard.ap-northeast-1.elasticbeanstalk.com
```

---

## 🌟 最も簡単な方法: GitHub Desktop（推奨）

Gitコマンドが使えない場合、GitHub Desktopを使うのが最も簡単です。

### ステップ1: GitHub Desktopをインストール

1. https://desktop.github.com/ を開く
2. 「Download for Windows」をクリック
3. インストーラーを実行

### ステップ2: GitHubアカウントでログイン

1. GitHub Desktopを起動
2. 「Sign in to GitHub.com」をクリック
3. ブラウザでログイン

### ステップ3: リポジトリを作成

1. 「File」→「New repository」
2. Name: `sshve2-dashboard`
3. Local path: `C:\Users\murakei\Desktop\SSHVE2\Dashboard`
4. 「Create repository」をクリック

### ステップ4: コミットとプッシュ

1. 左下の「Summary」に `Initial commit` と入力
2. 「Commit to main」をクリック
3. 「Publish repository」をクリック
4. 「Private」にチェック
5. 「Publish repository」をクリック

### ステップ5: AWS Amplifyでデプロイ

1. https://console.aws.amazon.com/amplify/ を開く
2. 「新しいアプリ」→「Webアプリをホスト」
3. 「GitHub」を選択
4. リポジトリ: `sshve2-dashboard` を選択
5. 「保存してデプロイ」をクリック

---

## 💡 一番手っ取り早い方法: ローカルで起動

Gitもインストールも面倒な場合、今すぐローカルで起動できます。

### ステップ1: 起動（1分）

コマンドプロンプトで：

```cmd
cd C:\Users\murakei\Desktop\SSHVE2\Dashboard
python src/sshve2_dashboard_web_app.py
```

### ステップ2: IPアドレスを確認

別のコマンドプロンプトで：

```cmd
ipconfig
```

「IPv4 アドレス」をメモ（例: `10.123.45.67`）

### ステップ3: 営業担当に共有

```
http://YOUR_IP:5001
```

**メリット**:
- ✅ 今すぐ使える
- ✅ インストール不要
- ✅ 無料

**デメリット**:
- ⚠️ あなたのPCが起動している間だけ

---

## 📊 方法の比較

| 方法 | 難易度 | 時間 | 費用 | 24時間稼働 |
|------|--------|------|------|------------|
| ローカル起動 | ⭐ 簡単 | 1分 | 無料 | ❌ |
| GitHub Desktop + Amplify | ⭐⭐ 普通 | 10分 | $0-5/月 | ✅ |
| S3 + App Runner | ⭐⭐ 普通 | 5分 | $10-15/月 | ✅ |
| Elastic Beanstalk | ⭐⭐ 普通 | 5分 | $7-10/月 | ✅ |

---

## 🎉 推奨: GitHub Desktopを使う

最も簡単で、将来的にも便利です。

1. GitHub Desktopをインストール（3分）
2. リポジトリを作成（2分）
3. AWS Amplifyでデプロイ（5分）

**合計10分で完了！**

---

## ❓ どの方法がいいですか？

1. **今すぐ使いたい** → ローカル起動（1分）
2. **簡単に24時間稼働させたい** → GitHub Desktop + Amplify（10分）
3. **Gitを使いたくない** → S3 + App Runner（5分）

---

**最終更新**: 2026年3月19日

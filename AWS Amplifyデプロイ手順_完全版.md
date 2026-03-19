# SSHVE2 Dashboard - AWS Amplifyデプロイ手順（完全版）

24時間稼働するWebアプリを10分で作ります。

---

## 📋 ステップ1: GitHub Desktopをインストール（5分）

### 1-1. ダウンロード

1. ブラウザで https://desktop.github.com/ を開く
2. 「Download for Windows」をクリック
3. ダウンロードした `GitHubDesktopSetup.exe` を実行

### 1-2. インストール

1. インストーラーが自動的に進む（待つだけ）
2. 完了したら「Finish」をクリック

### 1-3. GitHubアカウントでログイン

1. GitHub Desktopが起動
2. 「Sign in to GitHub.com」をクリック
3. ブラウザが開く
4. GitHubアカウントでログイン（アカウントがない場合は作成）
5. 「Authorize desktop」をクリック
6. GitHub Desktopに戻る

---

## 📋 ステップ2: リポジトリを作成（2分）

### 2-1. 新しいリポジトリを作成

1. GitHub Desktopで「File」→「Add local repository」をクリック
2. 「Choose...」をクリック
3. `C:\Users\murakei\.aki` を選択
4. 「Add repository」をクリック

**エラーが出た場合:**
1. 「create a repository」をクリック
2. Name: `sshve2-dashboard`
3. Local path: `C:\Users\murakei\.aki`
4. 「Create repository」をクリック

### 2-2. 初回コミット

1. 左下の「Summary」に `Initial commit: SSHVE2 Dashboard` と入力
2. 「Commit to main」をクリック

### 2-3. GitHubにプッシュ

1. 「Publish repository」をクリック
2. 「Keep this code private」にチェック（重要！）
3. 「Publish repository」をクリック
4. 完了を待つ（1-2分）

---

## 📋 ステップ3: AWS Amplifyでデプロイ（3分）

### 3-1. Amplifyコンソールを開く

1. ブラウザで https://console.aws.amazon.com/amplify/ を開く
2. 右上のリージョンが「東京（ap-northeast-1）」になっているか確認

### 3-2. 新しいアプリを作成

1. 「新しいアプリ」ボタンをクリック
2. 「Webアプリをホスト」を選択
3. 「GitHub」を選択
4. 「次へ」をクリック

### 3-3. GitHubを接続

1. 「GitHubに接続」をクリック
2. ブラウザでGitHubの認証画面が開く
3. 「Authorize AWS Amplify」をクリック
4. パスワードを入力（必要な場合）

### 3-4. リポジトリを選択

1. リポジトリ: `sshve2-dashboard` を選択
2. ブランチ: `main` を選択
3. 「次へ」をクリック

### 3-5. ビルド設定を確認

以下の設定が自動的に検出されます：

```yaml
version: 1
backend:
  phases:
    build:
      commands:
        - pip3 install -r requirements_production.txt
frontend:
  phases:
    preBuild:
      commands:
        - echo "Starting SSHVE2 Dashboard build..."
    build:
      commands:
        - echo "Build completed"
  artifacts:
    baseDirectory: /
    files:
      - '**/*'
```

「次へ」をクリック

### 3-6. アプリ名を設定

1. アプリ名: `sshve2-dashboard`
2. 環境名: `production`
3. 「次へ」をクリック

### 3-7. デプロイ開始

1. 設定を確認
2. 「保存してデプロイ」をクリック
3. 5-10分待つ

---

## 📋 ステップ4: デプロイ完了を確認（1分）

### 4-1. デプロイステータスを確認

Amplifyコンソールで以下のステータスが表示されます：

1. ✅ プロビジョン
2. ✅ ビルド
3. ✅ デプロイ
4. ✅ 検証

全て緑色のチェックマークになれば完了！

### 4-2. URLを取得

デプロイ完了後、以下のようなURLが表示されます：

```
https://main.xxxxxxxxxxxxx.amplifyapp.com
```

このURLをコピーしてください。

---

## 📋 ステップ5: 動作確認（1分）

### 5-1. ブラウザでアクセス

```
https://main.xxxxxxxxxxxxx.amplifyapp.com
```

ダッシュボードが表示されればOK！

### 5-2. 使い方ガイドを確認

```
https://main.xxxxxxxxxxxxx.amplifyapp.com/guide
```

---

## 📋 ステップ6: 営業担当にURLを共有（1分）

以下のメールを送信：

```
件名: SSHVE2 Opportunity Dashboard - アクセス方法

営業担当 各位

お世話になっております。
SSHVE2 Opportunity Dashboardが利用可能になりました。

【アクセスURL】
https://main.xxxxxxxxxxxxx.amplifyapp.com

【使い方ガイド】
https://main.xxxxxxxxxxxxx.amplifyapp.com/guide

【注意事項】
- ブラウザはChrome、Edge、Safari推奨
- 何もインストール不要、URLを開くだけで使えます
- 24時間いつでも利用可能です

ご不明点があればご連絡ください。
```

---

## ❓ トラブルシューティング

### Q1: ビルドが失敗する

**エラー**: `ModuleNotFoundError: No module named 'flask'`

**解決策**:
1. Amplifyコンソールで「ビルド設定」を開く
2. 以下を確認：

```yaml
version: 1
backend:
  phases:
    build:
      commands:
        - pip3 install -r requirements_production.txt
```

3. 「保存」をクリック
4. 「再デプロイ」をクリック

### Q2: アプリが起動しない

**エラー**: `Application failed to start`

**解決策**:
1. Amplifyコンソールで「環境変数」を開く
2. 以下を追加：

| キー | 値 |
|------|-----|
| `PORT` | `8000` |
| `PYTHON_VERSION` | `3.9` |

3. 「保存」をクリック
4. 「再デプロイ」をクリック

### Q3: データが読み込まれない

**原因**: データファイルがGitにプッシュされていない

**解決策**:
1. GitHub Desktopを開く
2. 左側のファイルリストで `sshve2_data_new_suppression_20260318_222020.json` にチェック
3. 「Commit to main」をクリック
4. 「Push origin」をクリック
5. Amplifyが自動的に再デプロイ

### Q4: GitHubに接続できない

**解決策**:
1. GitHubでPersonal Access Tokenを作成
   - https://github.com/settings/tokens
   - 「Generate new token (classic)」
   - スコープ: `repo` にチェック
   - 「Generate token」をクリック
   - トークンをコピー
2. Amplifyコンソールで「GitHub接続」を再試行
3. トークンを入力

---

## 🔄 データ更新方法

### 新しいデータファイルをデプロイ

1. GitHub Desktopを開く
2. 新しいJSONファイルを `C:\Users\murakei\.aki` にコピー
3. GitHub Desktopで変更が表示される
4. 「Commit to main」をクリック
5. 「Push origin」をクリック
6. Amplifyが自動的に再デプロイ（5分）

---

## 💰 費用

### AWS Amplify料金

- **ビルド時間**: 無料枠 1000分/月
- **ホスティング**: 無料枠 15GB/月
- **データ転送**: 無料枠 15GB/月

**月額合計**: 約 $0-5（無料枠内なら$0）

### 無料枠を超えた場合

- ビルド時間: $0.01/分
- ホスティング: $0.023/GB
- データ転送: $0.15/GB

**通常の使用では月額$5以下です。**

---

## 🎉 完了！

### あなたがやったこと
1. ✅ GitHub Desktopをインストール（5分）
2. ✅ リポジトリを作成（2分）
3. ✅ AWS Amplifyでデプロイ（3分）
4. ✅ URLを営業担当に共有（1分）

### 営業担当がやること
1. URLを開く

**それだけです！**

---

**最終更新**: 2026年3月19日
**AWSアカウントID**: 764946308314

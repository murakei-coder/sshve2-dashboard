# 🚀 今すぐ始める - AWSデプロイ（10分）

## ステップ1: GitHub Desktopをインストール（5分）

### 1. ダウンロード
ブラウザで開く: https://desktop.github.com/

「Download for Windows」をクリック → インストーラーを実行

### 2. GitHubにログイン
- GitHub Desktopが起動したら「Sign in to GitHub.com」
- ブラウザでGitHubアカウントにログイン（なければ作成）
- 「Authorize desktop」をクリック

---

## ステップ2: リポジトリを作成（2分）

### 1. GitHub Desktopで
- 「File」→「Add local repository」
- 「Choose...」→ `C:\Users\murakei\.aki` を選択
- 「Add repository」をクリック

### 2. エラーが出たら
- 「create a repository」をクリック
- Name: `sshve2-dashboard`
- 「Create repository」をクリック

### 3. コミット
- 左下の「Summary」に `Initial commit` と入力
- 「Commit to main」をクリック

### 4. GitHubにプッシュ
- 「Publish repository」をクリック
- 「Keep this code private」にチェック ✅
- 「Publish repository」をクリック
- 完了を待つ（1-2分）

---

## ステップ3: AWS Amplifyでデプロイ（3分）

### 1. Amplifyコンソールを開く
ブラウザで開く: https://console.aws.amazon.com/amplify/

右上のリージョン: 「東京（ap-northeast-1）」を確認

### 2. 新しいアプリを作成
- 「新しいアプリ」→「Webアプリをホスト」
- 「GitHub」を選択 → 「次へ」

### 3. GitHubを接続
- 「GitHubに接続」をクリック
- ブラウザで「Authorize AWS Amplify」
- パスワード入力（必要な場合）

### 4. リポジトリを選択
- リポジトリ: `sshve2-dashboard`
- ブランチ: `main`
- 「次へ」

### 5. ビルド設定を確認
自動検出された設定をそのまま使用
- 「次へ」

### 6. アプリ名を設定
- アプリ名: `sshve2-dashboard`
- 環境名: `production`
- 「次へ」

### 7. デプロイ開始
- 「保存してデプロイ」をクリック
- 5-10分待つ ☕

---

## ステップ4: 完了確認（1分）

### デプロイステータス
全て緑色のチェックマークになれば完了！
1. ✅ プロビジョン
2. ✅ ビルド
3. ✅ デプロイ
4. ✅ 検証

### URLを取得
```
https://main.xxxxxxxxxxxxx.amplifyapp.com
```

このURLをコピーして営業担当に共有！

---

## 🎉 完了！

営業担当は以下のURLを開くだけ：
```
https://main.xxxxxxxxxxxxx.amplifyapp.com
```

24時間いつでも使えます！

---

## ❓ トラブルシューティング

### ビルドが失敗したら
1. Amplifyコンソールで「ビルドログ」を確認
2. エラーメッセージをコピー
3. 私に教えてください

### データが表示されない
1. GitHub Desktopで `sshve2_data_new_suppression_20260318_222020.json` がコミットされているか確認
2. されていなければ、チェックを入れて「Commit」→「Push」

---

**最終更新**: 2026年3月19日
**所要時間**: 約10分

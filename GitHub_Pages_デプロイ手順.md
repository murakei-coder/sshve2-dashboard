# SSHVE2 Dashboard - GitHub Pagesデプロイ手順

24時間稼働するWebアプリを5分で公開します。

---

## ✅ 準備完了

以下のファイルが生成されました：
- `index.html` - メインダッシュボード
- `guide.html` - 使い方ガイド
- `sshve2_data_new_suppression_20260318_222020.json` - データファイル

---

## 📋 ステップ1: GitHubにプッシュ（2分）

### 1-1. GitHub Desktopを開く

1. デスクトップの「GitHub Desktop」アイコンをダブルクリック
2. 左側に変更されたファイルが表示されます：
   - `index.html`
   - `guide.html`
   - `generate_github_pages_version.py`

### 1-2. 変更をコミット

1. 左下の「Summary」欄に以下を入力：
   ```
   Add GitHub Pages static version
   ```

2. 「Commit to main」ボタンをクリック

### 1-3. GitHubにプッシュ

1. 上部の「Push origin」ボタンをクリック
2. 完了を待つ（10-30秒）

---

## 📋 ステップ2: GitHub Pagesを有効化（1分）

### 2-1. GitHubリポジトリを開く

1. ブラウザで以下を開く：
   ```
   https://github.com/murakei-coder/sshve2-dashboard
   ```

2. 既にログイン済みのはずです

### 2-2. Settingsを開く

1. リポジトリページの上部にある「Settings」タブをクリック

### 2-3. Pagesを設定

1. 左側のメニューで「Pages」をクリック
2. 「Source」セクションで：
   - Branch: `main` を選択
   - Folder: `/ (root)` を選択
3. 「Save」ボタンをクリック

### 2-4. デプロイ完了を待つ

1. 1-2分待つ
2. ページをリロード（F5キー）
3. 上部に緑色のボックスが表示されます：
   ```
   Your site is live at https://murakei-coder.github.io/sshve2-dashboard/
   ```

---

## 📋 ステップ3: 動作確認（1分）

### 3-1. ダッシュボードにアクセス

ブラウザで以下を開く：
```
https://murakei-coder.github.io/sshve2-dashboard/
```

### 3-2. 動作確認

1. ダッシュボードが表示される
2. フィルターが動作する
3. データが表示される

---

## 📋 ステップ4: 営業担当にURLを共有（1分）

以下のメールを送信：

```
件名: SSHVE2 Opportunity Dashboard - アクセス方法

営業担当 各位

お世話になっております。
SSHVE2 Opportunity Dashboardが利用可能になりました。

【アクセスURL】
https://murakei-coder.github.io/sshve2-dashboard/

【使い方ガイド】
https://murakei-coder.github.io/sshve2-dashboard/guide.html

【注意事項】
- ブラウザはChrome、Edge、Safari推奨
- 何もインストール不要、URLを開くだけで使えます
- 24時間いつでも利用可能です
- データ更新時はブラウザをリロード（F5キー）してください

ご不明点があればご連絡ください。
```

---

## 🔄 データ更新方法

### 新しいデータをデプロイ

1. **新しいJSONファイルを生成**
   - 通常の手順でJSONファイルを生成
   - ファイル名は同じ（`sshve2_data_new_suppression_20260318_222020.json`）

2. **GitHub Desktopでコミット**
   - GitHub Desktopを開く
   - 変更されたファイル（JSONファイル）が表示される
   - Summary: `Update dashboard data`
   - 「Commit to main」をクリック

3. **プッシュ**
   - 「Push origin」をクリック
   - 30秒-1分待つ

4. **営業担当に通知**
   - 「データを更新しました。ブラウザをリロード（F5キー）してください」

---

## ❓ トラブルシューティング

### Q1: ページが表示されない

**原因**: GitHub Pagesのデプロイが完了していない

**解決策**:
1. https://github.com/murakei-coder/sshve2-dashboard/actions を開く
2. 「pages build and deployment」が緑色のチェックマークになるまで待つ
3. 1-2分後に再度アクセス

### Q2: データが表示されない

**原因**: JSONファイルがプッシュされていない

**解決策**:
1. GitHub Desktopを開く
2. `sshve2_data_new_suppression_20260318_222020.json` が含まれているか確認
3. 含まれていない場合、コミット＆プッシュ

### Q3: 古いデータが表示される

**原因**: ブラウザのキャッシュ

**解決策**:
1. ブラウザで Ctrl+F5（強制リロード）
2. または、ブラウザのキャッシュをクリア

---

## 💰 費用

**完全無料、永久に使えます！**

- GitHub Pages: 無料
- 帯域幅: 月間100GB（十分）
- ストレージ: 1GB（十分）

---

## 🎉 完了！

### あなたがやったこと
1. ✅ 静的HTML版を生成（1分）
2. ✅ GitHubにプッシュ（2分）
3. ✅ GitHub Pagesを有効化（1分）
4. ✅ URLを営業担当に共有（1分）

### 営業担当がやること
1. URLを開く

**それだけです！**

---

**最終更新**: 2026年3月20日
**GitHubリポジトリ**: https://github.com/murakei-coder/sshve2-dashboard
**公開URL**: https://murakei-coder.github.io/sshve2-dashboard/

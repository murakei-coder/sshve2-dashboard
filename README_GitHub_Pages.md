# GitHub Pagesデプロイ - 準備完了

## ✅ 完了した作業

1. 大きなファイルを削除・除外しました：
   - `sshve2_dashboard_v2_cascading_*.html` (142MB) - 削除済み
   - `sshve2_final_dashboard_*.html` (141MB) - 削除済み
   - `data/BF25_3PAllraw.txt` (1.5GB) - .gitignoreに追加
   - `bin/amzn-mcp.exe` (125MB) - .gitignoreに追加

2. GitHub Pages用のファイルを生成しました：
   - `index.html` - メインダッシュボード
   - `guide.html` - 使い方ガイド

## 📋 次のステップ

### ステップ1: GitHub Desktopでコミット

1. GitHub Desktopを開く
2. 変更されたファイルが表示されます：
   - `.gitignore` (更新)
   - 削除されたファイル（赤色で表示）
   - `index.html` (新規)
   - `guide.html` (新規)

3. 左下の「Summary」欄に以下を入力：
   ```
   Add GitHub Pages version and remove large files
   ```

4. 「Commit to main」ボタンをクリック

### ステップ2: GitHubにプッシュ

1. 上部の「Push origin」ボタンをクリック
2. 完了を待つ（10-30秒）
3. エラーが出なければ成功です！

### ステップ3: GitHub Pagesを有効化

1. ブラウザで以下を開く：
   ```
   https://github.com/murakei-coder/sshve2-dashboard
   ```

2. 「Settings」タブをクリック

3. 左側のメニューで「Pages」をクリック

4. 「Source」セクションで：
   - Branch: `main` を選択
   - Folder: `/ (root)` を選択
   - 「Save」ボタンをクリック

5. 1-2分待つ

6. ページをリロード（F5キー）

7. 上部に緑色のボックスが表示されます：
   ```
   Your site is live at https://murakei-coder.github.io/sshve2-dashboard/
   ```

### ステップ4: 動作確認

ブラウザで以下を開く：
```
https://murakei-coder.github.io/sshve2-dashboard/
```

---

## 📊 データファイルについて

JSONデータファイルは小さいのでGitHubにプッシュできます。
`index.html`は自動的にJSONファイルを読み込みます。

---

## 🎉 完了！

これで24時間稼働するWebアプリが公開されます。
営業担当はURLを開くだけで使えます。

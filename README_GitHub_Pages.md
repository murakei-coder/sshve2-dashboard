# GitHub Pagesデプロイ - データファイルについて

## 問題

JSONデータファイル（`sshve2_data_new_suppression_20260318_222020.json`）が大きすぎてGitHubにプッシュできません。

## 解決策

データファイルは別の方法でホスティングします。

### オプション1: GitHub Releasesを使う（推奨）

1. GitHubリポジトリページを開く
2. 「Releases」→「Create a new release」
3. JSONファイルをアップロード
4. HTMLから直接URLを参照

### オプション2: 外部ストレージを使う

- Google Drive
- Dropbox
- AWS S3

### オプション3: データを分割する

大きなJSONファイルを複数の小さなファイルに分割してプッシュ

---

## 今すぐできること

まずはHTMLファイルだけをプッシュして、GitHub Pagesを有効化しましょう。
データは後で追加できます。

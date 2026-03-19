# スタンドアロンダッシュボード

## 概要
このツールは、データファイルとセラーリストを読み込んで、スタンドアロンHTMLダッシュボードを生成します。

生成されたHTMLファイルは：
- Pythonなしで動作（データが埋め込まれている）
- ダブルクリックでブラウザで開ける
- フィルター、検索、ソート、ページネーション機能付き
- 他の人に共有可能

## 使い方

### 管理者（ダッシュボードを生成する人）

1. `generate_dashboard.bat` をダブルクリック
2. 処理が完了すると `standalone_dashboard.html` が生成されます
3. このHTMLファイルを他の人に共有してください

**ファイルパスの変更方法：**
`generate_dashboard.bat` をテキストエディタで開いて、以下の行を編集：
```batch
set DATA_FILE=C:\Users\murakei\Desktop\3PEITS_AI\Opp_Dashboard\raw\Sourcing&Suppression_Sample.txt
set SELLER_FILE=C:\Users\murakei\Desktop\3PEITS_AI\Opp_Dashboard\raw\EITS_Seller_list.xlsx
set OUTPUT_FILE=standalone_dashboard.html
```

### エンドユーザー（ダッシュボードを見る人）

1. 受け取った `standalone_dashboard.html` をダブルクリック
2. ブラウザで自動的に開きます
3. Pythonのインストールは不要です！

## ダッシュボード機能

- **フィルター**: PF、GL、Team、Alias、Suppression Statusでフィルタリング
- **検索**: テーブル内の全データを検索
- **ソート**: 列ヘッダーをクリックして昇順/降順ソート
- **ページネーション**: 100行ごとにページ分割

## 必要な環境

### 管理者（生成時のみ）
- Python 3.x
- pandas
- openpyxl

インストール：
```bash
pip install pandas openpyxl
```

### エンドユーザー
- Webブラウザのみ（Chrome、Edge、Firefoxなど）
- Pythonは不要！

## データ形式

### データファイル
- タブ区切りテキストファイル（.txt）
- `merchant_customer_id` 列が必須

### セラーリスト
- Excelファイル（.xlsx）
- 必須列：`merchant_customer_id`, `team`, `alias`

## トラブルシューティング

**Q: バッチファイルを実行してもエラーが出る**
A: ファイルパスが正しいか確認してください。パスにスペースや特殊文字が含まれている場合は、ダブルクォートで囲んでください。

**Q: HTMLファイルが開かない**
A: ブラウザを右クリック → プログラムから開く → お好みのブラウザを選択

**Q: データが表示されない**
A: ブラウザのコンソール（F12キー）でエラーを確認してください。

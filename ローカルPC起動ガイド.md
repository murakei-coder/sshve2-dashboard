# SSHVE2 Dashboard - ローカルPC起動ガイド

あなたのPCで起動して、社内の営業担当がアクセスできるようにする方法です。

## 📋 全体の流れ（2ステップ）

1. **あなたのPCで起動**（5分）
2. **営業担当にURLを共有**（1分）

---

## ステップ1: あなたのPCで起動（5分）

### 1-1. 必要なパッケージをインストール

コマンドプロンプトまたはPowerShellを開いて、プロジェクトフォルダに移動：

```cmd
cd C:\Users\murakei\Desktop\SSHVE2\Dashboard
```

依存パッケージをインストール：

```cmd
pip install flask pandas gunicorn
```

### 1-2. データファイルを確認

以下のファイルがプロジェクトルートにあることを確認：
- `sshve2_data_new_suppression_20260318_222020.json`

### 1-3. アプリを起動

**方法A: 簡単起動（推奨）**

```cmd
python src/sshve2_dashboard_web_app.py
```

**方法B: 本番モード起動**

```cmd
start_production.bat
```

### 1-4. あなたのPCのIPアドレスを確認

別のコマンドプロンプトを開いて：

```cmd
ipconfig
```

「IPv4 アドレス」を探してください（例: `10.123.45.67` または `192.168.1.100`）

---

## ステップ2: 営業担当にURLを共有（1分）

### 営業担当に送るメール（コピペOK）

```
件名: SSHVE2 Opportunity Dashboard - アクセス方法

営業担当 各位

お世話になっております。
SSHVE2 Opportunity Dashboardが利用可能になりました。

【アクセス方法】
1. 社内ネットワークに接続（VPN接続または社内Wi-Fi）
2. ブラウザで以下のURLを開く
   http://YOUR_PC_IP:5001

【使い方ガイド】
   http://YOUR_PC_IP:5001/guide

【注意事項】
- 社内ネットワーク接続必須
- ブラウザはChrome、Edge、Safari推奨
- 何もインストール不要、URLを開くだけで使えます
- 私のPCが起動している間のみ利用可能です

ご不明点があればご連絡ください。
```

**重要**: `YOUR_PC_IP` をステップ1-4で確認したIPアドレスに置き換えてください。

---

## 🔥 ファイアウォール設定（重要）

営業担当がアクセスできない場合、Windowsファイアウォールでポートを開放する必要があります。

### 方法1: Windowsファイアウォール設定（GUI）

1. 「コントロールパネル」を開く
2. 「Windows Defender ファイアウォール」をクリック
3. 左側の「詳細設定」をクリック
4. 「受信の規則」を右クリック → 「新しい規則」
5. 「ポート」を選択 → 「次へ」
6. 「TCP」を選択、「特定のローカルポート」に `5001` を入力 → 「次へ」
7. 「接続を許可する」を選択 → 「次へ」
8. すべてにチェック → 「次へ」
9. 名前: `SSHVE2 Dashboard` → 「完了」

### 方法2: コマンドで設定（管理者権限必要）

PowerShellを管理者として実行：

```powershell
New-NetFirewallRule -DisplayName "SSHVE2 Dashboard" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow
```

---

## ⚠️ 注意事項

### あなたがやること
- PCを起動したままにする（営業担当が使う間）
- PCがスリープモードにならないように設定
- 社内ネットワークに接続したままにする

### PCをスリープさせない設定

1. 「設定」→「システム」→「電源とスリープ」
2. 「スリープ」を「なし」に設定（使用中のみ）

---

## 🛑 停止方法

コマンドプロンプトで `Ctrl+C` を押すだけです。

---

## 📊 アクセス確認

### 自分のPCでテスト

ブラウザで以下を開く：
```
http://localhost:5001
```

### 営業担当がアクセスできるかテスト

別のPCから以下を開く：
```
http://YOUR_PC_IP:5001
```

---

## ❓ トラブルシューティング

### Q1: 営業担当がアクセスできない

**原因1**: ファイアウォールがブロックしている
→ 上記の「ファイアウォール設定」を実施

**原因2**: 異なるネットワークにいる
→ 同じWi-Fiまたは社内ネットワークに接続しているか確認

**原因3**: IPアドレスが間違っている
→ `ipconfig` で再確認

### Q2: データが読み込まれない

**原因**: ファイルパスが間違っている

**解決策**:
`src/sshve2_dashboard_web_app.py` の52-53行目を確認：

```python
json_file = 'sshve2_data_new_suppression_20260318_222020.json'
suppression_file = r'C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt'
```

ファイルが存在するか確認：
```cmd
dir sshve2_data_new_suppression_20260318_222020.json
dir "C:\Users\murakei\Desktop\SSHVE2\Dashboard\raw\Suppression\SSHVE2_ByASIN_Suppression_raw_Final.txt"
```

### Q3: ポート5001が使用中

**解決策**: 別のポートを使う

`src/sshve2_dashboard_web_app.py` の最後の行を編集：

```python
app.run(debug=True, host='0.0.0.0', port=5002)  # 5001から5002に変更
```

---

## 🚀 より安定した運用方法

### オプション1: 常時起動用のバッチファイル

`start_dashboard_always_on.bat` を作成：

```batch
@echo off
echo ========================================
echo SSHVE2 Dashboard - 常時起動モード
echo ========================================
echo.
echo あなたのPCのIPアドレス:
ipconfig | findstr "IPv4"
echo.
echo アクセスURL: http://YOUR_PC_IP:5001
echo.
echo 停止するには Ctrl+C を押してください
echo ========================================
echo.

cd /d "%~dp0"
python src/sshve2_dashboard_web_app.py

pause
```

ダブルクリックで起動できます。

### オプション2: タスクスケジューラで自動起動

1. 「タスクスケジューラ」を開く
2. 「基本タスクの作成」
3. トリガー: 「コンピューターの起動時」
4. 操作: 「プログラムの開始」
5. プログラム: `python`
6. 引数: `C:\Users\murakei\Desktop\SSHVE2\Dashboard\src\sshve2_dashboard_web_app.py`

これでPC起動時に自動的にダッシュボードが起動します。

---

## まとめ

### あなたがやること
1. ✅ 依存パッケージをインストール（1分）
2. ✅ アプリを起動（1分）
3. ✅ IPアドレスを確認（1分）
4. ✅ ファイアウォールを設定（2分）
5. ✅ 営業担当にURLを共有（1分）

### 営業担当がやること
1. 社内ネットワークに接続
2. URLを開く

**それだけです！**

---

**最終更新**: 2026年3月19日

# PDF Binder

この小さな Streamlit アプリは、複数の PDF をアップロードして、ファイル名の末尾にある数字（例: `document (8).pdf` の `8`）の順に結合し、1つの PDF としてダウンロードできます。

## 使い方（Windows PowerShell）

1. 仮想環境を作る（任意）:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. 依存をインストール:

```powershell
pip install -r requirements.txt
```

3. Streamlit アプリを起動:

```powershell
streamlit run app.py
```

4. ブラウザで開いた UI から複数の PDF を選択してアップロードし、「結合してダウンロード」ボタンを押してください。

## 備考
- ファイル名に数字が見つからない場合、そのファイルは結合リストの先頭に置かれ、アップロード順が保たれます。
- 大きなファイルを多数アップロードするとメモリを大量に消費する可能性があります。必要ならファイルサイズチェックや一時ファイルでの処理に改修してください。

---

作成: Streamlit + pypdf を使ったシンプルな PDF マージアプリ

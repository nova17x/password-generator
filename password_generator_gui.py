#!/usr/bin/env python3
"""
セキュアなパスワード生成ツール - GUI版
Tkinterを使用したグラフィカルインターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox
from password_generator import generate_password, evaluate_password_strength


class PasswordGeneratorGUI:
    """パスワードジェネレータのGUIアプリケーション"""

    def __init__(self, root):
        """
        GUIの初期化

        Args:
            root: Tkinterのルートウィンドウ
        """
        self.root = root
        self.root.title("パスワードジェネレータ")
        self.root.geometry("650x700")
        self.root.minsize(650, 700)
        self.root.resizable(True, True)

        # スタイル設定
        self.setup_styles()

        # メインフレームの作成
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # グリッドの重み設定（リサイズ対応）
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # UIコンポーネントの作成
        self.create_widgets(main_frame)

        # 起動時に自動でパスワードを生成
        self.generate_password()

    def setup_styles(self):
        """ttk Styleの設定"""
        style = ttk.Style()

        # プログレスバーのスタイル定義
        style.configure("Weak.Horizontal.TProgressbar", foreground='red', background='red')
        style.configure("Medium.Horizontal.TProgressbar", foreground='orange', background='orange')
        style.configure("Strong.Horizontal.TProgressbar", foreground='yellow green', background='yellow green')
        style.configure("VeryStrong.Horizontal.TProgressbar", foreground='green', background='green')

    def create_widgets(self, parent):
        """
        UIウィジェットを作成

        Args:
            parent: 親フレーム
        """
        row = 0

        # ========== パスワード長さスライダー ==========
        length_frame = ttk.LabelFrame(parent, text="パスワードの長さ", padding="10")
        length_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        length_frame.columnconfigure(0, weight=1)

        # 長さ表示ラベル
        self.length_var = tk.IntVar(value=16)
        self.length_label = ttk.Label(length_frame, text="16 文字", font=("", 12, "bold"))
        self.length_label.grid(row=0, column=0, pady=(0, 5))

        # スライダー
        self.length_slider = ttk.Scale(
            length_frame,
            from_=4,
            to=32,
            orient=tk.HORIZONTAL,
            variable=self.length_var,
            command=self.update_length_label
        )
        self.length_slider.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # スライダーの範囲表示
        range_label = ttk.Label(length_frame, text="(4〜32文字)", foreground="gray")
        range_label.grid(row=2, column=0, pady=(5, 0))

        row += 1

        # ========== 文字種選択チェックボックス ==========
        charset_frame = ttk.LabelFrame(parent, text="文字種の選択", padding="10")
        charset_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(charset_frame, text="大文字 (A-Z)", variable=self.upper_var).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Checkbutton(charset_frame, text="小文字 (a-z)", variable=self.lower_var).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Checkbutton(charset_frame, text="数字 (0-9)", variable=self.digits_var).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Checkbutton(charset_frame, text="記号 (!@#$%...)", variable=self.symbols_var).grid(
            row=3, column=0, sticky=tk.W, pady=2
        )

        row += 1

        # ========== 生成ボタン ==========
        self.generate_button = ttk.Button(
            parent,
            text="パスワードを生成",
            command=self.generate_password,
            style="Accent.TButton"
        )
        self.generate_button.grid(row=row, column=0, pady=(0, 15))

        row += 1

        # ========== パスワード表示エリア ==========
        password_frame = ttk.LabelFrame(parent, text="生成されたパスワード", padding="10")
        password_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        password_frame.columnconfigure(0, weight=1)

        # パスワード表示用テキストボックス
        self.password_text = tk.Text(
            password_frame,
            height=2,
            font=("Courier", 14),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.password_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        row += 1

        # ========== コピーボタン ==========
        self.copy_button = ttk.Button(
            parent,
            text="クリップボードにコピー",
            command=self.copy_to_clipboard
        )
        self.copy_button.grid(row=row, column=0, pady=(0, 15))

        row += 1

        # ========== 強度表示エリア ==========
        strength_frame = ttk.LabelFrame(parent, text="パスワード強度", padding="10")
        strength_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))
        strength_frame.columnconfigure(0, weight=1)

        # プログレスバー
        self.strength_progress = ttk.Progressbar(
            strength_frame,
            length=400,
            mode='determinate',
            style="VeryStrong.Horizontal.TProgressbar"
        )
        self.strength_progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 強度レベルとスコア表示
        self.strength_label = ttk.Label(
            strength_frame,
            text="強度: 非常に強い (0/100)",
            font=("", 11, "bold")
        )
        self.strength_label.grid(row=1, column=0, sticky=tk.W)

        # フィードバックメッセージ
        self.feedback_label = ttk.Label(
            strength_frame,
            text="評価: ",
            foreground="gray",
            wraplength=500,
            justify=tk.LEFT
        )
        self.feedback_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

    def update_length_label(self, value):
        """
        スライダーの値が変更されたときに長さラベルを更新

        Args:
            value: スライダーの現在値（文字列）
        """
        length = int(float(value))
        self.length_label.config(text=f"{length} 文字")

    def generate_password(self):
        """パスワードを生成して表示する"""
        try:
            # 設定値の取得
            length = self.length_var.get()
            use_upper = self.upper_var.get()
            use_lower = self.lower_var.get()
            use_digits = self.digits_var.get()
            use_symbols = self.symbols_var.get()

            # パスワード生成
            password = generate_password(length, use_upper, use_lower, use_digits, use_symbols)

            # パスワード表示
            self.password_text.config(state=tk.NORMAL)
            self.password_text.delete(1.0, tk.END)
            self.password_text.insert(1.0, password)
            self.password_text.config(state=tk.DISABLED)

            # 強度評価
            level, score, feedback = evaluate_password_strength(password)
            self.update_strength_display(level, score, feedback)

        except ValueError as e:
            # エラーメッセージ表示
            messagebox.showerror("エラー", str(e))

    def update_strength_display(self, level, score, feedback):
        """
        強度表示を更新

        Args:
            level: 強度レベル（文字列）
            score: スコア（0-100）
            feedback: フィードバックメッセージ
        """
        # プログレスバーの値を設定
        self.strength_progress['value'] = score

        # スコアに応じてプログレスバーのスタイルを変更
        if score >= 80:
            self.strength_progress.config(style="VeryStrong.Horizontal.TProgressbar")
        elif score >= 60:
            self.strength_progress.config(style="Strong.Horizontal.TProgressbar")
        elif score >= 40:
            self.strength_progress.config(style="Medium.Horizontal.TProgressbar")
        else:
            self.strength_progress.config(style="Weak.Horizontal.TProgressbar")

        # ラベルを更新
        self.strength_label.config(text=f"強度: {level} ({score}/100)")
        self.feedback_label.config(text=f"評価: {feedback}")

    def copy_to_clipboard(self):
        """パスワードをクリップボードにコピー"""
        # パスワードテキストの取得
        password = self.password_text.get(1.0, tk.END).strip()

        if password:
            # クリップボードにコピー
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()  # クリップボードを更新

            # ボタンテキストを一時的に変更
            original_text = self.copy_button['text']
            self.copy_button['text'] = "✓ コピーしました！"
            self.copy_button.config(state=tk.DISABLED)

            # 1.5秒後に元に戻す
            self.root.after(1500, lambda: [
                self.copy_button.config(text=original_text, state=tk.NORMAL)
            ])
        else:
            messagebox.showwarning("警告", "コピーするパスワードがありません")


def main():
    """メイン関数：GUIアプリケーションを起動"""
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

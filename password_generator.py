#!/usr/bin/env python3
"""
セキュアなパスワード生成ツール
コマンドラインから使用できるパスワードジェネレータで、強度評価機能付き
"""

import secrets
import string
import argparse
import sys
from typing import Tuple


def get_character_set(use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool) -> str:
    """
    選択された文字種から文字セットを構築する

    Args:
        use_upper: 大文字を含むか
        use_lower: 小文字を含むか
        use_digits: 数字を含むか
        use_symbols: 記号を含むか

    Returns:
        文字セットの文字列

    Raises:
        ValueError: すべての文字種がFalseの場合
    """
    charset = ""

    if use_upper:
        charset += string.ascii_uppercase
    if use_lower:
        charset += string.ascii_lowercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += string.punctuation

    if not charset:
        raise ValueError("少なくとも1つの文字種を選択してください")

    return charset


def generate_password(length: int, use_upper: bool, use_lower: bool,
                     use_digits: bool, use_symbols: bool) -> str:
    """
    指定された設定でパスワードを生成する

    Args:
        length: パスワードの長さ
        use_upper: 大文字を含むか
        use_lower: 小文字を含むか
        use_digits: 数字を含むか
        use_symbols: 記号を含むか

    Returns:
        生成されたパスワード

    Raises:
        ValueError: 長さが1未満の場合、または文字種が選択されていない場合
    """
    if length < 1:
        raise ValueError("パスワードの長さは1以上である必要があります")

    charset = get_character_set(use_upper, use_lower, use_digits, use_symbols)

    # secretsモジュールを使用して暗号学的に安全な乱数でパスワード生成
    password = ''.join(secrets.choice(charset) for _ in range(length))

    return password


def evaluate_password_strength(password: str) -> Tuple[str, int, str]:
    """
    パスワードの強度を評価する

    Args:
        password: 評価するパスワード

    Returns:
        (評価レベル, スコア, フィードバックメッセージ)のタプル
    """
    score = 0
    feedback = []

    # 長さによる評価
    length = len(password)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
        feedback.append("より長いパスワード(16文字以上)を推奨します")
    elif length >= 8:
        score += 20
        feedback.append("より長いパスワード(12文字以上)を推奨します")
    else:
        score += 10
        feedback.append("パスワードが短すぎます(最低8文字推奨)")

    # 文字種の多様性による評価
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    variety_count = sum([has_upper, has_lower, has_digit, has_symbol])

    if variety_count == 4:
        score += 40
    elif variety_count == 3:
        score += 30
        feedback.append("記号を追加するとさらに強化されます")
    elif variety_count == 2:
        score += 15
        feedback.append("より多くの文字種を使用してください")
    else:
        score += 5
        feedback.append("文字種が少なすぎます")

    # エントロピーの簡易計算（文字セットサイズ × 長さ）
    charset_size = 0
    if has_upper:
        charset_size += 26
    if has_lower:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_symbol:
        charset_size += 32  # string.punctuationの文字数

    if charset_size > 0:
        import math
        entropy = length * math.log2(charset_size)
        if entropy >= 80:
            score += 20
        elif entropy >= 60:
            score += 15
        elif entropy >= 40:
            score += 10
        else:
            score += 5

    # スコアに基づいて評価レベルを決定
    if score >= 80:
        level = "非常に強い"
    elif score >= 60:
        level = "強い"
    elif score >= 40:
        level = "中程度"
    else:
        level = "弱い"

    feedback_text = " / ".join(feedback) if feedback else "良好なパスワードです"

    return level, score, feedback_text


def main():
    """
    メイン関数：CLIインターフェースを提供
    """
    parser = argparse.ArgumentParser(
        description="セキュアなパスワード生成ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s                    # デフォルト設定で1つ生成
  %(prog)s -l 20 -n 5         # 20文字のパスワードを5つ生成
  %(prog)s --no-symbols       # 記号を含まないパスワード生成
  %(prog)s -l 12 --no-upper   # 大文字を含まない12文字のパスワード
        """
    )

    parser.add_argument(
        '-l', '--length',
        type=int,
        default=16,
        help='パスワードの長さ (デフォルト: 16)'
    )

    parser.add_argument(
        '-n', '--count',
        type=int,
        default=1,
        help='生成するパスワードの数 (デフォルト: 1)'
    )

    parser.add_argument(
        '--upper',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='大文字を含む (デフォルト: True)'
    )

    parser.add_argument(
        '--lower',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='小文字を含む (デフォルト: True)'
    )

    parser.add_argument(
        '--digits',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='数字を含む (デフォルト: True)'
    )

    parser.add_argument(
        '--symbols',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='記号を含む (デフォルト: True)'
    )

    args = parser.parse_args()

    # 入力検証
    if args.length < 4:
        print("エラー: パスワードの長さは4文字以上にしてください", file=sys.stderr)
        sys.exit(1)

    if args.count < 1:
        print("エラー: 生成数は1以上にしてください", file=sys.stderr)
        sys.exit(1)

    try:
        # パスワード生成と表示
        for i in range(args.count):
            password = generate_password(
                args.length,
                args.upper,
                args.lower,
                args.digits,
                args.symbols
            )

            level, score, feedback = evaluate_password_strength(password)

            print(f"\nパスワード {i + 1}: {password}")
            print(f"強度: {level} (スコア: {score}/100)")
            print(f"評価: {feedback}")

    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

---
name: ui-ux-design
description: |
  プロダクショングレードのUI/UXを作成するための統合スキル。
  ダッシュボード、管理画面、LP、Webアプリケーション等のUI構築時に使用。
  Linear, Notion, Stripe, Vercel等のデザイン品質を再現し、
  AIっぽい平凡なデザインを避け、独自性のある洗練されたインターフェースを生成する。
---

# UI/UX Design Skill

このスキルは、エンタープライズソフトウェア、SaaSダッシュボード、管理画面、Webアプリケーション向けの精密で洗練されたデザインを生成する。

---

## フェーズ1: デザイン方向性の決定（必須）

**コードを書く前に、必ずデザイン方向性を決定する。** デフォルトに頼らない。このプロダクトが何を感じさせるべきかを考える。

### コンテキスト分析

以下の質問に答えてからデザインを開始する：

1. **プロダクトの目的は？** ファイナンスツールとクリエイティブツールでは必要なエネルギーが異なる
2. **ユーザーは誰か？** パワーユーザーは情報密度を求め、カジュアルユーザーはガイダンスを求める
3. **感情的な仕事は？** 信頼？効率？喜び？集中？
4. **何が記憶に残るか？** すべてのプロダクトには独自性を出すチャンスがある

### デザインパーソナリティの選択

エンタープライズ/SaaS UIには想像以上の幅がある。以下の方向性から選択：

| 方向性 | 美学 | 適用先 |
|--------|------|--------|
| **Precision & Density** | タイトな間隔、モノクロ、情報優先 | 開発者ツール、パワーユーザーアプリ（Linear, Raycast） |
| **Warmth & Approachability** | 広い余白、柔らかい影、フレンドリーな色 | コラボレーションツール、コンシューマーSaaS（Notion, Coda） |
| **Sophistication & Trust** | クールな色調、レイヤード深度、金融的重厚感 | フィンテック、エンタープライズB2B（Stripe, Mercury） |
| **Boldness & Clarity** | 高コントラスト、大胆な余白、自信のあるタイポグラフィ | モダンダッシュボード、マーケティング（Vercel） |
| **Utility & Function** | ミュートなパレット、機能的密度、明確な階層 | GitHubスタイルのツール、開発者ツール |
| **Data & Analysis** | チャート最適化、技術的だがアクセシブル、数字第一 | アナリティクス、BI、メトリクスダッシュボード |

**1つを選ぶか、2つをブレンドする。しかし、プロダクトに合った方向性にコミットする。**

### トーンの選択（大胆なアプローチ）

以下の極端なスタイルから選択またはインスパイアを得る：

- **Brutally Minimal** — 極限まで削ぎ落とした美学
- **Maximalist Chaos** — 情報過多を美しく見せる
- **Retro-Futuristic** — 80sサイバーパンク × 現代UI
- **Organic/Natural** — 自然界からインスピレーション
- **Luxury/Refined** — ハイエンドブランドの質感
- **Playful/Toy-like** — 遊び心のあるインタラクション
- **Editorial/Magazine** — 出版物のレイアウト美学
- **Brutalist/Raw** — むき出しの構造美
- **Art Deco/Geometric** — 幾何学パターン
- **Soft/Pastel** — 柔らかい色調
- **Industrial/Utilitarian** — 工業的機能美

---

## フェーズ2: カラーファウンデーション

**デフォルトで暖色系に逃げない。** プロダクトを考慮：

### ベースカラー選択

| タイプ | 特徴 | 用途 |
|--------|------|------|
| **Warm foundations** | クリーム、ウォームグレー | 親しみやすい、人間的 |
| **Cool foundations** | スレート、ブルーグレー | プロフェッショナル、信頼性 |
| **Pure neutrals** | トゥルーグレー、黒/白 | ミニマル、大胆、技術的 |
| **Tinted foundations** | 微妙なカラーキャスト | 独自性、ブランド |

### 業界別推奨パレット

```
SaaS:           Primary #4F46E5 (Indigo), Accent #10B981 (Emerald)
Fintech:        Primary #0F172A (Slate), Accent #22C55E (Green)
Healthcare:     Primary #0EA5E9 (Sky), Accent #14B8A6 (Teal)
E-commerce:     Primary #7C3AED (Violet), Accent #F59E0B (Amber)
Creative:       Primary #EC4899 (Pink), Accent #8B5CF6 (Purple)
Developer:      Primary #18181B (Zinc), Accent #3B82F6 (Blue)
```

### ライト vs ダーク

- **Dark Mode** — 技術的、集中、プレミアム感
- **Light Mode** — オープン、親しみやすい、クリーン

**アクセントカラー** — 意味を持つ1つを選ぶ：
- Blue = 信頼
- Green = 成長・成功
- Orange = エネルギー
- Violet = 創造性
- Red = 緊急・注意（控えめに）

---

## フェーズ3: コアクラフト原則

デザイン方向性に関係なく適用される品質の床。

### 4pxグリッドシステム

すべてのスペーシングは4pxベースグリッドを使用：

```css
/* スペーシングスケール */
--space-1: 4px;   /* マイクロ（アイコンギャップ） */
--space-2: 8px;   /* タイト（コンポーネント内） */
--space-3: 12px;  /* 標準（関連要素間） */
--space-4: 16px;  /* 快適（セクションパディング） */
--space-6: 24px;  /* 広め（セクション間） */
--space-8: 32px;  /* 大きな区切り */
--space-12: 48px; /* メジャーセパレーション */
```

### 対称パディング

**TLBRは一致させる。** トップパディングが16pxなら、左/下/右も16px。

```css
/* Good */
padding: 16px;
padding: 12px 16px; /* 水平にだけ余分なスペースが必要な場合のみ */

/* Bad - 非対称パディング */
padding: 24px 16px 12px 16px;
```

### ボーダーラジアス一貫性

4pxグリッドに従う。シャープなコーナーは技術的、丸いコーナーはフレンドリー：

```css
/* Sharp System */
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;

/* Soft System */
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;

/* Minimal System */
--radius-sm: 2px;
--radius-md: 4px;
--radius-lg: 6px;
```

**システムを混在させない。一貫性が統一感を生む。**

### 深度 & エレベーション戦略

**1つのアプローチを選び、コミットする。**

#### Option A: Borders-only（フラット）
```css
--border: rgba(0, 0, 0, 0.08);
--border-subtle: rgba(0, 0, 0, 0.05);
border: 0.5px solid var(--border);
```
→ クリーン、技術的、密度重視（Linear, Raycast）

#### Option B: Single Shadow（シンプル）
```css
--shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
```
→ ソフトリフト、親しみやすい

#### Option C: Layered Shadows（リッチ）
```css
--shadow-layered:
  0 0 0 0.5px rgba(0, 0, 0, 0.05),
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 2px 4px rgba(0, 0, 0, 0.03),
  0 4px 8px rgba(0, 0, 0, 0.02);
```
→ プレミアム、立体感（Stripe, Mercury）

#### Option D: Surface Color Shifts
背景の色相で階層を作り、影なしで立体感を出す。

```css
--surface-0: #ffffff;
--surface-1: #f8fafc;
--surface-2: #f1f5f9;
```

---

## フェーズ4: タイポグラフィシステム

### フォントスタック選択

| タイプ | フォント | トーン |
|--------|----------|--------|
| **System** | -apple-system, BlinkMacSystemFont | 速い、ネイティブ、透明 |
| **Geometric Sans** | Geist, Inter, Satoshi | モダン、クリーン、技術的 |
| **Humanist Sans** | SF Pro, Plus Jakarta Sans | 暖かい、親しみやすい |
| **Mono Influence** | JetBrains Mono, Fira Code | 技術、開発者向け |
| **Editorial** | Playfair Display, Fraunces | 出版物、ラグジュアリー |

### 推奨フォントペアリング

```css
/* Modern SaaS */
--font-display: 'Geist', sans-serif;
--font-body: 'Inter', sans-serif;

/* Premium Product */
--font-display: 'Fraunces', serif;
--font-body: 'Plus Jakarta Sans', sans-serif;

/* Developer Tool */
--font-display: 'JetBrains Mono', monospace;
--font-body: 'Inter', sans-serif;

/* Editorial */
--font-display: 'Playfair Display', serif;
--font-body: 'Source Serif Pro', serif;
```

### タイポグラフィ階層

```css
/* スケール */
--text-xs: 11px;
--text-sm: 12px;
--text-base: 14px;
--text-lg: 16px;
--text-xl: 18px;
--text-2xl: 24px;
--text-3xl: 32px;
--text-4xl: 48px;

/* ウェイトと詳細 */
.headline {
  font-weight: 600;
  letter-spacing: -0.02em;
}

.body {
  font-weight: 400;
  letter-spacing: 0;
}

.label {
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  font-size: var(--text-xs);
}

/* データ用モノスペース */
.data-value {
  font-family: 'JetBrains Mono', monospace;
  font-variant-numeric: tabular-nums;
}
```

---

## フェーズ5: UIスタイルカタログ

代表的なUIスタイル（Glassmorphism, Neumorphism, Claymorphism, Bento Grid, Dark Mode Premium）のCSSパターン: [references/css-patterns.md](references/css-patterns.md)

---

## フェーズ6: コンポーネント設計原則

### カードレイアウト多様性

単調なカードレイアウトは怠慢なデザイン。
- メトリクスカードにはスパークライン
- プランカードにはCTAと比較
- 設定カードには2カラム分割
- ユーザーカードにはアバタースタック

**各カードの内部構造は内容に合わせて設計し、表面処理（境界線の太さ、影の深さ、角丸、パディング、タイポグラフィ）は一貫させる。**

### 隔離されたコントロール

日付ピッカー、フィルター、ドロップダウンは、ページ上の洗練されたオブジェクトとして感じられるべき。

```css
.control-container {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  white-space: nowrap; /* テキストとアイコンを同じ行に保持 */
}
```

**重要:** ネイティブフォーム要素をスタイル付きUIに使用しない。カスタムコンポーネントを構築する。

### コントラスト階層

4レベルシステムを構築し、一貫して使用：

```css
--text-primary: #0f172a;   /* フォアグラウンド */
--text-secondary: #475569; /* セカンダリ */
--text-muted: #94a3b8;     /* ミュート */
--text-faint: #cbd5e1;     /* フェイント */
```

### 色は意味のためだけ

グレーで構造を構築。色はステータス、アクション、エラー、成功を伝えるときのみ使用。装飾的な色はノイズ。

```css
/* 意味のある色のみ */
--color-success: #22c55e;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
```

---

## フェーズ7-9: モーション・ダークモード・アイコン

詳細なCSSパターンとガイドライン: [references/css-patterns.md](references/css-patterns.md)

---

## フェーズ10: ナビゲーションコンテキスト

スクリーンには接地が必要。データテーブルが空間に浮いているとコンポーネントデモのように見える。

### 含めるべき要素

1. **ナビゲーション** — サイドバーまたはトップナビ
2. **現在地インジケーター** — パンくず、ページタイトル、アクティブナビ状態
3. **ユーザーコンテキスト** — ログインユーザー、ワークスペース/組織

### サイドバー設計

メインコンテンツと同じ背景を使用し、微妙なボーダーで分離（Supabase, Linear, Vercelスタイル）：

```css
.sidebar {
  background: var(--surface-0);
  border-right: 1px solid var(--border);
  width: 240px;
}
```

---

## アンチパターン

### 絶対にやってはいけない

- ❌ ドラマチックなドロップシャドウ（`box-shadow: 0 25px 50px...`）
- ❌ 小さな要素に大きなボーダーラジアス（16px+）
- ❌ 理由のない非対称パディング
- ❌ 色付き背景上の純白カード
- ❌ 装飾用の太いボーダー（2px+）
- ❌ 過剰なスペーシング（セクション間48px以上）
- ❌ スプリング/バウンシーアニメーション
- ❌ 装飾的なグラデーション
- ❌ 1つのインターフェースに複数のアクセントカラー
- ❌ Inter, Arial, Robotoへのデフォルト依存
- ❌ 紫グラデーション + 白背景（AIっぽい）

### 常に自問する

1. 「このプロダクトに何が必要か考えたか、デフォルトに逃げていないか？」
2. 「この方向性はコンテキストとユーザーに合っているか？」
3. 「この要素は洗練されているか？」
4. 「深度戦略は一貫して意図的か？」
5. 「すべての要素がグリッド上にあるか？」
6. 「何が記憶に残るか？」

---

## 実装チェックリスト

### コーディング前
- [ ] デザイン方向性を決定した
- [ ] カラーファウンデーションを選択した
- [ ] タイポグラフィスタックを決定した
- [ ] 深度戦略を選択した

### コーディング中
- [ ] 4pxグリッドに従っている
- [ ] パディングが対称的
- [ ] ボーダーラジアスが一貫
- [ ] カラーは意味のためだけに使用
- [ ] データにモノスペース使用
- [ ] アニメーションが150-250ms

### コーディング後
- [ ] ダークモード対応確認
- [ ] レスポンシブ対応確認
- [ ] ナビゲーションコンテキストあり
- [ ] アンチパターンを回避

---

## 品質基準

すべてのインターフェースは、1ピクセルの違いにこだわるチームがデザインしたように見えるべき。
剥ぎ取られたのではなく — *洗練された*。そして、特定のコンテキストのためにデザインされた。

開発者ツールは精度と密度を求める。コラボレーションプロダクトは暖かさとスペースを求める。金融プロダクトは信頼と洗練を求める。プロダクトコンテキストが美学をガイドする。

**目標: 適切なパーソナリティを持つ複雑なミニマリズム。同じ品質基準、コンテキスト駆動の実行。**

---

## 参考リソース

- Linear (https://linear.app) — Precision & Density
- Notion (https://notion.so) — Warmth & Approachability
- Stripe (https://stripe.com) — Sophistication & Trust
- Vercel (https://vercel.com) — Boldness & Clarity
- GitHub (https://github.com) — Utility & Function

**Remember: Claude is capable of extraordinary creative work.**



## 出典・マージ元

このスキルは以下の3つの優れたスキルをマージ・統合して作成された：

| スキル名 | 作者 | リポジトリ | ライセンス |
|----------|------|------------|------------|
| **frontend-design** | Anthropic | https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design | - |
| **claude-design-skill** | Dammyjay93 | https://github.com/Dammyjay93/claude-design-skill | MIT |
| **ui-ux-pro-max-skill** | nextlevelbuilder | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | MIT |

### 各スキルからの主な採用要素

- **frontend-design (Anthropic)**: 大胆な美学的方向性、トーン選択、AIっぽさ回避のアプローチ
- **claude-design-skill**: 4pxグリッドシステム、深度戦略、エンタープライズ品質基準、アンチパターン
- **ui-ux-pro-max-skill**: UIスタイルカタログ、業界別カラーパレット、フォントペアリング
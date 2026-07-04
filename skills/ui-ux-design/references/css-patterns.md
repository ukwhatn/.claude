# CSS Patterns & Style Catalog

ui-ux-design スキルで参照されるCSSパターン集。SKILL.md 本文でデザイン方向性・カラー・深度・タイポを決めた後、実装時に該当セクションの CSS 値・変数定義をここから参照する。

## 目次

- ファウンデーション — スペーシング（4pxグリッド） / 対称パディング / ボーダーラジアス / 深度・エレベーション
- カラー — 業界別パレット / コントラスト階層 / セマンティックカラー
- タイポグラフィ — フォントペアリング / 階層スケール
- コンポーネント — 隔離コントロール / サイドバー
- UIスタイルカタログ — Glassmorphism / Neumorphism / Claymorphism / Bento Grid / Dark Mode Premium
- モーション & アニメーション
- ダークモード考慮事項
- アイコノグラフィ

---

## ファウンデーション

### スペーシング（4pxグリッド）

すべてのスペーシングは 4px ベースグリッドを使用する。

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

TLBR を一致させる。トップパディングが 16px なら左/下/右も 16px。

```css
/* Good */
padding: 16px;
padding: 12px 16px; /* 水平にだけ余分なスペースが必要な場合のみ */

/* Bad - 非対称パディング */
padding: 24px 16px 12px 16px;
```

### ボーダーラジアス

4px グリッドに従う。シャープなコーナーは技術的、丸いコーナーはフレンドリー。**システムを混在させない。一貫性が統一感を生む。**

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

### 深度 & エレベーション

1つのアプローチを選び、コミットする。

#### Option A: Borders-only（フラット）— クリーン、技術的、密度重視（Linear, Raycast）
```css
--border: rgba(0, 0, 0, 0.08);
--border-subtle: rgba(0, 0, 0, 0.05);
border: 0.5px solid var(--border);
```

#### Option B: Single Shadow（シンプル）— ソフトリフト、親しみやすい
```css
--shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
```

#### Option C: Layered Shadows（リッチ）— プレミアム、立体感（Stripe, Mercury）
```css
--shadow-layered:
  0 0 0 0.5px rgba(0, 0, 0, 0.05),
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 2px 4px rgba(0, 0, 0, 0.03),
  0 4px 8px rgba(0, 0, 0, 0.02);
```

#### Option D: Surface Color Shifts — 背景の色相で階層を作り、影なしで立体感を出す
```css
--surface-0: #ffffff;
--surface-1: #f8fafc;
--surface-2: #f1f5f9;
```

---

## カラー

### 業界別パレット

```
SaaS:           Primary #4F46E5 (Indigo), Accent #10B981 (Emerald)
Fintech:        Primary #0F172A (Slate), Accent #22C55E (Green)
Healthcare:     Primary #0EA5E9 (Sky), Accent #14B8A6 (Teal)
E-commerce:     Primary #7C3AED (Violet), Accent #F59E0B (Amber)
Creative:       Primary #EC4899 (Pink), Accent #8B5CF6 (Purple)
Developer:      Primary #18181B (Zinc), Accent #3B82F6 (Blue)
```

### コントラスト階層

4レベルシステムを構築し、一貫して使用する。

```css
--text-primary: #0f172a;   /* フォアグラウンド */
--text-secondary: #475569; /* セカンダリ */
--text-muted: #94a3b8;     /* ミュート */
--text-faint: #cbd5e1;     /* フェイント */
```

### セマンティックカラー（ライト）

グレーで構造を構築し、色はステータス・アクション・エラー・成功を伝えるときのみ使う。装飾的な色はノイズ。

```css
--color-success: #22c55e;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
```

ダーク背景用の調整値（彩度を下げる）は「ダークモード考慮事項 > セマンティックカラー調整」を参照。

---

## タイポグラフィ

### フォントペアリング

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

### 階層スケール

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

## コンポーネント

### 隔離コントロール

日付ピッカー、フィルター、ドロップダウンは、ページ上の洗練されたオブジェクトとして感じられるべき。ネイティブフォーム要素をスタイル付き UI に使わず、カスタムコンポーネントを構築する。

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

### サイドバー

メインコンテンツと同じ背景を使用し、微妙なボーダーで分離（Supabase, Linear, Vercel スタイル）。

```css
.sidebar {
  background: var(--surface-0);
  border-right: 1px solid var(--border);
  width: 240px;
}
```

---

## UIスタイルカタログ

代表的なUIスタイルのCSS実装パターン。

### Glassmorphism
```css
.glass-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
}
```

### Neumorphism
```css
.neu-card {
  background: #e0e5ec;
  box-shadow:
    8px 8px 16px #a3b1c6,
    -8px -8px 16px #ffffff;
  border-radius: 20px;
}
```

### Claymorphism
```css
.clay-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 24px;
  box-shadow:
    inset 2px 2px 4px rgba(255, 255, 255, 0.5),
    8px 8px 16px rgba(0, 0, 0, 0.1);
}
```

### Bento Grid
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.bento-card-large {
  grid-column: span 2;
  grid-row: span 2;
}
```

### Dark Mode Premium
```css
.dark-premium {
  background: #0a0a0a;
  color: #fafafa;
  --accent: #3b82f6;
  --border: rgba(255, 255, 255, 0.08);
}
```

---

## モーション & アニメーション

### 基本原則

```css
/* 標準イージング */
--ease-out: cubic-bezier(0.25, 1, 0.5, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* デュレーション */
--duration-fast: 150ms;   /* マイクロインタラクション */
--duration-normal: 200ms; /* 通常のトランジション */
--duration-slow: 300ms;   /* 大きなトランジション */
```

### 推奨パターン

```css
/* ホバー状態 */
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-layered);
  transition: all var(--duration-fast) var(--ease-out);
}

/* ページロードのスタッガード表示 */
.fade-in-stagger {
  opacity: 0;
  transform: translateY(10px);
  animation: fadeIn var(--duration-normal) var(--ease-out) forwards;
}
.fade-in-stagger:nth-child(1) { animation-delay: 0ms; }
.fade-in-stagger:nth-child(2) { animation-delay: 50ms; }
.fade-in-stagger:nth-child(3) { animation-delay: 100ms; }

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**禁止:** エンタープライズUIでのスプリング/バウンシーエフェクト

---

## ダークモード考慮事項

### 影より境界線

ダーク背景では影が見えにくい。定義のために境界線に頼る。

```css
.dark-mode .card {
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none; /* または非常に控えめ */
}
```

### セマンティックカラー調整

ステータスカラーをダーク背景用に調整（彩度を下げる）：

```css
.dark-mode {
  --color-success: #4ade80; /* より明るく */
  --color-warning: #fbbf24;
  --color-error: #f87171;
}
```

---

## アイコノグラフィ

### 推奨アイコンライブラリ

1. **Phosphor Icons** (`@phosphor-icons/react`) — バランス良い
2. **Lucide** (`lucide-react`) — 軽量
3. **Heroicons** (`@heroicons/react`) — Tailwind統合

### 使用原則

- アイコンは明確にする、装飾しない
- 意味を失わずに削除できるアイコンは削除
- スタンドアロンアイコンには背景コンテナで存在感を与える

```css
.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--surface-1);
  border-radius: var(--radius-sm);
}
```

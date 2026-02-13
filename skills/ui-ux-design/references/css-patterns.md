# CSS Patterns & Style Catalog

ui-ux-design スキルで参照されるCSSパターン集。

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

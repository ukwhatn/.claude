# shadcn/ui への対応付け

PJ に `components.json` があるときに読む。型の選び方は SKILL.md の手順と各参照で決め、本ファイルは選んだ型を shadcn のどの部品とトークンで作るかだけを扱う。部品の API と組み立ての正誤（Group の入れ子・`asChild` と `render` の違い・Title の必須など）は `/shadcn` スキルに従う。

- 使える部品は、`npx shadcn@latest info --json` の `components` と `resolvedPaths.ui` で確かめる。`package.json` が無いなどで実行できないときは、`components.json` の `aliases.ui` が指すディレクトリの中身を見る。入っていない部品を使うなら `/shadcn` スキルの手順で追加する
- `base`（`radix` か `base`）で API が違う部品がある。toast の部品も `base` で変わる

## 型と部品

| 型 | 部品 | 注意 |
|---|---|---|
| サイドバー（広い幅） | `Sidebar` + `SidebarProvider` | 2段目は `Collapsible` で包んだ `SidebarGroup` にする。開閉は Cmd/Ctrl+B |
| レール（中くらいの幅） | `Sidebar collapsible="icon"` | 展開したときと同じ項目・同じ順序のまま畳む |
| 狭い幅で畳んだメニュー | `Sidebar collapsible="offcanvas"` | |
| 上部ナビ | `NavigationMenu` | 行き先へのリンクの集まりとして使う |
| タブ（画面の中の切り替え） | `Tabs` | URL が変わる切り替えには使わない |
| URL が変わるタブ風の列・作業中の対象の横タブ（各タブが URL を持つ） | リンク（`<a>` かフレームワークの Link）を並べた `nav` に `aria-current="page"` | `Tabs` を使わない。閉じるボタンはリンクの隣の `Button` |
| ローカルのサイドナビ | リンクを縦に並べた `nav`（`aria-current="page"`） | グローバルの `Sidebar` と見た目で区別し、控えめにする |
| セグメント（表示切替） | `ToggleGroup` | |
| パンくず | `Breadcrumb` | |
| ページ送り | `Pagination` | |
| コマンドパレット | `Dialog` の中の `Command` | 見えるナビと併置する |
| 一覧と詳細・主内容と補助ペイン | `ResizablePanelGroup` と `ResizablePanel` | 狭い幅での畳み方は自分で実装する |
| モーダルダイアログ | `Dialog` | |
| 確認ダイアログ | `AlertDialog` | |
| 側面パネル（モーダル） | `Sheet` | `Sheet` は `Dialog` の拡張で、モーダルとして動く |
| 側面パネル（非モーダル） | `ResizablePanel` か `Sidebar side="right"` | `Sheet` を使わない（背景を操作できなくなる） |
| 下から出るシート | `Drawer` | |
| ポップオーバー | `Popover` | |
| メニュー | `DropdownMenu` / `ContextMenu` / `Menubar` | |
| ツールチップ | `Tooltip` | |
| ホバーカード | `HoverCard` | ホバーでしか届かない内容にしない |
| その場の展開 | `Collapsible` / `Accordion` | |
| toast | `base` が `radix` なら `sonner`、`base` なら `toast` | エラーに使わない |
| 項目の近くのエラー | `Field`（`data-invalid`）+ 入力部品（`aria-invalid`）+ `FieldError` | |
| 領域内のメッセージ・画面上部のバナー | `Alert` | バナーとして使うときも同じ画面に1つだけ |
| 空状態 | `Empty` | |
| 読み込み | `Skeleton` / `Spinner` / `Progress` | `Button` に読み込みの prop は無い。`Spinner` と `disabled` で組む |

## トークン

- 色は意味を持つトークン（`bg-primary`・`text-muted-foreground` など）だけを使う。パレットの色（`bg-blue-500`）・色コード・`dark:` での手動の上書きを書かない（テーマとダークモードの切替に追随しないから）
- 面の色（`--card` など）と、その上の文字色（`--card-foreground` など）を対で使う
- 成功・警告など、テーマに無い状態の色が要るときは、`Badge` の variant か `text-destructive` で足りるかを先に見る。足りないなら、テーマに CSS 変数を足すことをユーザーに確認してから、`:root` と `.dark` に定義する。Tailwind v4 は `@theme inline` で公開し、v3 は `tailwind.config` に登録する
- 面の明暗の段階が要るときは、PJ のテーマで `--background`・`--card`・`--popover`・`--muted` が段階を持つかを確かめる。段階が無いなら、面を持ち上げず境界線（`--border`）か余白で区切る
- 角丸は `--radius` から派生させ、部品ごとに値を書かない
- 部品の見た目は variant で変える。呼び出し側の `className` で決めてよいのは配置と幅（margin・width・flex の配分）だけ。足りない見た目は、部品の定義（`components/ui` の中）に variant を足す

## lint

`@shadcn/lint` は、上のトークンと見た目の規則を機械で検査する。ルールは次の6つ。

| ルール | 検査すること |
|---|---|
| `no-restyle` | 部品に `className` で配置以外の見た目（余白・色・文字・形・影・動き）を付けていないか |
| `no-raw-colors` | パレットの色・テーマに無い色・SVG の生の色を使っていないか |
| `no-arbitrary-values` | `p-[13px]` のようなスケール外の任意値を使っていないか |
| `no-inline-styles` | `style` 属性・`<style>` で見た目を書いていないか（動的な値は CSS 変数で渡す） |
| `no-unknown-classes` | Tailwind が生成しないクラス（綴りの誤り）を書いていないか |
| `require-static-classes` | クラス名を文字列の連結で組み立てていないか |

- PJ に `@shadcn/lint` が入っていれば、変更の後に PJ 規定の lint コマンドで実行し、指摘を直す。例外は理由を書いた disable コメントで残す
- 入っていない PJ に導入するのは依頼の範囲外。必要だと思えば提案として伝える
- lint はレイアウト・型の選択・a11y・文言を検査しない。それらは SKILL.md の手順8で確認する

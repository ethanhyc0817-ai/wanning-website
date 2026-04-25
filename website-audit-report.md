# 网站性能审计报告（仅检查，不动代码）

审计时间：2026-04-25  
审计目标：`index.html`（3538 行，173 KB）+ 所有链接到的页面 + `Assets/` 文件夹

---

## 重要结论先行（一句话总结）

**首页之所以重，不是因为图片没压缩，而是因为整个网站的所有"页面"都被打包进了同一个 `index.html` 里。** Wave Pool 页、7 个 Session Detail 页、Packages 页、Explore Hainan 页、Plan Your Trip 页、Contact 页**全部以 `display:none` 的方式预先放在 DOM 里**。用户打开首页时，浏览器仍然会下载这些"隐藏页面"里的图片、视频和 YouTube iframe。

另外，`Assets/` 文件夹里有 **155 个文件没有任何 HTML 引用**（≈ 200 MB）。这部分不影响首页加载（因为没被引用），但会拖慢 Git push 和 Vercel 部署。

---

## 1. 隐藏区块（仍在 DOM 里，仍会下载资源）

> 架构层面的问题：`index.html` 是一个 single-page-app 风格的页面，用 `.page { display:none }` + `.page.active { display:block }` 来切换路由。所有"页面"全部在 DOM 里。

| 文件 | 区块 | 行号 | 是否安全移除 | 原因 | 移除后影响 |
|---|---|---|---|---|---|
| index.html | `#page-wavepool`（整个 Wave Pool 页） | 1550–1844 | **不能直接删** | 是导航的第二个主菜单，菜单链接 `showPage('wavepool')` 会跳转到这里 | 路由：会破坏 Wave Pool 入口 |
| index.html | `#page-session-learn` | 1847–2004 | **不能直接删** | 用户点 Wave Pool → 7 个 session 卡片之一时跳到这里 | 路由：会破坏 Session 详情入口 |
| index.html | `#page-session-beginner` | 2007–2155 | 同上 | 同上 | 同上 |
| index.html | `#page-session-intermediate` | 2157–2317 | 同上 | 同上 | 同上 |
| index.html | `#page-session-advanced` | 2320–2466 | 同上 | 同上 | 同上 |
| index.html | `#page-session-barrel` | 2469–2614 | 同上 | 同上 | 同上 |
| index.html | `#page-session-air` | 2617–2762 | 同上 | 同上 | 同上 |
| index.html | `#page-session-private` | 2765–2912 | 同上 | 同上 | 同上 |
| index.html | `#page-packages` | 2915–3018 | **不能直接删** | 主菜单 Packages 入口 | 路由 |
| index.html | `#page-explore` | 3021–3146 | **不能直接删** | 主菜单 Explore Hainan 入口 | 路由 |
| index.html | `#page-plan` | 3149–3252 | **不能直接删** | 主菜单 Plan Your Trip 入口 | 路由 |
| index.html | `#page-contact` | 3255–3385 | **不能直接删** | 主菜单 Contact / 所有 CTA 都跳到这里 | 路由 |

> **建议（不立刻执行）：**
> 1. 短期内：给所有非首页区块里的 `<img>` 加 `loading="lazy"`，给两个 YouTube `<iframe>` 加 `loading="lazy"`。这样浏览器会延迟到滚动到才下载。
> 2. 中长期：把 7 个 Session Detail 页（行 1847–2912，约 1066 行）和 Wave Pool 页拆成独立 HTML 文件（像 `culture.html` / `golf.html` 已经做过的那样）。这是首页瘦身最大的一刀。

### 1b. CSS 真正"display:none"的元素（功能性，不能动）

| 行号 | 选择器 | 用途 | 是否安全移除 |
|---|---|---|---|
| 112 | `.nav-logo-text` | 小屏幕隐藏 logo 文字 | 不能动（响应式） |
| 132 | `.nav-mobile-toggle` | 桌面隐藏汉堡菜单 | 不能动（响应式） |
| 135 | `.nav-mobile-cta` | 桌面隐藏移动版 CTA | 不能动（响应式） |
| 568 | `.gallery-nav` | 桌面隐藏画廊左右箭头 | 不能动（移动端用） |
| 724 | `.mobile-menu` | 默认隐藏移动菜单遮罩 | 不能动（点击汉堡时打开） |
| 676 | `.page` | 路由切换 | 不能动（核心架构） |
| 865 | `.facilities-grid .facility-card-body p` | 中屏隐藏卡片描述文字 | 不能动（响应式） |

---

## 2. 重复或旧版本区块

| 文件 | 旧版本痕迹 | 行号 | 是否安全移除 | 原因 |
|---|---|---|---|---|
| index.html | `<!-- HIDDEN BREAKS - Natural Surf Secret -->` | 1254 | **保留**（误判） | 这里 "HIDDEN BREAKS" 指的是"海南隐藏的浪点（隐秘冲浪点）"，不是技术上隐藏的区块。这一段是首页可见内容的一部分。 |
| index.html | `.sd-video-placeholder` CSS（行 1058–1060） | — | **可清理**（CSS 残留） | 早期 session detail 页用占位图，现在已经全部换成真视频了。HTML 里搜不到这个 class。 |

**没有发现明显的 old hero / old package cards / old gallery / old contact 这种成对的"新旧版本并存"的情况。** 主要的重复和臃肿都集中在"所有页面塞在一个 HTML 里"这件事上。

---

## 3. 隐藏区块里的重资源（重点关注：浏览器仍会下载）

### 3a. `index.html` 内 — 隐藏 `.page` 区块里加载的媒体

| 隐藏页面 | 媒体数量 | 关键资源 | 是否会自动下载 |
|---|---|---|---|
| `#page-wavepool` | 5 | • 1 个全屏背景视频（Cloudinary，行 1554，`autoplay`）<br>• **2 个 YouTube iframe**（行 1577、1722，**没有 `loading="lazy"`**）<br>• 大量 background-image 画廊（行 1745–1753） | **是**（iframe 一定下载、autoplay 视频会预加载） |
| 7 个 `#page-session-*` | 8 个 `<video autoplay muted loop>` | 行 1886、2044、2195、2204、2354、2503、2651、2799 — 全部 Cloudinary 视频 | autoplay 通常触发 metadata 预加载 |
| `#page-packages` | 4 张 `<img>` | 行 2919、2937、2976、2983 | **是**（无 `loading="lazy"`） |
| `#page-explore` | 13 张 `<img>` | 行 3025–3137 | **是**（无 `loading="lazy"`） |
| `#page-plan` | 6 张 `<img>` | 行 3153–3243 | **是**（无 `loading="lazy"`） |
| `#page-contact` | 2 张 `<img>` | 行 3259、3376 | **是**（无 `loading="lazy"`） |

> **关键发现**：整个 `index.html` 共 **53 个 `<img>` 标签，0 个带 `loading="lazy"`**；2 个 YouTube `<iframe>` 也都没有 `loading="lazy"`。

> **建议**：给非 `#page-home` 的所有 img/iframe 加上 `loading="lazy"`，再把 8 个 session 视频的 `preload` 显式设成 `none`（或者干脆做成 click-to-play）。这是不动设计、不动文案、不删文件就能拿到的最大性能提升。

---

## 4. 引入了但没用上的"组件"

> 这是个纯静态站，没有 JS module 概念，所以"未使用组件"= 仓库里存在但没被任何页面链接的 HTML 文件。

| 文件 | 是否被引用 | 是否安全删除 | 原因 |
|---|---|---|---|
| `culture-detail-preview.html` | ❌ 没有任何 HTML 引用 | **可删**（建议先确认） | 像是早期的 culture 页设计探索版；现役版本是 `culture.html` |
| `font-pairings-preview.html` | ❌ 没有任何 HTML 引用 | **可删** | 字体方案预览稿 |
| `hero-variants-preview.html` | ❌ 没有任何 HTML 引用 | **可删** | hero 设计方案对比稿 |
| `logo-preview.html` | ❌ 没有任何 HTML 引用 | **可删** | logo 早期设计稿 |
| `logo-preview-v2.html` | ❌ 没有任何 HTML 引用 | **可删** | logo 设计稿 v2 |
| `accommodation-detail-preview.html` | ✅ `index.html:1346` | **不能删** | "Book Accommodations" 按钮跳转到这里 |
| ~~`wavepool-detail-preview.html`~~ | 已于 2026-04-26 删除 | 已删除 | 旧草稿；导航链接已改指 `index.html#wavepool`（活的 Wave Pool 页） |
| `cuisine.html` | ✅ index.html、package-2、package-3 | 不能删 | 现役页 |
| `culture.html` | ✅ index.html、package-2 | 不能删 | 现役页 |
| `golf.html` | ✅ index.html、package-3 | 不能删 | 现役页 |
| `nature.html` | ✅ 多处 | 不能删 | 现役页 |
| `package-1/2/3-*.html` | ✅ 多处 | 不能删 | 现役页 |

> **5 个 preview HTML 是清理 candidate**。删掉前建议你先确认下设计上有没有还要回头参考的，没有就可以放心移除（它们只在你电脑上和 GitHub 里占位，不上线也不影响首页）。

---

## 5. 没用到的 JavaScript / CSS

### 5a. JavaScript

`index.html` 里 4 个全局函数：`scrollWpGallery`, `showPage`, `toggleMobile`, `handleSubmit` — **全部都在用**。无未使用 JS 函数。

### 5b. CSS — 定义了但 HTML 里没用的 class

下面这些 class 在 `<style>` 里有规则，但 `<body>` 里**搜不到任何使用**。这些应该是早期版本的 section 删掉之后留下的"孤儿样式"。

| 选择器 | 行 | 推断的旧用途 | 是否安全移除 |
|---|---|---|---|
| `.natural-surf-img` | CSS 里 2 处 | 旧的 Natural Surf 区块图片样式 | **可删**（仅 CSS） |
| `.pro-card` / `.pro-photo` / `.pros-grid` / `.wp-pros` | 共 9 处规则 | 旧的"职业冲浪手介绍"区块 | **可删**（仅 CSS） |
| `.ps-logo-inline` / `.ps-logo-nav` | 各 1 处 | 旧的 PerfectSwell logo 内联样式（现在用普通 `<img>`） | **可删**（仅 CSS） |
| `.recovery-grid` / `.recovery-section` | 4 处 | 旧的 Recovery 区块布局 | **可删**（仅 CSS） |
| `.wave-type-card` / `.wave-type-level` / `.wave-types-grid` | 11 处 | 旧的"浪型介绍"区块 | **可删**（仅 CSS） |
| `.sd-video-placeholder` | 3 处（行 1058–1060） | 早期 session 视频占位符（已被真实视频替换） | **可删**（仅 CSS） |

> **总计约 30+ 行 CSS 可以清理。**这些和你说的"old activity sections / old gallery sections"在风格上吻合：HTML 已经改版重写了，但 CSS 没跟着删干净。

> 备注：以下 class 看起来"未用"实际上是 **JS 在运行时动态加上的**，**不要删**：
> - `.gallery-nav-prev` / `.gallery-nav-next` / `.gallery-strip-wrap`（行 3500–3535 由 JS 动态生成）
> - `.open`（mobile menu 和 FAQ 折叠用）
> - `.scrolled`（滚动时 nav 状态）
> - `.visible`（fade-in IntersectionObserver 用）

---

## 6. 不可见但仍在加载的视频/图片（首页打开瞬间就下载的）

按"打开首页时浏览器实际会下载、但用户看不到"来排序：

| 严重度 | 资源 | 行号 | 大小估计 | 为什么会下载 |
|---|---|---|---|---|
| 🔴 高 | YouTube iframe 1（Wave Pool 主介绍视频） | 1577 | YouTube 播放器 ~500 KB JS + 缩略图 | 没有 `loading="lazy"`，iframe 默认即时加载 |
| 🔴 高 | YouTube iframe 2（Performance 视频） | 1722 | 同上 | 同上 |
| 🔴 高 | Wave Pool 顶部背景视频（Cloudinary） | 1554 | autoplay，会下载完整视频 | autoplay + 无 `preload="none"` |
| 🟡 中 | 8 个 Session Detail autoplay 视频 | 1886/2044/2195/2204/2354/2503/2651/2799 | 各自至少下 metadata | autoplay 触发预加载 |
| 🟡 中 | `#page-explore` 13 张图（鸡尾酒 / 美食 / 自然 / 文化等） | 3025–3137 | 总 ≈ 数 MB | 没有 `loading="lazy"` |
| 🟡 中 | `#page-plan` 6 张酒店图 | 3153–3243 | 总 ≈ 1–2 MB | 同上 |
| 🟡 中 | `#page-packages` 4 张图 | 2919–2983 | 总 ≈ 1 MB | 同上 |
| 🟢 低 | `#page-contact` 2 张图 | 3259/3376 | <1 MB | 同上 |

> **不动设计、不动图、不动文案的修复方案（仅供参考，不在这次执行）**：
> 1. 给非 `#page-home` 的 ~25 个 `<img>` 加 `loading="lazy"`
> 2. 给两个 `<iframe>` 加 `loading="lazy"`
> 3. 给所有非首页 `<video>` 加 `preload="none"` 并去掉 `autoplay`（改成"点击播放"）

---

## 7. `Assets/` 里疑似没用的文件（按文件夹分组）

> 检测方法：把每个文件名（含 URL 编码版本）在所有 .html 里 grep 一遍，找不到就标为"未引用"。

> ⚠️ **重要前提**：未引用 ≠ 一定可以删。可能存在以下情况：
> - 准备给某个新页面用，但还没写 HTML
> - 是 Cloudinary 上视频的本地原始版本（你说过视频已搬到 Cloudinary）
> - 是 4K 大图的素材，留着以后做 A/B 测试

### 总览

| 类别 | 未引用文件数 | 总大小 |
|---|---|---|
| `Assets/culture` 系列 | 3 | 1.2 MB |
| `Assets/food` | 1 | 0.5 MB |
| `Assets/golf` 系列 | 10 | 6.4 MB |
| `Assets/hotel/designer hotel` | 9 | 4.8 MB |
| **`Assets/hotel/main hotel`** | **41** | **17.3 MB** |
| `Assets/hotel/outside` | 3 | 2.0 MB |
| `Assets/hotel/restaurant` | 2 | 0.8 MB |
| `Assets/nature` | 5 | 2.1 MB |
| **`Assets/ocean-surf`** | **9（含 4 个超大原始视频）** | **127 MB** |
| `Assets/recovery` | 5 | 2.1 MB |
| `Assets/surf-shop` 系列 | 23 | 5.5 MB |
| `Assets/wavepool`（杂项 + 原始视频） | 12 | 15.4 MB |
| `Assets/wavepool/详情页/*text*/` | 32 个 PNG 截图 | 21.9 MB |
| **合计** | **155 个文件** | **≈ 207 MB** |

### 重点关注

| 资源 | 大小 | 说明 | 是否安全删除 |
|---|---|---|---|
| `Assets/ocean-surf/ScreenRecording_04-15-2026 22.mov` | 35 MB | 原始屏幕录制视频，对应 Cloudinary `ScreenRecording_04-15-2026_22_atofc3.mp4` | **应该可删**（已上 Cloudinary） |
| `Assets/ocean-surf/ScreenRecording_04-15-2026 23.mov` | 45 MB | 同上 | 同上 |
| `Assets/ocean-surf/ScreenRecording_04-16-2026 16.mov` | 27 MB | 同上 | 同上 |
| `Assets/ocean-surf/01e93cc50a2157da010370039b16115f56_4610.mp4video.MP4` | 21 MB | 原始 MP4 | 同上 |
| `Assets/wavepool/88c2e2f982028a914efc5aa8d674c8.MP4` | 7.8 MB | 原始版（Cloudinary 已有压缩版） | 同上 |
| `Assets/wavepool/_compressed_88c2e2f982028a914efc5aa8d674c8.mp4` | 1.5 MB | 中间产物 | 同上 |
| `Assets/wavepool/详情页/*text*/IMG_57**.PNG`（32 个文件） | 22 MB | 7 个 session detail 的"原始文字截图"（PNG 形式的设计稿） | **可删**（HTML 是按文字 + 图片重写的，没引用这些 PNG） |
| `Assets/hotel/main hotel/*.jpg`（41 张） | 17.3 MB | 主酒店房型大杂烩；HTML 里只用到 `main-hotel-room-01.jpg` | **保守保留**（你可能想再加酒店画廊） |
| `Assets/surf-shop/community/*.jpg`（14 张） | 2.7 MB | 社区图集 | **保守保留**（看上去是有意收集的图集） |
| `Assets/golf/choose/*.jpg`（8 张） | 5.2 MB | 像是 Golf 配图候选 | **保守保留** |
| `Assets/perfectswell-logo.png` | 304 KB | 在用 | **保留** |

> **`Assets-original/` 文件夹（1.4 GB）**：已被 `.gitignore` 忽略，不会上线，仅本地占空间。属于安全资产备份，**不影响网站性能**。可以随时挪到外置硬盘释放空间。

---

## 总体清理优先级建议（按收益从高到低）

| 优先级 | 行动 | 预计效果 | 风险 |
|---|---|---|---|
| ① 最高 | 给非首页的 25 个 `<img>` 加 `loading="lazy"`；给 2 个 YouTube iframe 加 `loading="lazy"`；给 8 个 session 视频加 `preload="none"` | 首屏字节数减少 ~80%（YouTube 播放器和 25 张图都不再立刻下载） | 极低（属于浏览器原生属性，不动设计/文案） |
| ② 高 | 把 7 个 Session Detail 页（约 1066 行）和 Wave Pool 页（约 295 行）拆成独立 HTML 文件，按 `culture.html` 的模式做 | `index.html` 体积从 173 KB 砍到 ~70 KB；首屏 JS/HTML 解析时间显著下降 | 中（需要改 `showPage()` 里的链接为 `<a href="...">`，并测试导航是否还正常） |
| ③ 中 | 删 5 个 preview HTML（`logo-preview*.html`, `font-pairings-preview.html`, `hero-variants-preview.html`, `culture-detail-preview.html`） | 仓库小一点，没运行时收益 | 低（已经没人引用） |
| ④ 中 | 删 32 个 `Assets/wavepool/详情页/*text*/IMG_*.PNG`（22 MB） | 仓库瘦 22 MB，Vercel 部署快 | 低（HTML 没引用） |
| ⑤ 低 | 删 4 个原始 .mov / .mp4（127 MB，已搬 Cloudinary）+ 2 个 wavepool 原始 mp4（9 MB） | 仓库瘦 ~136 MB | 低（前提是 Cloudinary 上视频不会被误删，或本地保留另一份） |
| ⑥ 低 | 删 30+ 行 orphan CSS（`.pro-card`, `.wave-type-card`, `.recovery-grid`, `.sd-video-placeholder` 等） | 文件小几 KB | 极低（确认无 JS 动态用即可） |
| ⑦ 慎重 | `Assets/hotel/main hotel/` 41 张未引用图（17 MB）和 `Assets/surf-shop/community/` 14 张（2.7 MB） | 仓库瘦 20 MB | 中（你可能后面要做酒店/社群画廊） |

---

## 一句话收尾

**你直觉是对的——首页拖慢的不是图片本身没压缩，而是"整个网站塞在一个 HTML 里"，加上 53 个 `<img>` 全都没开 lazy load。下一步我可以按你选的优先级去具体修改，但这次只看不动。**

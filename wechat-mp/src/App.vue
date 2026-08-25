<script>
export default {
  onLaunch: function () {
    console.log('HR 技能训练营 · 小程序启动')
  },
}
</script>

<style>
/* ============================================================
   Constructivism 构成主义设计系统（严格三色体系）— 小程序版
   - 苏维埃红 #cc0000  |  纯黑 #1a1a1a  |  泛黄纸色 #f2e8d5
   - 金星色 #d4a843（点缀）  |  棕色 #8b4513（弱化）
   禁止：圆角 / 渐变 / 柔和阴影 / 玻璃态 / 过多颜色
   ============================================================ */
page {
  --sov-red: #cc0000;
  --sov-red-dark: #a80000;
  --sov-black: #1a1a1a;
  --sov-paper: #f2e8d5;
  --sov-white: #ffffff;
  --sov-gold: #d4a843;
  --sov-brown: #8b4513;

  --shadow-sm: 2px 2px 0 #1a1a1a;
  --shadow-md: 4px 4px 0 #1a1a1a;
  --shadow-lg: 6px 6px 0 #1a1a1a;

  --font-sans: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei',
    system-ui, -apple-system, sans-serif;

  background: var(--sov-paper);
  color: var(--sov-black);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.6;
  font-weight: 700;
}

view, text, button, input, rich-text { box-sizing: border-box; }

/* 标题字重由各页面 class 控制（小程序不支持 h1 等标签选择器） */

/* ============================================================
   按钮：无圆角 + 4px 边框 + 硬阴影 + Block Invasion
   ============================================================ */
.btn {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: 4px solid var(--sov-black);
  border-radius: 0;
  background: var(--sov-paper);
  color: var(--sov-black);
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .06em;
  box-shadow: var(--shadow-md);
  transition: transform 100ms linear, box-shadow 100ms linear, background-color 100ms linear;
}
.btn::after {
  border: none;
}
.btn.primary {
  background: var(--sov-red);
  border-color: var(--sov-black);
  color: var(--sov-paper);
}
.btn.ink {
  background: var(--sov-black);
  color: var(--sov-paper);
}
.btn.gold {
  background: var(--sov-gold);
  color: var(--sov-black);
}
.btn.small { padding: 6px 14px; font-size: 12.5px; box-shadow: var(--shadow-sm); }
.btn.mini { padding: 4px 12px; font-size: 12px; box-shadow: var(--shadow-sm); }
.btn[disabled] { opacity: .5; }

/* ============================================================
   卡片 / 标签徽章
   ============================================================ */
.card {
  background: var(--sov-white);
  border: 4px solid var(--sov-black);
  border-radius: 0;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.badge {
  display: inline-block;
  padding: 3px 12px;
  border: 4px solid var(--sov-black);
  border-radius: 0;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .08em;
  line-height: 1.4;
}.badge.red { background: var(--sov-red); color: var(--sov-paper); }
.badge.gold { background: var(--sov-gold); color: var(--sov-black); }
.badge.black { background: var(--sov-black); color: var(--sov-paper); }

/* 网格纹理（SVG data URI 在小程序可用） */
.grid-pattern {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28'%3E%3Cpath d='M28 0H0v28' fill='none' stroke='%231a1a1a' stroke-opacity='0.07'/%3E%3C/svg%3E");
  background-size: 28px 28px;
}
.grid-pattern.on-dark {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28'%3E%3Cpath d='M28 0H0v28' fill='none' stroke='%23f2e8d5' stroke-opacity='0.10'/%3E%3C/svg%3E");
}

/* ============================================================
   章节 Markdown 渲染说明：
   小程序 rich-text 为原生组件，内部节点无法被外部 CSS 命中，
   所有构成主义样式已由 MarkdownBody.vue 内联到生成 HTML 中。
   ============================================================ */

/* 底部安全区 */
.safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
</style>

// ============================================================
// 轻量 Markdown → HTML 渲染器（小程序 rich-text 专用）
// 纯 ES5 语法，无第三方依赖，兼容老安卓 JSCore。
// 支持：标题 / 段落 / 粗体 / 斜体 / 行内代码 / 引用 /
//       有序·无序列表 / 表格 / 分隔线 / 换行
// 所有样式内联（rich-text 内部节点无法被外部 CSS 命中）
// ============================================================

const BLACK = '#1a1a1a'
const RED = '#cc0000'
const RED_DARK = '#a80000'
const PAPER = '#f2e8d5'
const WHITE = '#ffffff'

function st(rules) {
  const parts = []
  for (const k in rules) {
    if (Object.prototype.hasOwnProperty.call(rules, k)) {
      parts.push(k + ':' + rules[k])
    }
  }
  return parts.join(';')
}

// 转义 HTML 特殊字符
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// 行内解析：**粗体**、*斜体*、`行内代码`、链接 [文字](url)
function inline(text) {
  let out = esc(text)
  // 行内代码（先处理，避免代码内的标记被解析）
  out = out.replace(/`([^`]+)`/g, (m, code) => {
    return '<code style="' + st({ background: PAPER, border: '2px solid ' + BLACK, padding: '1px 6px', 'font-size': '13px', 'font-weight': '700' }) + '">' + code + '</code>'
  })
  // 链接
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, txt, url) => {
    return '<a style="color:' + RED_DARK + ';font-weight:900">' + txt + '</a>'
  })
  // 粗体
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight:900">$1</strong>')
  // 斜体
  out = out.replace(/\*([^*]+)\*/g, '<em style="font-style:normal;color:' + RED_DARK + ';font-weight:900">$1</em>')
  return out
}

// 主渲染：markdown 文本 → HTML 字符串
export function renderMarkdown(md) {
  if (!md) return ''
  const lines = String(md).split(/\r?\n/)
  const out = []
  let i = 0
  const n = lines.length

  function isTableSep(line) {
    // | --- | :---: | 分隔行
    return /^\s*\|[\s:|-]+\|\s*$/.test(line) && line.indexOf('-') >= 0
  }

  function parseTable(startIdx) {
    // 表头行 + 分隔行 + 数据行
    const headerCells = lines[startIdx]
      .split('|').map((x) => x.trim()).filter((x) => x !== '')
    const rows = []
    let r = startIdx + 2
    while (r < n) {
      const line = lines[r]
      if (!line.trim() || !/^\s*\|/.test(line)) break
      const cells = line.split('|').map((x) => x.trim()).filter((x) => x !== '')
      rows.push(cells)
      r++
    }
    let html = '<table style="' + st({ width: '100%', 'border-collapse': 'collapse', margin: '16px 0', 'font-size': '14px', color: BLACK }) + '">'
    html += '<tr>'
    for (let c = 0; c < headerCells.length; c++) {
      html += '<th style="' + st({ background: BLACK, color: PAPER, 'font-weight': '900', 'text-align': 'left', padding: '8px 12px', border: '2px solid ' + BLACK }) + '">' + inline(headerCells[c]) + '</th>'
    }
    html += '</tr>'
    for (let ri = 0; ri < rows.length; ri++) {
      html += '<tr>'
      for (let c = 0; c < headerCells.length; c++) {
        const cell = rows[ri][c] || ''
        html += '<td style="' + st({ padding: '8px 12px', border: '2px solid ' + BLACK, background: WHITE, color: BLACK }) + '">' + inline(cell) + '</td>'
      }
      html += '</tr>'
    }
    html += '</table>'
    return { html, next: r }
  }

  while (i < n) {
    const line = lines[i]
    const trimmed = line.trim()

    // 空行
    if (!trimmed) { i++; continue }

    // 分隔线 ---
    if (/^-{3,}$/.test(trimmed) || /^\*{3,}$/.test(trimmed)) {
      out.push('<hr style="' + st({ border: 'none', 'border-top': '4px solid ' + BLACK, margin: '22px 0' }) + '"/>')
      i++; continue
    }

    // 表格
    if (/^\s*\|/.test(trimmed) && i + 1 < n && isTableSep(lines[i + 1])) {
      const t = parseTable(i)
      out.push(t.html)
      i = t.next
      continue
    }

    // 标题 # ## ###
    const h = trimmed.match(/^(#{1,3})\s+(.+)$/)
    if (h) {
      const depth = h[1].length
      const txt = inline(h[2])
      if (depth === 1) {
        out.push('<h1 style="' + st({ 'font-size': '26px', margin: '0 0 18px', 'padding-bottom': '10px', 'border-bottom': '4px solid ' + BLACK, color: BLACK, 'font-weight': '900', 'line-height': '1.25' }) + '">' + txt + '</h1>')
      } else if (depth === 2) {
        out.push('<h2 style="' + st({ 'font-size': '20px', margin: '28px 0 12px', 'padding-left': '12px', 'border-left': '8px solid ' + RED, color: BLACK, 'font-weight': '900', 'line-height': '1.25' }) + '">' + txt + '</h2>')
      } else {
        out.push('<h3 style="' + st({ 'font-size': '17px', margin: '22px 0 10px', color: BLACK, 'font-weight': '900', 'line-height': '1.25' }) + '">' + txt + '</h3>')
      }
      i++; continue
    }

    // 引用块 >（支持多行连续 >）
    if (/^\s*>/.test(trimmed)) {
      const quoteLines = []
      while (i < n && /^\s*>/.test(lines[i].trim())) {
        let ql = lines[i].replace(/^\s*>\s?/, '')
        quoteLines.push(ql)
        i++
      }
      const body = quoteLines.map((ql) => {
        if (/^#{1,3}\s/.test(ql.trim())) return inline(ql.trim())
        return '<p style="' + st({ margin: '0 0 8px', color: BLACK }) + '">' + inline(ql) + '</p>'
      }).join('')
      out.push('<blockquote style="' + st({ margin: '16px 0', padding: '12px 16px', background: PAPER, border: '3px solid ' + BLACK, 'border-left': '8px solid ' + RED, 'font-weight': '700' }) + '">' + body + '</blockquote>')
      continue
    }

    // 无序列表 - / * / •
    if (/^\s*[-*•]\s+/.test(trimmed)) {
      const items = []
      while (i < n && /^\s*[-*•]\s+/.test(lines[i].trim())) {
        items.push(inline(lines[i].replace(/^\s*[-*•]\s+/, '')))
        i++
      }
      const liHtml = items.map((it) => '<li style="' + st({ 'margin-bottom': '6px', color: BLACK }) + '">' + it + '</li>').join('')
      out.push('<ul style="' + st({ 'padding-left': '24px', margin: '0 0 14px' }) + '">' + liHtml + '</ul>')
      continue
    }

    // 有序列表 1. / 1）
    const ol = trimmed.match(/^\s*\d+[.)]\s+(.+)$/)
    if (ol) {
      const items = []
      while (i < n) {
        const m = lines[i].match(/^\s*\d+[.)]\s+(.+)$/)
        if (!m) break
        items.push(inline(m[1]))
        i++
      }
      const liHtml = items.map((it) => '<li style="' + st({ 'margin-bottom': '6px', color: BLACK }) + '">' + it + '</li>').join('')
      out.push('<ol style="' + st({ 'padding-left': '24px', margin: '0 0 14px' }) + '">' + liHtml + '</ol>')
      continue
    }

    // 普通段落：合并连续非空行
    const paraLines = []
    while (i < n && lines[i].trim() && !/^\s*[-*•]\s+/.test(lines[i].trim()) && !/^\s*\d+[.)]\s+/.test(lines[i].trim()) && !/^\s*>/.test(lines[i].trim()) && !/^#{1,3}\s/.test(lines[i].trim()) && !/^-{3,}$/.test(lines[i].trim()) && !/^\s*\|/.test(lines[i].trim())) {
      paraLines.push(lines[i].trim())
      i++
    }
    if (paraLines.length) {
      const txt = paraLines.map((p) => inline(p)).join('<br/>')
      out.push('<p style="' + st({ margin: '0 0 14px', color: BLACK }) + '">' + txt + '</p>')
      continue
    }

    i++
  }

  return out.join('')
}

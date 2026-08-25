<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: { type: String, default: '' },
})

// ============================================================
// 小程序 rich-text 内部节点无法被外部 CSS 命中（原生组件），
// 因此通过 marked 自定义 renderer 将构成主义样式内联到 HTML。
// marked v12 默认 renderer 使用旧式字符串签名：
//   heading(text, depth) / paragraph(text) / strong(text) ...
// text 参数为已渲染好的子内容字符串。
// 微信 rich-text 支持的标签：p/h1-h6/ul/ol/li/blockquote/
// table/thead/tbody/tr/th/td/strong/em/code/pre/hr/br/div/span
// ============================================================
const BLACK = '#1a1a1a'
const RED = '#cc0000'
const RED_DARK = '#a80000'
const PAPER = '#f2e8d5'
const WHITE = '#ffffff'

function st(rules) {
  return Object.entries(rules)
    .map(([k, v]) => `${k}:${v}`)
    .join(';')
}

const renderer = {
  heading(text, depth) {
    if (depth === 1) {
      return `<h1 style="${st({ 'font-size': '26px', 'margin': '0 0 18px', 'padding-bottom': '10px', 'border-bottom': '4px solid ' + BLACK, 'color': BLACK, 'font-weight': '900', 'line-height': '1.25' })}">${text}</h1>`
    }
    if (depth === 2) {
      return `<h2 style="${st({ 'font-size': '20px', 'margin': '28px 0 12px', 'padding-left': '12px', 'border-left': '8px solid ' + RED, 'color': BLACK, 'font-weight': '900', 'line-height': '1.25' })}">${text}</h2>`
    }
    return `<h3 style="${st({ 'font-size': '17px', 'margin': '22px 0 10px', 'color': BLACK, 'font-weight': '900', 'line-height': '1.25' })}">${text}</h3>`
  },
  paragraph(text) {
    return `<p style="${st({ 'margin': '0 0 14px', 'color': BLACK })}">${text}</p>`
  },
  strong(text) {
    return `<strong style="font-weight:900">${text}</strong>`
  },
  em(text) {
    return `<em style="${st({ 'font-style': 'normal', 'color': RED_DARK, 'font-weight': '900' })}">${text}</em>`
  },
  codespan(code) {
    return `<code style="${st({ 'background': PAPER, 'border': '2px solid ' + BLACK, 'padding': '1px 6px', 'font-size': '13px', 'font-weight': '700' })}">${code}</code>`
  },
  code(code) {
    return `<pre style="${st({ 'background': BLACK, 'color': PAPER, 'padding': '14px', 'overflow-x': 'auto', 'border': '3px solid ' + BLACK, 'font-size': '13px', 'font-weight': '700' })}"><code style="${st({ 'background': 'transparent', 'border': 'none', 'color': PAPER, 'padding': '0' })}">${code}</code></pre>`
  },
  blockquote(quote) {
    return `<blockquote style="${st({ 'margin': '16px 0', 'padding': '12px 16px', 'background': PAPER, 'border': '3px solid ' + BLACK, 'border-left': '8px solid ' + RED, 'font-weight': '700' })}">${quote}</blockquote>`
  },
  list(body, ordered) {
    const tag = ordered ? 'ol' : 'ul'
    return `<${tag} style="${st({ 'padding-left': '24px', 'margin': '0 0 14px' })}">${body}</${tag}>`
  },
  listitem(text) {
    return `<li style="${st({ 'margin-bottom': '6px', 'color': BLACK })}">${text}</li>`
  },
  table(header, body) {
    return `<table style="${st({ 'width': '100%', 'border-collapse': 'collapse', 'margin': '16px 0', 'font-size': '14px', 'color': BLACK })}">${header}${body}</table>`
  },
  tablerow(content) {
    return `<tr>${content}</tr>`
  },
  tablecell(content, flags) {
    if (flags.header) {
      return `<th style="${st({ 'background': BLACK, 'color': PAPER, 'font-weight': '900', 'text-align': 'left', 'padding': '8px 12px', 'border': '2px solid ' + BLACK })}">${content}</th>`
    }
    return `<td style="${st({ 'padding': '8px 12px', 'border': '2px solid ' + BLACK, 'background': WHITE, 'color': BLACK })}">${content}</td>`
  },
  hr() {
    return `<hr style="${st({ 'border': 'none', 'border-top': '4px solid ' + BLACK, 'margin': '22px 0' })}">`
  },
  br() {
    return '<br/>'
  },
  text(text) {
    return text
  },
  html(html) {
    return html
  },
  link(href, title, text) {
    return `<a style="color:${RED_DARK};font-weight:900">${text}</a>`
  },
}

marked.use({ renderer })

marked.setOptions({
  gfm: true,
  breaks: true,
})

const html = computed(() => marked.parse(props.content || ''))
</script>

<template>
  <rich-text class="md-body" :nodes="html"></rich-text>
</template>

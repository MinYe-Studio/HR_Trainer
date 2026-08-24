<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: { type: String, default: '' },
})

marked.setOptions({
  gfm: true,
  breaks: true,
})

const html = computed(() => marked.parse(props.content || ''))
</script>

<template>
  <!-- 章节 Markdown 渲染（构成主义阅读排版） -->
  <div class="md-body" v-html="html"></div>
</template>

<style scoped>
.md-body {
  font-size: 15px;
  line-height: 1.85;
  color: var(--sov-black);
  max-width: 78ch;
}
.md-body :deep(h1) {
  font-size: 26px;
  margin: 0 0 18px;
  padding-bottom: 10px;
  border-bottom: 4px solid var(--sov-black);
}
.md-body :deep(h2) {
  font-size: 20px;
  margin: 28px 0 12px;
  padding-left: 12px;
  border-left: 8px solid var(--sov-red);
}
.md-body :deep(h3) {
  font-size: 17px;
  margin: 22px 0 10px;
}
.md-body :deep(p) { margin: 0 0 14px; }
.md-body :deep(strong) { font-weight: 900; }
.md-body :deep(em) { font-style: normal; color: var(--sov-red-dark); font-weight: 900; }
.md-body :deep(ul), .md-body :deep(ol) { padding-left: 24px; margin: 0 0 14px; }
.md-body :deep(li) { margin-bottom: 6px; }
.md-body :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  background: var(--sov-paper);
  border: 3px solid var(--sov-black);
  border-left: 8px solid var(--sov-red);
  font-weight: 700;
}
.md-body :deep(blockquote p) { margin: 0; }
.md-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 14px;
}
.md-body :deep(th) {
  background: var(--sov-black);
  color: var(--sov-paper);
  font-weight: 900;
  text-align: left;
  padding: 8px 12px;
  border: 2px solid var(--sov-black);
}
.md-body :deep(td) {
  padding: 8px 12px;
  border: 2px solid var(--sov-black);
  background: var(--sov-white);
}
.md-body :deep(code) {
  background: var(--sov-paper);
  border: 2px solid var(--sov-black);
  padding: 1px 6px;
  font-size: 13px;
  font-weight: 700;
}
.md-body :deep(pre) {
  background: var(--sov-black);
  color: var(--sov-paper);
  padding: 14px;
  overflow-x: auto;
  border: 3px solid var(--sov-black);
}
.md-body :deep(pre code) {
  background: transparent;
  border: none;
  color: var(--sov-paper);
  padding: 0;
}
.md-body :deep(hr) {
  border: none;
  border-top: 4px solid var(--sov-black);
  margin: 22px 0;
}
</style>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../utils/markdown'

const props = defineProps({
  content: { type: String, default: '' },
})

// 使用自研轻量渲染器（纯 ES5，兼容老安卓 JSCore），
// 样式内联到 HTML，rich-text 直接渲染。
const html = computed(() => renderMarkdown(props.content || ''))
</script>

<template>
  <rich-text class="md-body" :nodes="html"></rich-text>
</template>

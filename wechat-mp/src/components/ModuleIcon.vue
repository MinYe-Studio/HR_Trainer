<script setup>
import { computed } from 'vue'

// 模块首字（构成主义方块图标）
const GLYPHS = {
  recruitment: '招',
  performance: '绩',
  compensation: '薪',
  'employee-relations': '员',
  training: '培',
  'labor-law': '法',
}

const props = defineProps({
  code: { type: String, required: true },
  size: { type: Number, default: 52 },
  tone: { type: String, default: 'ink' }, // ink | red | gold | paper
})

const glyph = computed(() => GLYPHS[props.code] || '模')
</script>

<template>
  <view
    class="micon"
    :class="'tone-' + tone"
    :style="{ width: size + 'px', height: size + 'px' }"
  >
    <text class="glyph" :style="{ fontSize: Math.round(size * 0.46) + 'px' }">{{ glyph }}</text>
  </view>
</template>

<style scoped>
.micon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 3px solid var(--sov-black);
  background: transparent;
  color: var(--sov-black);
}
.tone-red { background: var(--sov-red); color: var(--sov-paper); }
.tone-gold { background: var(--sov-gold); color: var(--sov-black); }
.tone-paper { background: var(--sov-paper); color: var(--sov-black); }
.tone-ink { background: var(--sov-black); color: var(--sov-paper); }
.glyph {
  font-weight: 900;
  line-height: 1;
  transform: translateY(-1px);
}
</style>

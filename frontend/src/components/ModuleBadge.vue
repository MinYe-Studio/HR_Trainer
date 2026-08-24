<script setup>
import { computed } from 'vue'
import { iconOf } from '../utils/icons'

// 徽章成长四阶段：
// 0=未开始(灰淡) 1=轮廓(学完1章) 2=标志(50%章节) 3=点亮(全部章节) 4=闪耀(考核通过)
const props = defineProps({
  code: { type: String, required: true },
  name: { type: String, default: '' },
  chaptersCompleted: { type: Number, default: 0 },
  chaptersTotal: { type: Number, default: 0 },
  examPassed: { type: Boolean, default: false },
  size: { type: Number, default: 46 },
})

const level = computed(() => {
  if (props.examPassed) return 4
  const total = props.chaptersTotal
  if (total <= 0) return 0
  const done = props.chaptersCompleted
  if (done >= total) return 3
  if (done >= Math.ceil(total / 2)) return 2
  if (done >= 1) return 1
  return 0
})

const levelLabel = ['未解锁', '轮廓', '标志', '点亮', '闪耀']

const showIcon = computed(() => level.value >= 2)
const showFill = computed(() => level.value >= 3)
</script>

<template>
  <div
    class="mbadge"
    :class="['lv' + level]"
    :style="{ width: size + 'px', height: size + 'px' }"
    :title="name ? `${name}（${levelLabel[level]}）` : ''"
  >
    <span v-if="showIcon" class="mb-icon" v-html="iconOf(code, Math.round(size * 0.5))"></span>
    <span v-if="level >= 4" class="mb-check">✓</span>
    <span v-if="level === 0" class="mb-lock">?</span>
  </div>
</template>

<style scoped>
.mbadge {
  position: relative;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
  transition: all .3s ease;
}
.mb-icon { display: inline-flex; align-items: center; justify-content: center; }
.mb-icon :deep(svg) { display: block; }

/* 0 未解锁：灰淡虚线框 */
.lv0 {
  border: 3px dashed var(--sov-border-strong, #c3d4dc);
  background: rgba(255,255,255,.15);
  opacity: .55;
}
.lv0 .mb-lock {
  font-size: 12px; font-weight: 900; color: var(--sov-ink-3, #93a1b1);
}

/* 1 轮廓：纸色实线空壳 */
.lv1 {
  border: 3px solid var(--sov-paper);
  background: transparent;
}

/* 2 标志：图标浮现（金底淡） */
.lv2 {
  border: 3px solid var(--sov-paper);
  background: var(--sov-gold);
  color: var(--sov-black);
}

/* 3 点亮：金色填充 */
.lv3 {
  border: 4px solid var(--sov-black);
  background: var(--sov-gold);
  color: var(--sov-black);
  box-shadow: var(--shadow-sm);
}

/* 4 闪耀：发光 + 闪烁 + 扫光 */
.lv4 {
  border: 4px solid var(--sov-black);
  background: var(--sov-gold);
  color: var(--sov-black);
  box-shadow: 0 0 10px 2px rgba(212, 168, 67, .9), 0 0 22px 6px rgba(212, 168, 67, .45);
  animation: badge-glow 1.6s ease-in-out infinite;
}
.lv4::after {
  content: '';
  position: absolute; top: 0; bottom: 0;
  width: 40%;
  border-radius: 50%;
  background: rgba(255, 255, 255, .45);
  transform: translateX(-220%) skewX(-20deg);
  animation: badge-shine 2.2s ease-in-out infinite;
}
@keyframes badge-glow {
  0%, 100% { box-shadow: 0 0 10px 2px rgba(212,168,67,.9), 0 0 22px 6px rgba(212,168,67,.45); }
  50% { box-shadow: 0 0 16px 4px rgba(212,168,67,1), 0 0 34px 10px rgba(212,168,67,.7); }
}
@keyframes badge-shine {
  0%, 55% { transform: translateX(-220%) skewX(-20deg); }
  85%, 100% { transform: translateX(320%) skewX(-20deg); }
}
.mb-check {
  position: absolute; top: -4px; right: -4px;
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 2px solid var(--sov-paper);
  font-size: 11px; font-weight: 900;
}
</style>

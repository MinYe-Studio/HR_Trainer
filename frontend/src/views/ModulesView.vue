<script setup>
import client from '../api/client'
import { onMounted, ref } from 'vue'
import { iconOf } from '../utils/icons'

// 六大技能模块（按个性化学习路径排序）
const modules = ref([])

onMounted(async () => {
  try {
    const [data, path] = await Promise.all([
      client.get('/modules'),
      client.get('/learning-path').catch(() => ({ module_codes: [] })),
    ])
    const pathCodes = path.module_codes || []
    const byCode = {}
    data.forEach((m) => { byCode[m.code] = m })
    const ordered = pathCodes.map((c) => byCode[c]).filter(Boolean)
    data.forEach((m) => { if (!pathCodes.includes(m.code)) ordered.push(m) })
    modules.value = ordered
  } catch {
    modules.value = [
      { code: 'recruitment', name: '招聘与面试' },
      { code: 'performance', name: '绩效管理' },
      { code: 'compensation', name: '薪酬福利' },
      { code: 'employee-relations', name: '员工关系' },
      { code: 'training', name: '培训与人才发展' },
      { code: 'labor-law', name: '劳动法与合规' },
    ]
  }
})
</script>

<template>
  <div class="modules">
    <div class="head">
      <h1>技能模块</h1>
      <RouterLink to="/tasks" class="head-link">学习路径 ▸</RouterLink>
    </div>
    <p class="tip">按学习路径学习：讲解 → 训练 → 考核</p>

    <div class="grid">
      <RouterLink
        v-for="(m, i) in modules"
        :key="m.code"
        :to="`/modules/${m.code}`"
        class="mcard"
      >
        <span class="step">{{ i + 1 }}</span>
        <div class="icon" v-html="iconOf(m.code, 24)"></div>
        <div class="minfo">
          <h3>{{ m.name }}</h3>
          <span class="cnt">{{ (m.chapters?.length || 0) }} 章</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.modules h1 { margin: 0; font-size: 20px; }
.head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px; }
.head-link { font-size: 12.5px; font-weight: 900; color: var(--sov-red-dark); }
.tip { margin: 0 0 12px; color: var(--sov-brown); font-size: 12px; font-weight: 700; }

/* 紧凑网格：一屏可容纳 6 个模块 */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.mcard {
  position: relative;
  display: flex; align-items: center; gap: 12px;
  background: var(--sov-white);
  border: 3px solid var(--sov-black);
  border-radius: 0;
  box-shadow: var(--shadow-sm);
  padding: 16px 14px;
  text-decoration: none; color: inherit;
  transition: transform 100ms linear, box-shadow 100ms linear;
}
.mcard:hover { transform: translate(2px, 2px); box-shadow: none; }
.step {
  position: absolute; top: -8px; left: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 24px; height: 24px; padding: 0 5px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 2px solid var(--sov-black);
  font-size: 12px; font-weight: 900;
}
.icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 52px; height: 52px; flex-shrink: 0;
  border: 3px solid var(--sov-black);
  color: var(--sov-black);
  background: transparent;
}
.icon :deep(svg) { display: block; }
.minfo { flex: 1; min-width: 0; }
.minfo h3 { margin: 0; font-size: 15.5px; line-height: 1.3; }
.cnt { font-size: 11px; font-weight: 900; color: var(--sov-brown); }

@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(3, 1fr); gap: 14px; }
  .mcard { padding: 18px; }
  .minfo h3 { font-size: 16.5px; }
}
</style>

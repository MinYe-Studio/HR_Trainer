<script setup>
import client from '../api/client'
import { onMounted, ref } from 'vue'

// 六大技能模块线稿图标（黑色 stroke，无填充）
const ICONS = {
  recruitment: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/>',
  'labor-law': '<path d="M12 3v17"/><path d="M4 8h16"/><path d="M4 8l-2.5 6"/><path d="M20 8l2.5 6"/><path d="M1.5 14h5"/><path d="M17.5 14h5"/><path d="M12 20v1.5"/><path d="M9 21.5h6"/>',
  performance: '<path d="M4 20h16"/><path d="M7.5 20v-4"/><path d="M12 20v-8"/><path d="M16.5 20v-12"/>',
  compensation: '<circle cx="12" cy="12" r="8"/><path d="M9.5 8 12 13.5 14.5 8"/><path d="M9.5 13h5"/>',
  'employee-relations': '<circle cx="9" cy="8" r="3"/><path d="M4 19.5c.7-3.4 2.8-5.2 5-5.2s4.3 1.8 5 5.2"/><circle cx="16" cy="9.5" r="2.5"/><path d="M13 16.5c.4-2.4 1.7-3.7 3-3.7s2.6 1.3 3 3.7"/>',
  training: '<path d="M3 5.5c2.5-.4 5 .2 7 2.2v12c-2-2-4.5-2.6-7-2.2v-12z"/><path d="M21 5.5c-2.5-.4-5 .2-7 2.2v12c2-2 4.5-2.6 7-2.2v-12z"/>',
}

function iconOf(code) {
  const body = ICONS[code] || ICONS.recruitment
  return `<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`
}

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
    // 按学习路径排序，缺失的模块追加到末尾
    const ordered = pathCodes.map((c) => byCode[c]).filter(Boolean)
    data.forEach((m) => { if (!pathCodes.includes(m.code)) ordered.push(m) })
    modules.value = ordered
  } catch {
    // 骨架阶段：接口未实现时使用静态占位
    modules.value = [
      { code: 'recruitment', name: '招聘与面试', description: '岗位需求分析、简历筛选、结构化面试、录用决策' },
      { code: 'performance', name: '绩效管理', description: 'KPI与OKR、绩效面谈、评估流程设计' },
      { code: 'compensation', name: '薪酬福利', description: '薪酬结构设计、岗位价值评估、福利体系' },
      { code: 'employee-relations', name: '员工关系', description: '入职管理、沟通与冲突、离职面谈' },
      { code: 'training', name: '培训与人才发展', description: '培训需求分析、计划制定、人才梯队' },
      { code: 'labor-law', name: '劳动法与合规', description: '劳动合同、工时加班、解除终止、争议处理' },
    ]
  }
})
</script>

<template>
  <div class="modules">
    <div class="head">
      <h1>技能模块</h1>
      <span class="head-bar red"></span>
    </div>
    <p class="tip">按你的学习路径学习：先学讲解，再做训练，最后参加模块考核。可在「教学任务」页自定义学习顺序。</p>

    <div class="grid">
      <RouterLink
        v-for="(m, i) in modules"
        :key="m.code"
        :to="`/modules/${m.code}`"
        class="mcard"
      >
        <div class="step-no">{{ i + 1 }}</div>
        <div class="icon" v-html="iconOf(m.code)"></div>
        <h3>{{ m.name }}</h3>
        <p>{{ m.description }}</p>
        <span class="badge" :class="m.chapters?.length ? 'red' : 'black'">
          {{ m.chapters?.length ? '内容已就绪' : '内容建设中' }}
        </span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.modules h1 { margin: 0 0 4px; }
.head { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.head-bar { display: inline-block; width: 46px; height: 8px; border: 4px solid var(--sov-black); }
.head-bar.red { background: var(--sov-red); }
.tip { margin: 0 0 24px; color: var(--sov-brown); font-weight: 700; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.mcard {
  display: block; background: var(--sov-white);
  border: 4px solid var(--sov-black);
  border-radius: 0;
  box-shadow: var(--shadow-lg);
  padding: 22px; text-decoration: none; color: inherit;
  transition: transform 100ms linear, box-shadow 100ms linear;
  position: relative;
}
.mcard:hover {
  transform: translate(3px, 3px);
  box-shadow: var(--shadow-sm);
}
.mcard:active {
  transform: translate(5px, 5px);
  box-shadow: none;
}
.step-no {
  position: absolute; top: 14px; right: 14px;
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px;
  background: var(--sov-black); color: var(--sov-paper);
  font-size: 15px; font-weight: 900;
  border: 3px solid var(--sov-black);
}
/* 线稿图标：无背景，黑色描边 */
.icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 48px; height: 48px;
  border: 4px solid var(--sov-black);
  border-radius: 0;
  color: var(--sov-black);
  background: transparent;
}
.icon :deep(svg) { display: block; }
.mcard h3 { margin: 14px 0 6px; font-size: 18px; }
.mcard p { margin: 0 0 16px; color: var(--sov-brown); font-size: 13px; line-height: 1.6; }
</style>

<script setup>
import { onMounted, ref } from 'vue'
import client from '../../api/client'
import ModuleIcon from '../../components/ModuleIcon.vue'
import TabBar from '../../components/TabBar.vue'

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

function goDetail(code) {
  uni.navigateTo({ url: `/pages/modules/detail?code=${code}` })
}
function goTasks() {
  uni.navigateTo({ url: '/pages/tasks/index' })
}
</script>

<template>
  <view class="modules">
    <view class="head">
      <text class="head-title">技能模块</text>
      <text class="head-link" @click="goTasks">学习路径 ▸</text>
    </view>
    <text class="tip">按学习路径学习：讲解 → 训练 → 考核</text>

    <view class="grid">
      <view
        v-for="(m, i) in modules"
        :key="m.code"
        class="mcard"
        @click="goDetail(m.code)"
      >
        <view class="step"><text>{{ i + 1 }}</text></view>
        <ModuleIcon :code="m.code" :size="52" tone="paper" />
        <view class="minfo">
          <text class="mname">{{ m.name }}</text>
          <text class="cnt">{{ (m.chapters?.length || 0) }} 章</text>
        </view>
      </view>
    </view>

    <TabBar current="modules" />
  </view>
</template>

<style scoped>
.modules { display: flex; flex-direction: column; gap: 12px; padding: 14px 14px calc(80px + env(safe-area-inset-bottom)); }
.head-title { font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: .02em; }
.head { display: flex; align-items: center; justify-content: space-between; }
.head-link { font-size: 12.5px; font-weight: 900; color: var(--sov-red-dark); }
.tip { color: var(--sov-brown); font-size: 12px; font-weight: 700; display: block; }

/* 紧凑网格 */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.mcard {
  position: relative;
  display: flex; align-items: center; gap: 12px;
  background: var(--sov-white);
  border: 3px solid var(--sov-black);
  box-shadow: var(--shadow-sm);
  padding: 16px 14px;
}
.step {
  position: absolute; top: -8px; left: 8px;
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 24px; height: 24px; padding: 0 5px;
  background: var(--sov-red); color: var(--sov-paper);
  border: 2px solid var(--sov-black);
  font-size: 12px; font-weight: 900;
}
.minfo { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.mname { font-size: 15.5px; font-weight: 900; line-height: 1.3; display: block; }
.cnt { font-size: 11px; font-weight: 900; color: var(--sov-brown); display: block; }
</style>

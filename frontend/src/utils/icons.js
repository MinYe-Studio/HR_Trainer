// 六大技能模块线稿图标（黑色 stroke，无填充）+ 徽章辅助
export const ICONS = {
  recruitment: '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/>',
  performance: '<path d="M4 20h16"/><path d="M7.5 20v-4"/><path d="M12 20v-8"/><path d="M16.5 20v-12"/>',
  compensation: '<circle cx="12" cy="12" r="8"/><path d="M9.5 7.5 12 13.5 14.5 7.5"/><path d="M12 13.5v4"/><path d="M9.5 11h5"/>',
  'employee-relations': '<circle cx="9" cy="8" r="3"/><path d="M4 19.5c.7-3.4 2.8-5.2 5-5.2s4.3 1.8 5 5.2"/><circle cx="16" cy="9.5" r="2.5"/><path d="M13 16.5c.4-2.4 1.7-3.7 3-3.7s2.6 1.3 3 3.7"/>',
  training: '<path d="M3 5.5c2.5-.4 5 .2 7 2.2v12c-2-2-4.5-2.6-7-2.2v-12z"/><path d="M21 5.5c-2.5-.4-5 .2-7 2.2v12c2-2 4.5-2.6 7-2.2v-12z"/>',
  'labor-law': '<path d="M12 3v17"/><path d="M4 8h16"/><path d="M4 8l-2.5 6"/><path d="M20 8l2.5 6"/><path d="M1.5 14h5"/><path d="M17.5 14h5"/><path d="M12 20v1.5"/><path d="M9 21.5h6"/>',
}

export const MODULE_NAMES = {
  recruitment: '招聘与面试',
  performance: '绩效管理',
  compensation: '薪酬福利',
  'employee-relations': '员工关系',
  training: '培训与人才发展',
  'labor-law': '劳动法与合规',
}

export function iconOf(code, size = 26) {
  const body = ICONS[code] || ICONS.recruitment
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`
}

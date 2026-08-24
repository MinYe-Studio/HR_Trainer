// 单机模式本地数据层全流程测试（Node 环境）
// 用法：cd frontend && node test-local.mjs
const store = {}
globalThis.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v) },
  removeItem: (k) => { delete store[k] },
}

const { localApi } = await import('./src/api/localApi.js')
const content = (await import('./src/data/app-content.js')).default
const realAnswers = {}
content.questions.forEach((q) => { realAnswers[q.id] = q.answer })

const client = {
  get: (p) => localApi.get(p),
  post: (p, b) => localApi.post(p, b),
  put: (p, b) => localApi.put(p, b),
}

let ok = 0, fail = 0
function check(name, cond, extra = '') {
  if (cond) { ok++; console.log(`  ✅ ${name} ${extra}`) }
  else { fail++; console.log(`  ❌ ${name} ${extra}`) }
}

console.log('=== 单机模式全流程 ===')

// 1. 档案
const me = await client.get('/auth/me')
check('本地档案', me.nickname === '学员')
const renamed = await client.put('/auth/me', { nickname: 'iOS学员' })
check('昵称修改', renamed.nickname === 'iOS学员')

// 2. 摸底测试
const pq = await client.get('/placement/questions')
check('摸底抽题30(6模块各5)', pq.length === 30 && new Set(pq.map(q => q.module_code)).size === 6)
const pq2 = await client.get('/placement/questions')
check('随机抽题(两次不同)', JSON.stringify(pq.map(q=>q.id).sort()) !== JSON.stringify(pq2.map(q=>q.id).sort()))
const answers = {}
pq.forEach(q => { answers[q.id] = realAnswers[q.id] })
const pl = await client.post('/placement/submit', { question_ids: pq.map(q=>q.id), answers })
check('摸底全对100分', pl.total_score === 100, `(${pl.total_score})`)
const latest = await client.get('/placement/latest')
check('摸底latest', latest && latest.total_score === 100)

// 3. 教学任务
const tasks = await client.get('/placement/tasks')
check('教学任务6项', tasks.tasks.length === 6 && tasks.has_placement)

// 4. 模块/章节
const mods = await client.get('/modules')
check('模块列表6个', mods.length === 6)
const perf = await client.get('/modules/performance')
check('绩效模块3章', perf.chapters.length === 3)
const ch1 = perf.chapters[0]
const chapter = await client.get(`/modules/performance/chapters/${ch1.id}`)
check('章节内容(案例驱动)', chapter.content.includes('案例引入') && chapter.content.includes('费曼自检'))

// 5. 进度
await client.post('/progress/complete', { chapter_id: ch1.id, completed: true })
const prog = await client.get('/progress')
check('进度标记', prog.chapter_progress[ch1.id]?.completed === true)

// 6. 训练（全对 → 自动完成）
const practiceQs = await client.get(`/modules/performance/chapters/${ch1.id}/practice`)
check('训练题(7+含案例)', practiceQs.length >= 7 && practiceQs.some(q => q.category === 'practice_case'))
const pAns = {}
practiceQs.forEach(q => { pAns[q.id] = realAnswers[q.id] })
const pr = await client.post('/practice/submit', { chapter_id: ch1.id, answers: pAns })
check('训练满分', pr.score === 100, `(${pr.score}分)`)
const progAfterPractice = await client.get('/progress')
check('满分后章节已完成', progAfterPractice.chapter_progress[ch1.id]?.completed === true)
check('训练详情带知识点', pr.details[0].chapter_title && pr.details[0].knowledge_point)

// 7. 考核（全对 → 100分通过 + 自动标记全部章节）
const examInfo = await client.get('/modules/performance/exam')
check('考核卷信息', examInfo.pass_score === 100)
const eqs = await client.get('/modules/performance/exam/questions')
check('考核抽题10(7知识+3案例)', eqs.length === 10 && eqs.filter(q=>q.category==='exam_case').length === 3)
const eAns = {}
eqs.forEach(q => { eAns[q.id] = realAnswers[q.id] })
const exam = await client.post('/exam/submit', { module_code: 'performance', question_ids: eqs.map(q=>q.id), answers: eAns, duration_seconds: 200 })
check('考核满分通过', exam.score === 100 && exam.passed, `(${exam.score}分)`)
const prog2 = await client.get('/progress')
const perfDone = perf.chapters.every(c => prog2.chapter_progress[c.id]?.completed)
check('通过后自动标记全部章节', perfDone)
const records = await client.get('/exam/records?module_code=performance')
check('成绩记录', records.length === 1 && records[0].score === 100)
const latestExam = await client.get('/exam/latest?module_code=performance')
check('最近考核', latestExam && latestExam.passed)
const detail = await client.get(`/exam/result/${exam.exam_record_id}`)
check('考核结果详情', detail.details.length === 10)
check('考核详情带章节知识点', detail.details.some(d => d.chapter_title && d.knowledge_point))

// 8. 统计
const stats = await client.get('/stats')
check('统计: 通过模块', 'performance' in stats.exams.passed_modules || stats.exams.passed_modules.includes('performance'))
check('统计: 今日时长', typeof stats.study_today.minutes === 'number')

// 9. 遗忘曲线复习
const reviews = await client.get('/dashboard/review')
const perfReview = reviews.reviews.find(r => r.code === 'performance')
check('复习提醒在列', !!perfReview)
check('刚通过未到期', perfReview && !perfReview.due)
const done = await client.post('/dashboard/review/performance/done')
check('复习打卡', !!done.reviewed_at)

// 10. 学习时长
const log1 = await client.post('/study/log', { seconds: 300 })
check('学习时长累计', log1.seconds === 300)
const log2 = await client.post('/study/log', { seconds: 120 })
check('再次累计', log2.seconds === 420)
const srec = await client.get('/study/records?days=7')
check('7天记录', srec.some(r => r.seconds === 420))

// 11. 学习路径
const path = await client.get('/learning-path')
check('默认路径', path.module_codes[0] === 'recruitment' && path.module_codes[5] === 'labor-law' && !path.customized)
const custom = ['training','recruitment','performance','compensation','employee-relations','labor-law']
const saved = await client.put('/learning-path', { module_codes: custom })
check('自定义路径', saved.customized && saved.module_codes[0] === 'training')
let invalid = false
try { await client.put('/learning-path', { module_codes: ['recruitment'] }) } catch { invalid = true }
check('非法路径拦截', invalid)

console.log(`\n=== 单机模式测试: 通过 ${ok}/${ok+fail} ===`)
process.exit(fail ? 1 : 0)

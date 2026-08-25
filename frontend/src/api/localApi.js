// ============================================================
// 本地数据层（单机 iOS 版）
// 替代后端 API：内容数据静态打包 + 用户数据存 localStorage
// 提供与 axios client 相同的方法签名（get/post/put → Promise<data>）
// ============================================================
import content from '../data/app-content.js'

const STATE_KEY = 'hrt_state_v1'
const REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
const DEFAULT_PATH = ['recruitment', 'performance', 'compensation', 'employee-relations', 'training', 'labor-law']

// ---------- 内容数据索引 ----------
const MODULES = content.modules
const CHAPTERS = content.chapters
const QUESTIONS = content.questions

const qByCode = (code) => QUESTIONS.filter((q) => q.module_code === code)
const qByChapter = (cid, cats) => QUESTIONS.filter(
  (q) => q.chapter_id === cid && cats.includes(q.category)
)

// ---------- 状态存储 ----------
function today() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function defaultState() {
  return {
    profile: { username: 'local', nickname: '学员', createdAt: new Date().toISOString() },
    placementRecords: [],
    practiceRecords: [],
    examRecords: [],
    progress: {},
    reviews: [],
    study: {},
    learningPath: null,
    seq: 1,
  }
}

let state = loadState()
function loadState() {
  try {
    const raw = localStorage.getItem(STATE_KEY)
    if (raw) return { ...defaultState(), ...JSON.parse(raw) }
  } catch { /* 忽略损坏数据 */ }
  return defaultState()
}
function saveState() {
  localStorage.setItem(STATE_KEY, JSON.stringify(state))
}

// ---------- 工具 ----------
const moduleByCode = (code) => MODULES.find((m) => m.code === code) || null
const chapterById = (id) => CHAPTERS.find((c) => c.id === id) || null

function randomSample(arr, k) {
  const copy = [...arr]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy.slice(0, k)
}
const isCorrect = (user, right) =>
  JSON.stringify([...user].sort()) === JSON.stringify([...right].sort())
const roundScore = (c, t) => (t ? Math.round((c / t) * 100) : 0)

function levelOf(score) {
  if (score < 60) return ['focus', '重点学习', '从讲解开始系统学习，完成章节训练与模块考核']
  if (score < 80) return ['consolidate', '巩固提升', '快速浏览讲解，重点完成训练并参加模块考核']
  return ['express', '快速通道', '基础知识扎实，直接参加训练与模块考核']
}

// ---------- 摸底测试 ----------
function buildPlacementResult(record) {
  const moduleScores = []
  for (const m of MODULES) {
    const ms = record.moduleScores[m.code] || { correct: 0, total: 0, score: 0 }
    const [level] = levelOf(ms.score)
    moduleScores.push({
      module_id: m.sort_order,
      code: m.code,
      name: m.name,
      icon: m.icon,
      correct: ms.correct,
      total: ms.total,
      score: ms.score,
      level,
    })
  }
  return {
    record_id: record.id,
    total_score: record.totalScore,
    submitted_at: record.at,
    module_scores: moduleScores,
  }
}

// ---------- 本地 API ----------
export const localApi = {
  get(path) {
    return Promise.resolve(this._handle('GET', path))
  },
  post(path, body = {}) {
    return Promise.resolve(this._handle('POST', path, body))
  },
  put(path, body = {}) {
    return Promise.resolve(this._handle('PUT', path, body))
  },

  _handle(method, path, body = {}) {
    const p = path.split('?')[0]
    const query = Object.fromEntries(new URLSearchParams(path.split('?')[1] || ''))
    try {
      return this._route(method, p, query, body)
    } catch (e) {
      return Promise.reject({ response: { status: 400, data: { detail: e.message || '操作失败' } } })
    }
  },

  _route(method, p, query, body) {
    // ---- 认证/档案（单用户本地） ----
    if (p === '/auth/me' && method === 'GET') return state.profile
    if (p === '/auth/me' && method === 'PUT') {
      const nickname = String(body.nickname || '').trim()
      if (!nickname) throw new Error('昵称不能为空')
      state.profile.nickname = nickname
      saveState()
      return state.profile
    }
    if (p === '/auth/login' || p === '/auth/register') {
      return { token: 'local', user: state.profile }
    }

    // ---- 摸底测试 ----
    if (p === '/placement/latest') {
      const rec = state.placementRecords[state.placementRecords.length - 1]
      return rec ? buildPlacementResult(rec) : null
    }
    if (p === '/placement/questions') {
      const per = Number(query.per_module || 5)
      const picked = []
      for (const m of MODULES) {
        const bank = qByCode(m.code).filter((q) => q.category === 'placement')
        picked.push(...randomSample(bank, Math.min(per, bank.length)))
      }
      picked.sort((a, b) => a.module_code.localeCompare(b.module_code) || a.sort_order - b.sort_order)
      // 不含答案；补充 module_id（前端按模块分组需要）
      return picked.map((q) => {
        const m = moduleByCode(q.module_code)
        const { answer, ...rest } = q
        return { ...rest, module_id: m ? m.sort_order : 0, options: q.options }
      })
    }
    if (p === '/placement/submit') {
      const qs = QUESTIONS.filter((q) => body.question_ids.includes(q.id))
      const moduleScores = {}
      let totalCorrect = 0
      for (const q of qs) {
        const ok = isCorrect(body.answers[String(q.id)] || [], q.answer)
        const ms = moduleScores[q.module_code] || (moduleScores[q.module_code] = { correct: 0, total: 0 })
        ms.total += 1
        if (ok) { ms.correct += 1; totalCorrect += 1 }
      }
      for (const code in moduleScores) {
        moduleScores[code].score = roundScore(moduleScores[code].correct, moduleScores[code].total)
      }
      const rec = {
        id: state.seq++,
        totalScore: roundScore(totalCorrect, qs.length),
        moduleScores,
        at: new Date().toISOString(),
      }
      state.placementRecords.push(rec)
      saveState()
      return buildPlacementResult(rec)
    }
    if (p === '/placement/tasks') {
      const rec = state.placementRecords[state.placementRecords.length - 1]
      const empty = {}
      MODULES.forEach((m) => { empty[m.code] = { correct: 0, total: 0, score: 0 } })
      const ms = rec ? rec.moduleScores : empty
      const tasks = MODULES.map((m) => {
        const s = (ms[m.code] || {}).score || 0
        const [level, label, action] = levelOf(s)
        return { module_id: m.sort_order, code: m.code, name: m.name, icon: m.icon, score: s, level, level_label: label, recommended_action: action }
      })
      const rank = { focus: 0, consolidate: 1, express: 2 }
      tasks.sort((a, b) => rank[a.level] - rank[b.level] || a.score - b.score)
      tasks.forEach((t, i) => { t.order = i + 1 })
      return { tasks, has_placement: !!rec, updated_at: rec ? rec.at : null }
    }

    // ---- 模块/章节 ----
    if (p === '/modules') {
      return MODULES.map((m) => this._moduleOut(m))
    }
    const modMatch = p.match(/^\/modules\/([a-z-]+)$/)
    if (modMatch) {
      const m = moduleByCode(modMatch[1])
      if (!m) throw new Error('模块不存在')
      return this._moduleOut(m)
    }
    const chMatch = p.match(/^\/modules\/([a-z-]+)\/chapters\/(\d+)$/)
    if (chMatch && method === 'GET') {
      const ch = chapterById(Number(chMatch[2]))
      if (!ch || ch.module_code !== chMatch[1]) throw new Error('章节不存在')
      return { id: ch.id, module_id: 0, title: ch.title, summary: ch.summary, sort_order: ch.sort_order, content: ch.content }
    }
    const prMatch = p.match(/^\/modules\/([a-z-]+)\/chapters\/(\d+)\/practice$/)
    if (prMatch && method === 'GET') {
      const cid = Number(prMatch[2])
      const qs = qByChapter(cid, ['practice', 'practice_case'])
        .sort((a, b) => (a.category === 'practice_case' ? 1 : 0) - (b.category === 'practice_case' ? 1 : 0) || a.sort_order - b.sort_order)
      return qs.map((q) => ({ id: q.id, chapter_id: q.chapter_id, module_id: 0, category: q.category, qtype: q.qtype, stem: q.stem, options: q.options, sort_order: q.sort_order }))
    }

    // ---- 训练 ----
    if (p === '/practice/submit') {
      const chapter = chapterById(body.chapter_id)
      if (!chapter) throw new Error('章节不存在')
      const qs = qByChapter(chapter.id, ['practice', 'practice_case'])
      let correctCount = 0
      const details = qs.map((q) => {
        const user = body.answers[String(q.id)] || []
        const ok = isCorrect(user, q.answer)
        if (ok) correctCount++
        return {
          question_id: q.id, category: q.category, qtype: q.qtype, stem: q.stem,
          options: q.options, user_answer: user, correct_answer: q.answer, correct: ok,
          explanation: q.explanation, chapter_id: chapter.id, chapter_title: chapter.title,
          knowledge_point: q.knowledge_point,
        }
      })
      const score = roundScore(correctCount, qs.length)
      let chapterCompleted = false
      if (score === 100) {
        const prog = state.progress[chapter.id]
        if (!prog || !prog.completed) {
          state.progress[chapter.id] = { completed: true, at: new Date().toISOString() }
          chapterCompleted = true
        }
      }
      state.practiceRecords.push({ id: state.seq++, chapterId: chapter.id, correctCount, totalCount: qs.length, answers: body.answers, at: new Date().toISOString() })
      saveState()
      return { chapter_id: chapter.id, correct_count: correctCount, total_count: qs.length, score, chapter_completed: chapterCompleted, details }
    }

    // ---- 进度 ----
    if (p === '/progress' && method === 'GET') {
      const chapterProgress = {}
      for (const cid in state.progress) {
        chapterProgress[cid] = { completed: state.progress[cid].completed, completed_at: state.progress[cid].at }
      }
      return { chapter_progress: chapterProgress }
    }
    if (p === '/progress/complete') {
      state.progress[body.chapter_id] = {
        completed: !!body.completed,
        at: body.completed ? new Date().toISOString() : null,
      }
      saveState()
      return { chapter_id: body.chapter_id, completed: !!body.completed }
    }

    // ---- 考核 ----
    const examInfoMatch = p.match(/^\/modules\/([a-z-]+)\/exam$/)
    if (examInfoMatch && method === 'GET') {
      const m = moduleByCode(examInfoMatch[1])
      if (!m) throw new Error('模块不存在')
      const k = qByCode(m.code).filter((q) => q.category === 'exam').length
      const c = qByCode(m.code).filter((q) => q.category === 'exam_case').length
      return { paper_id: m.sort_order, title: `${m.name} · 模块考核`, description: `覆盖全部章节，满分100分，100分通过（随机抽题组卷）`, pass_score: 100, duration_minutes: 15, knowledge_count: k, case_count: c, total: k + c }
    }
    const examQMatch = p.match(/^\/modules\/([a-z-]+)\/exam\/questions$/)
    if (examQMatch && method === 'GET') {
      const m = moduleByCode(examQMatch[1])
      const k = qByCode(m.code).filter((q) => q.category === 'exam')
      const c = qByCode(m.code).filter((q) => q.category === 'exam_case')
      const picked = [...randomSample(k, Math.min(7, k.length)), ...randomSample(c, Math.min(3, c.length))]
      randomSample(picked, picked.length)
      return picked.map((q) => ({ id: q.id, chapter_id: q.chapter_id, module_id: 0, category: q.category, qtype: q.qtype, stem: q.stem, options: q.options, sort_order: q.sort_order }))
    }
    if (p === '/exam/submit') {
      const m = moduleByCode(body.module_code)
      if (!m) throw new Error('模块不存在')
      const qs = QUESTIONS.filter((q) => body.question_ids.includes(q.id))
      let correctCount = 0
      for (const q of qs) {
        if (isCorrect(body.answers[String(q.id)] || [], q.answer)) correctCount++
      }
      const score = roundScore(correctCount, qs.length)
      const passed = score >= 100
      const details = qs.map((q) => {
        const user = body.answers[String(q.id)] || []
        return {
          question_id: q.id, category: q.category, qtype: q.qtype, stem: q.stem,
          options: q.options, user_answer: user, correct_answer: q.answer,
          correct: isCorrect(user, q.answer), explanation: q.explanation,
          chapter_id: q.chapter_id, knowledge_point: q.knowledge_point,
        }
      })
      let chapterAutoCompleted = false
      if (passed) {
        for (const ch of CHAPTERS.filter((c) => c.module_code === m.code)) {
          if (!state.progress[ch.id] || !state.progress[ch.id].completed) {
            state.progress[ch.id] = { completed: true, at: new Date().toISOString() }
            chapterAutoCompleted = true
          }
        }
      }
      const rec = {
        id: state.seq++, moduleCode: m.code, score, passed, answers: body.answers,
        questionIds: body.question_ids, durationSeconds: body.duration_seconds || 0,
        at: new Date().toISOString(),
      }
      state.examRecords.push(rec)
      saveState()
      return {
        exam_record_id: rec.id, module_id: m.sort_order, module_code: m.code, module_name: m.name,
        score, passed, pass_score: 100, duration_seconds: rec.durationSeconds,
        chapter_auto_completed: chapterAutoCompleted, details,
      }
    }
    if (p === '/exam/records') {
      return state.examRecords
        .filter((r) => r.moduleCode === query.module_code)
        .map((r) => ({
          id: r.id, module_code: r.moduleCode, module_name: moduleByCode(r.moduleCode).name,
          score: r.score, passed: r.passed, duration_seconds: r.durationSeconds, submitted_at: r.at,
        }))
    }
    if (p === '/exam/latest') {
      const recs = state.examRecords.filter((r) => r.moduleCode === query.module_code)
      const r = recs[recs.length - 1]
      if (!r) return null
      return {
        id: r.id, module_code: r.moduleCode, module_name: moduleByCode(r.moduleCode).name,
        score: r.score, passed: r.passed, duration_seconds: r.durationSeconds, submitted_at: r.at,
      }
    }
    const resultMatch = p.match(/^\/exam\/result\/(\d+)$/)
    if (resultMatch && method === 'GET') {
      const r = state.examRecords.find((x) => x.id === Number(resultMatch[1]))
      if (!r) throw new Error('成绩记录不存在')
      const m = moduleByCode(r.moduleCode)
      const qs = QUESTIONS.filter((q) => r.questionIds.includes(q.id))
      const details = qs.map((q) => {
        const user = (r.answers || {})[String(q.id)] || []
        const ch = chapterById(q.chapter_id)
        return {
          question_id: q.id, category: q.category, qtype: q.qtype, stem: q.stem,
          options: q.options, user_answer: user, correct_answer: q.answer,
          correct: isCorrect(user, q.answer), explanation: q.explanation,
          chapter_id: q.chapter_id, chapter_title: ch ? ch.title : '',
          knowledge_point: q.knowledge_point,
        }
      })
      return {
        exam_record_id: r.id, module_id: m.sort_order, module_code: m.code, module_name: m.name,
        score: r.score, passed: r.passed, pass_score: 100, duration_seconds: r.durationSeconds,
        chapter_auto_completed: false, details,
      }
    }

    // ---- 统计 ----
    if (p === '/stats') {
      const totalChapters = CHAPTERS.length
      const completedChapters = Object.values(state.progress).filter((x) => x.completed).length
      const practiceQs = state.practiceRecords
      const pqTotal = practiceQs.reduce((s, r) => s + r.totalCount, 0)
      const pqCorrect = practiceQs.reduce((s, r) => s + r.correctCount, 0)
      const moduleStatus = MODULES.map((m) => {
        const recs = state.examRecords.filter((r) => r.moduleCode === m.code)
        const latest = recs[recs.length - 1]
        const chs = CHAPTERS.filter((c) => c.module_code === m.code)
        const chDone = chs.filter((c) => state.progress[c.id]?.completed).length
        return {
          module_id: m.sort_order, code: m.code, name: m.name, icon: m.icon,
          exam_score: latest ? latest.score : null,
          exam_passed: latest ? latest.passed : false,
          exam_taken: !!latest,
          exam_at: latest ? latest.at : null,
          chapters_completed: chDone,
          chapters_total: chs.length,
        }
      })
      const placement = state.placementRecords[state.placementRecords.length - 1] || null
      const todayStudy = state.study[today()] || 0
      return {
        user: state.profile,
        study_today: { date: today(), seconds: todayStudy, minutes: Math.round(todayStudy / 60) },
        chapters: {
          total: totalChapters, completed: completedChapters,
          percent: totalChapters ? Math.round((completedChapters / totalChapters) * 100) : 0,
        },
        practice: {
          records: practiceQs.length, total_questions: pqTotal, correct_questions: pqCorrect,
          accuracy: pqTotal ? Math.round((pqCorrect / pqTotal) * 100) : null,
        },
        exams: {
          total_records: state.examRecords.length,
          passed_modules: moduleStatus.filter((x) => x.exam_passed).map((x) => x.code),
          passed_count: moduleStatus.filter((x) => x.exam_passed).length,
          module_status: moduleStatus,
        },
        placement: {
          taken: !!placement,
          total_score: placement ? placement.totalScore : null,
          submitted_at: placement ? placement.at : null,
        },
      }
    }

    // ---- 遗忘曲线复习 ----
    if (p === '/dashboard/review' && method === 'GET') {
      const now = new Date()
      const reviews = []
      for (const m of MODULES) {
        const lastPass = [...state.examRecords]
          .filter((r) => r.moduleCode === m.code && r.passed)
          .pop()
        if (!lastPass) continue
        const lastPassAt = new Date(lastPass.at)
        const reviewCount = state.reviews.filter(
          (r) => r.moduleCode === m.code && new Date(r.at) >= lastPassAt
        ).length
        const elapsedDays = Math.max(0, Math.floor((now - lastPassAt) / 86400000))
        const dueCount = REVIEW_INTERVALS.filter((iv) => iv <= elapsedDays).length
        const pending = Math.max(0, dueCount - reviewCount)
        const nextIdx = reviewCount
        const nextInterval = nextIdx < REVIEW_INTERVALS.length ? REVIEW_INTERVALS[nextIdx] : null
        reviews.push({
          module_id: m.sort_order, code: m.code, name: m.name, icon: m.icon,
          last_pass_at: lastPass.at, elapsed_days: elapsedDays, due: pending > 0,
          pending_reviews: pending, next_interval_days: nextInterval,
          next_review_at: nextInterval ? new Date(lastPassAt.getTime() + nextInterval * 86400000).toISOString() : null,
        })
      }
      reviews.sort((a, b) => (a.due === b.due ? (a.next_interval_days || 999) - (b.next_interval_days || 999) : a.due ? -1 : 1))
      return { reviews }
    }
    const reviewDone = p.match(/^\/dashboard\/review\/([a-z-]+)\/done$/)
    if (reviewDone && method === 'POST') {
      const m = moduleByCode(reviewDone[1])
      if (!m) throw new Error('模块不存在')
      const rec = { id: state.seq++, moduleCode: m.code, at: new Date().toISOString() }
      state.reviews.push(rec)
      saveState()
      return { module_code: m.code, reviewed_at: rec.at }
    }

    // ---- 学习时长 ----
    if (p === '/study/log') {
      const seconds = Math.max(0, Math.min(Number(body.seconds) || 0, 3600))
      state.study[today()] = (state.study[today()] || 0) + seconds
      saveState()
      return { date: today(), seconds: state.study[today()] }
    }
    if (p === '/study/records') {
      const days = Number(query.days || 7)
      const out = []
      for (let i = days - 1; i >= 0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        const key = d.toISOString().slice(0, 10)
        if (state.study[key]) out.push({ date: key, seconds: state.study[key] })
      }
      return out
    }

    // ---- 学习路径 ----
    if (p === '/learning-path' && method === 'GET') {
      return {
        module_codes: state.learningPath ? state.learningPath : DEFAULT_PATH,
        customized: !!state.learningPath,
      }
    }
    if (p === '/learning-path' && method === 'PUT') {
      const codes = body.module_codes
      const all = new Set(MODULES.map((m) => m.code))
      if (!Array.isArray(codes) || codes.length !== all.size || new Set(codes).size !== all.size || !codes.every((c) => all.has(c))) {
        throw new Error('学习路径必须包含全部 6 个模块且不重复')
      }
      state.learningPath = codes
      saveState()
      return { module_codes: codes, customized: true }
    }

    throw new Error(`未实现的本地接口: ${method} ${p}`)
  },

  _moduleOut(m) {
    const chapters = CHAPTERS
      .filter((c) => c.module_code === m.code)
      .map((c) => ({ id: c.id, module_id: 0, title: c.title, summary: c.summary, sort_order: c.sort_order }))
    return {
      id: m.sort_order, code: m.code, name: m.name, description: m.description,
      icon: m.icon, sort_order: m.sort_order, chapters,
    }
  },
}

export function resetLocalState() {
  state = defaultState()
  saveState()
}

export function getLocalProfile() {
  return { ...state.profile }
}

// 学习时长计时器（小程序版）：进入学习页面开始计时，定期与离开时上报
// 小程序无 beforeunload，改用 onHide/onUnload 上报
import { onHide, onShow, onUnload } from '@dcloudio/uni-app'
import { ref } from 'vue'
import client from '../api/client'

const FLUSH_INTERVAL = 30000 // 每 30 秒上报一次
const MIN_REPORT = 5         // 少于 5 秒不上报（防抖动）

export function useStudyTimer() {
  const seconds = ref(0)
  let timer = null
  let lastFlush = 0

  function flush(final = false) {
    const now = Date.now()
    const elapsed = Math.floor((now - lastFlush) / 1000)
    if (elapsed >= MIN_REPORT) {
      seconds.value += elapsed
      client.post('/study/log', { seconds: elapsed }).catch(() => {})
    }
    lastFlush = now
    if (final && timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function start() {
    if (timer) return
    lastFlush = Date.now()
    timer = setInterval(() => flush(), FLUSH_INTERVAL)
  }

  function stop() {
    flush(true)
  }

  onShow(start)
  onHide(stop)
  onUnload(stop)

  return { studySeconds: seconds }
}

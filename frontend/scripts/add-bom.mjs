// iOS 单机版构建后处理：为所有 JS 文件添加 UTF-8 BOM
// 解决 WKWebView(WebKit) 对外部 JS 文件默认按 windows-1252 解码导致中文乱码的问题
// 用法：node scripts/add-bom.mjs （在 vite build 之后运行）
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const assets = join(root, 'dist', 'assets')
const BOM = Buffer.from([0xef, 0xbb, 0xbf])

if (!existsSync(assets)) {
  console.error('dist/assets 不存在，请先运行 npm run build')
  process.exit(1)
}

let count = 0
for (const f of readdirSync(assets)) {
  if (!f.endsWith('.js')) continue
  const p = join(assets, f)
  const buf = readFileSync(p)
  if (!buf.subarray(0, 3).equals(BOM)) {
    writeFileSync(p, Buffer.concat([BOM, buf]))
  }
  count++
}
console.log(`✅ 已为 ${count} 个 JS 文件添加 UTF-8 BOM`)

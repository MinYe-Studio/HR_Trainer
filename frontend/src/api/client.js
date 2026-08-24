// 单机模式 API 客户端：直接使用本地数据层（localApi）
// 保持与 axios client 相同的方法签名（get/post/put → Promise<data>），视图无感知切换
import { localApi, resetLocalState, getLocalProfile } from './localApi'

const client = {
  get: (path) => localApi.get(path),
  post: (path, body) => localApi.post(path, body),
  put: (path, body) => localApi.put(path, body),
}

export { resetLocalState, getLocalProfile }
export default client

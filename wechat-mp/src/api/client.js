// 小程序版 API 客户端：直接使用本地数据层（localApi）
import { localApi, resetLocalState, getLocalProfile } from './localApi'

const client = {
  get: (path) => localApi.get(path),
  post: (path, body) => localApi.post(path, body),
  put: (path, body) => localApi.put(path, body),
}

export { resetLocalState, getLocalProfile }
export default client

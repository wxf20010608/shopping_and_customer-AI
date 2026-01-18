<template>
  <section class="chat">
    <header class="bar">
      <h3>联系客服</h3>
      <p v-if="productId">商品ID：{{ productId }}</p>
      <input v-model="filterStart" type="datetime-local" placeholder="开始时间" />
      <input v-model="filterEnd" type="datetime-local" placeholder="结束时间" />
      <button class="btn" @click="applyFilter">筛选</button>
      <button class="btn outline" @click="clearConversation">清空会话</button>
    </header>
    <div class="messages" ref="box">
      <div v-for="m in viewMessages" :key="(m.id + '-' + m.role + '-' + (m.atts?.length||0))" :class="['msg', m.role]" :data-id="'msg-'+m.id">
        <div :class="['bubble', { retracted: m.retracted && m.role==='user', highlight: highlightId === m.id } ]" @contextmenu.prevent="onContextMenu($event, m)">
          <template v-if="m.atts && m.atts.length">
            <div v-for="(att,idx) in m.atts" :key="'att-'+idx">
              <div v-if="att.type==='image'" class="attach image">
                <img :src="att.url" alt="image" />
                <div class="actions">
                  <a :href="att.url" target="_blank" class="icon-btn" title="查看">
                    <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7Zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10Z"/></svg>
                  </a>
                  <a :href="att.url" download class="icon-btn" title="下载">
                    <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 3v10l4-4 2 2-7 7-7-7 2-2 4 4V3h2Zm-9 16h18v2H3v-2Z"/></svg>
                  </a>
                </div>
              </div>
              <div v-else-if="att.type==='file'" class="attach file">
                <div class="file-box">
                  <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6"/></svg>
                  <span class="filename mono">{{ att.url.split('/').pop() }}</span>
                </div>
                <div class="actions">
                  <a :href="att.url" target="_blank" class="icon-btn" title="查看">
                    <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7Zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10Z"/></svg>
                  </a>
                  <a :href="att.url" download class="icon-btn" title="下载">
                    <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 3v10l4-4 2 2-7 7-7-7 2-2 4 4V3h2Zm-9 16h18v2H3v-2Z"/></svg>
                  </a>
                </div>
              </div>
              <div v-else-if="att.type==='audio'" class="attach audio">
                <audio :src="att.url" controls preload="metadata" style="width:100%"></audio>
                <div class="actions">
                  <a :href="att.url" download class="icon-btn" title="下载">
                    <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 3v10l4-4 2 2-7 7-7-7 2-2 4 4V3h2Zm-9 16h18v2H3v-2Z"/></svg>
                  </a>
                </div>
              </div>
            </div>
          </template>
          <template v-if="m.text">
            <p class="content">{{ m.text }}</p>
          </template>
          <span class="time">{{ displayTime(m) }}</span>
          <button v-if="m.role==='user' && typeof m.id==='number' && !m.retracted" class="icon-btn" title="撤回" @click="retract(m)">↩</button>
        </div>
      </div>
    </div>
    <p v-if="notice" :class="['notice', noticeType]">{{ notice }}</p>
    <div v-if="menu.show" class="ctx-menu" :style="{ left: menu.x + 'px', top: menu.y + 'px' }">
      <button class="ctx-item" @click="onMenuRetract" :disabled="!canRetract(menu.msg)">撤回</button>
    </div>
    <form class="input" @submit.prevent="send">
      <input v-model="text" placeholder="请输入咨询内容，例如：推荐、物流、售后..." />
      <label class="file" title="选择图片" style="cursor: pointer;">
        <input type="file" accept="image/*" multiple @change="onPickImages" />
        <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2ZM8.5 11.5A2.5 2.5 0 1 1 11 9a2.5 2.5 0 0 1-2.5 2.5Zm10 6.5H5l4.5-6 3.5 4.5 2.5-3.5L18.5 18Z"/></svg>
      </label>
      <label class="file" title="选择文件"><input type="file" multiple @change="onPickFiles" /><svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Zm0 0v6h6"/></svg></label>
      <button class="icon-btn" :class="{recording:isRecording}" type="button" @click="toggleRecording" title="按下录音/停止">
        <svg class="icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 3a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4Zm8 7h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0Z"/></svg>
      </button>
      <select v-model="modelOverride" class="model">
        <optgroup label="文本对话">
          <option value="">自动模型</option>
          <option value="qwen-turbo">qwen-turbo（快速响应）</option>
          <option value="qwen-plus">qwen-plus（平衡增强）</option>
          <option value="qwen-max">qwen-max（旗舰能力）</option>
          <option value="qwen-max-longcontext">qwen-max-longcontext（长文本）</option>
          <option value="qwen-long">qwen-long（超长文本）</option>
        </optgroup>
        <optgroup label="视觉理解">
          <option value="qwen-vl-plus">qwen-vl-plus（视觉理解）</option>
          <option value="qwen-vl-max">qwen-vl-max（视觉旗舰）</option>
        </optgroup>
        <optgroup label="多模态">
          <option value="qwen-omni-turbo">qwen-omni-turbo（全能模型）</option>
        </optgroup>
      </select>
      <button class="btn" :disabled="loading">发送</button>
    </form>
    <div v-if="pickedImages.length || pickedFiles.length" class="attachments">
      <div class="chips">
        <div v-for="(f,i) in pickedImages" :key="'img-'+i" class="chip">
          <img :src="thumbUrl(f)" alt="预览" />
          <button class="chip-x" @click="removeImage(i)">×</button>
        </div>
        <div v-for="(f,i) in pickedFiles" :key="'file-'+i" class="chip">
          <span class="mono">{{ f.name }}</span>
          <button class="chip-x" @click="removeFile(i)">×</button>
        </div>
      </div>
      <button class="btn outline" @click="clearAttachments">清除附件</button>
    </div>
    <div v-if="showRecognized" class="recognize-box">
      <textarea v-model="recognizedText" class="recognize-text"></textarea>
      <div class="recognize-actions">
        <button class="btn" @click="sendRecognizedAudio">直接发送语音</button>
        <button class="btn outline" @click="insertRecognized">填入输入框</button>
        <button class="btn outline" @click="cancelRecognized">取消</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, ref, nextTick, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const productId = ref(route.params.id || route.params.productId || null)
const messages = ref([])
const text = ref('')
const loading = ref(false)
const box = ref(null)
const pickedImages = ref([])
const pickedFiles = ref([])
const isRecording = ref(false)
let recog = null
const recognizing = ref(false)
const recognizedText = ref('')
const showRecognized = ref(false)
let mediaRecorder = null
let recordedChunks = []
let recordedFile = null
let ensureTimer = null
const notice = ref('')
const noticeType = ref('info')
const blobUrls = new Set()
function notify(msg, type='info'){
  try {
    notice.value = String(msg || '')
    noticeType.value = type
    setTimeout(() => { if (notice.value === msg) notice.value = '' }, 3000)
  } catch {}
}
function trackBlobUrl(u){ try { if (u && u.startsWith('blob:')) blobUrls.add(u) } catch {} }
function cleanupBlobUrls(){ try { blobUrls.forEach(u => { try { URL.revokeObjectURL(u) } catch {} }); blobUrls.clear() } catch {} }
const modelOverride = ref('')
const audioRefs = new Map()
const highlightId = ref(null)
const menu = ref({ show: false, x: 0, y: 0, msg: null })
const filterStart = ref('')
const filterEnd = ref('')
const limit = ref(5000)
const aiStatus = ref(null)
const viewMessages = computed(() => {
  const out = []
  const TH = 15000
  const isAttach = (c) => c && (c.startsWith('image:') || c.startsWith('file:') || c.startsWith('audio:'))
  const parseAtt = (c) => {
    if (c.startsWith('image:')) return { type:'image', url: c.slice(6) }
    if (c.startsWith('file:')) return { type:'file', url: c.slice(5) }
    if (c.startsWith('audio:')) return { type:'audio', url: c.slice(6) }
    return null
  }
  let g = null
  const flush = () => {
    if (g){
      const hasAudio = Array.isArray(g.atts) && g.atts.some(a => a && a.type === 'audio')
      const txt = hasAudio ? '' : (g.text || '')
      out.push({ id: g.id, role: 'user', text: txt, atts: g.atts || [], created_at: g.created_at, client_time: g.client_time, retracted: g.retracted })
      g = null
    }
  }
  for (const m of messages.value){
    const c = m.content
    if (m.role !== 'user'){
      flush()
      let txt = ''
      const atts = []
      if (Array.isArray(c)){
        for (const seg of c){
          if (seg && typeof seg === 'object'){
            if (seg.text) txt += (txt ? '\n' : '') + seg.text
            const iu = seg.image_url && (seg.image_url.url || seg.image_url)
            if (iu) atts.push({ type:'image', url: iu })
          }
        }
      } else {
        txt = String(c || '')
      }
      out.push({ id: m.id, role: m.role, text: txt, atts, created_at: m.created_at, retracted: m.retracted })
      continue
    }
    const ts = msgTs(m)
    if (!g){
      g = { id: m.id, startTs: ts, created_at: m.created_at, client_time: m.client_time, atts: [], text: '', retracted: m.retracted }
    } else if (ts - g.startTs > TH){
      flush()
      g = { id: m.id, startTs: ts, created_at: m.created_at, client_time: m.client_time, atts: [], text: '', retracted: m.retracted }
    }
    if (isAttach(c)){
      const att = parseAtt(c)
      if (att) g.atts.push(att)
    } else {
      // 更新为最新的文本
      g.text = c
      g.id = m.id
      g.created_at = m.created_at
      g.client_time = m.client_time
      g.retracted = m.retracted
    }
  }
  flush()
  return out
})

async function loadHistory(){
  if (!userStore.userId) return
  try {
    // 加载所有消息（不传时间筛选参数，筛选只负责跳转）
    const params = { limit: limit.value || 5000 }
    const { data } = await api.getChatHistory(userStore.userId, productId.value || 0, params)
    messages.value = (data.items || []).filter(m => !(m.role === 'assistant' && typeof m.content === 'string' && m.content.includes('AI服务暂不可用')))
    ensureBottom()
  } catch {}
}
async function loadAIStatus(){
  try { const { data } = await api.getAIStatus(); aiStatus.value = data } catch { aiStatus.value = null }
}

async function send(){
  if (!userStore.userId){ notify('请先登录','warn'); return }
  if (!text.value.trim() && !pickedImages.value.length && !pickedFiles.value.length){ notify('请输入内容或选择附件','warn'); return }
  try {
    loading.value = true
    if (text.value.trim()){
      const userNow = { id: 'local-' + Date.now(), role: 'user', content: text.value, client_time: new Date().toISOString() }
      messages.value.push(userNow)
      ensureBottom()
    }
    const currentText = text.value
    text.value = ''
    if (pickedImages.value.length){
      pickedImages.value.forEach((f,i) => { try { const url = URL.createObjectURL(f); trackBlobUrl(url); messages.value.push({ id: 'local-img-'+Date.now()+'-'+i, role:'user', content:'image:'+url, client_time:new Date().toISOString() }) } catch {} })
    }
    if (pickedFiles.value.length){
      pickedFiles.value.forEach((f,i) => { try { const url = URL.createObjectURL(f); trackBlobUrl(url); messages.value.push({ id: 'local-file-'+Date.now()+'-'+i, role:'user', content:'file:'+url, client_time:new Date().toISOString() }) } catch {} })
    }
    ensureBottom()
    let response
    if (pickedImages.value.length || pickedFiles.value.length){
      response = await api.sendChatWithUpload(userStore.userId, productId.value || null, currentText.trim(), { images: pickedImages.value, files: pickedFiles.value }, modelOverride.value || undefined)
    } else {
      response = await api.sendChat(userStore.userId, productId.value || null, currentText.trim(), modelOverride.value || undefined)
    }
    
    // 检查响应是否有效
    if (!response || !response.data) {
      throw new Error('服务器返回了无效响应')
    }
    
    await loadHistory(); cleanupBlobUrls()
    pickedImages.value = []; pickedFiles.value = []
    ensureBottom()
  } catch (e){
    console.error('发送消息失败:', e)
    const msg = (e && e.response && e.response.data && (e.response.data.detail || e.response.data.message)) || (e && e.message) || '发送失败，请检查网络连接或稍后重试'
    notify(msg,'error')
    // 如果发送失败，移除本地添加的用户消息
    if (messages.value.length > 0 && messages.value[messages.value.length - 1].id && String(messages.value[messages.value.length - 1].id).startsWith('local-')) {
      messages.value.pop()
    }
  } finally { loading.value = false }
}

async function applyFilter(){
  // 筛选只负责跳转到指定时间段，不限制显示内容
  // 如果消息列表为空，先加载消息
  if (messages.value.length === 0) {
    await loadHistory()
  }
  // 跳转到指定时间段的消息
  scrollToRange()
}
async function clearConversation(){
  try {
    await api.clearChat(userStore.userId, productId.value || 0)
    messages.value = []
    const key = `chat_filter_${userStore.userId}_${productId.value || 0}`
    try { sessionStorage.removeItem(key) } catch {}
    ensureBottom()
  } catch { notify('清空失败','error') }
}
async function retract(m){
  try {
    await api.retractChatMessage(m.id, userStore.userId)
    await loadHistory()
  } catch { notify('撤回失败','error') }
}

function canRetract(m){ return !!(m && m.role === 'user' && typeof m.id === 'number' && !m.retracted) }
function onContextMenu(e, m){
  if (!canRetract(m)) return
  const rect = box.value?.getBoundingClientRect()
  let x = e.clientX, y = e.clientY
  if (rect){ x = Math.min(e.clientX, rect.left + rect.width - 120); y = Math.min(e.clientY, rect.top + rect.height - 40) }
  menu.value = { show: true, x, y, msg: m }
}
function onMenuRetract(){ if (!menu.value.msg) return; retract(menu.value.msg); menu.value.show = false }
function hideMenu(){ menu.value.show = false; menu.value.msg = null }
function onGlobalClick(ev){ if (!menu.value.show) return; const el = ev.target; const menuEl = document.querySelector('.ctx-menu'); if (menuEl && !menuEl.contains(el)) hideMenu() }
function onKey(ev){ if (ev.key === 'Escape') hideMenu() }

function setAudioRef(el){ if (!el) return; audioRefs.set(el.src, el) }
function togglePlay(m){ const url = m.content.slice(6); const el = audioRefs.get(url); if (!el) return; if (el.paused) el.play(); else el.pause(); }
function togglePlayAtt(att){ const url = att.url; const el = audioRefs.get(url); if (!el) return; if (el.paused) el.play(); else el.pause(); }
function onPickImages(e){
  const files = Array.from(e.target.files || [])
  if (files.length === 0) return
  
  // 验证文件类型和大小
  const maxSize = 10 * 1024 * 1024 // 10MB
  const validFiles = []
  
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      notify(`文件 ${file.name} 不是图片格式`, 'warn')
      continue
    }
    if (file.size > maxSize) {
      notify(`图片 ${file.name} 超过10MB限制`, 'warn')
      continue
    }
    validFiles.push(file)
  }
  
  if (validFiles.length > 0) {
    pickedImages.value = [...pickedImages.value, ...validFiles]
    notify(`已选择 ${validFiles.length} 张图片`, 'info')
  }
  
  // 清空input，允许重复选择同一文件
  e.target.value = ''
}
function onPickFiles(e){ pickedFiles.value = Array.from(e.target.files || []) }
function thumbUrl(f){ try { const u = URL.createObjectURL(f); trackBlobUrl(u); return u } catch { return '' } }
function removeImage(i){ pickedImages.value.splice(i,1) }
function removeFile(i){ pickedFiles.value.splice(i,1) }
function clearAttachments(){ pickedImages.value = []; pickedFiles.value = []; cleanupBlobUrls() }

async function toggleRecording(){
  if (!isRecording.value){
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      recordedChunks = []
      mediaRecorder = new MediaRecorder(stream)
      mediaRecorder.ondataavailable = e => { try { if (e.data && e.data.size > 0) recordedChunks.push(e.data) } catch {} }
      mediaRecorder.onstop = () => {
        try {
          const blob = new Blob(recordedChunks, { type: 'audio/webm' })
          if (blob && blob.size > 0){
            recordedFile = new File([blob], `record_${Date.now()}.webm`, { type: 'audio/webm' })
          } else {
            recordedFile = null
          }
        } catch { recordedFile = null }
        showRecognized.value = !!(recognizedText.value || recordedFile)
      }
      try { mediaRecorder.start(250) } catch { mediaRecorder.start() }
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition
        recog = new SR(); recog.lang = 'zh-CN'; recog.interimResults = true; recog.maxAlternatives = 1
        recognizedText.value = ''
        recog.onresult = (ev) => {
          let final = ''
          for (let i = ev.resultIndex; i < ev.results.length; i++){
            const r = ev.results[i]
            const t = r[0]?.transcript || ''
            if (r.isFinal) final += t + ' '
          }
          if (final) recognizedText.value = (recognizedText.value + ' ' + final).trim()
        }
        recog.onend = () => { recognizing.value = false; try { mediaRecorder && mediaRecorder.stop() } catch {}; isRecording.value = false }
        recog.start(); recognizing.value = true
      }
      isRecording.value = true
    } catch { notify('无法开始录音','error') }
  } else {
    try { mediaRecorder && mediaRecorder.requestData() } catch {}
    try { mediaRecorder && mediaRecorder.stop() } catch {}
    try { recog && recog.stop() } catch {}
    recognizing.value = false; isRecording.value = false
  }
}

async function sendRecognizedAudio(){
  const msg = ((recognizedText.value || '').trim()) || '请根据语音内容进行解答'
  showRecognized.value = false
  try {
    if (recordedFile && recordedFile.size > 0){
      try {
        const url = URL.createObjectURL(recordedFile)
        trackBlobUrl(url); messages.value.push({ id: 'local-audio-'+Date.now(), role:'user', content:'audio:'+url, client_time:new Date().toISOString() })
        ensureBottom()
      } catch {}
      await api.sendChatWithUpload(userStore.userId, productId.value || null, msg, { audios: [recordedFile] }, modelOverride.value || undefined)
    } else {
      notify('没有可发送的语音或录音为空，请重新录制','warn')
      return
    }
  } finally {
    recordedFile = null
    recognizedText.value = ''
  }
  await loadHistory()
  ensureBottom()
}
function insertRecognized(){
  if (!recognizedText.value.trim()){ showRecognized.value = false; return }
  text.value = (text.value ? text.value + ' ' : '') + recognizedText.value.trim()
  showRecognized.value = false
  recognizedText.value = ''
}
function cancelRecognized(){ showRecognized.value = false; recognizedText.value = '' }

onMounted(() => { loadHistory(); loadAIStatus(); window.addEventListener('click', onGlobalClick); window.addEventListener('keydown', onKey); setTimeout(() => ensureBottom(), 0) })
watch(() => userStore.userId, (id) => { if (id) loadHistory() })
watch(() => [route.params.id, route.params.productId], () => { productId.value = route.params.id || route.params.productId || null; if (userStore.userId) loadHistory() })
onUnmounted(() => { window.removeEventListener('click', onGlobalClick); window.removeEventListener('keydown', onKey); cleanupBlobUrls() })

function displayTime(m){
  const t = m?.created_at || m?.client_time || ''
  if (!t) return ''
  
  const d = parseDateTime(t)
  if (!d || isNaN(d.getTime())) {
    console.warn('无法解析时间:', t, '原始值:', m)
    return ''
  }
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  // 1分钟内显示"刚刚"
  if (diff >= 0 && diff < 60000) return '刚刚'
  
  // 获取本地日期（年、月、日）- 使用本地时区的日期部分
  const nowYear = now.getFullYear()
  const nowMonth = now.getMonth()
  const nowDate = now.getDate()
  
  const msgYear = d.getFullYear()
  const msgMonth = d.getMonth()
  const msgDate = d.getDate()
  
  // 格式化日期时间组件
  const y = String(msgYear)
  const mo = String(msgMonth + 1).padStart(2, '0')
  const da = String(msgDate).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  
  // 所有消息都显示完整日期时间（YYYY/MM/DD HH:mm）
  return `${y}/${mo}/${da} ${h}:${mi}`
}

function parseDateTime(input){
  if (!input) return new Date()
  
  const s = String(input).trim()
  
  // 检查是否包含时区信息
  // 匹配时区格式：Z, +HH:mm, -HH:mm, +HHmm, -HHmm
  const hasTimezone = s.endsWith('Z') || 
                      /[+-]\d{2}:?\d{2}$/.test(s) ||
                      /[+-]\d{4}$/.test(s)
  
  // 如果没有时区信息，假设是UTC时间（后端使用datetime.utcnow()）
  // FastAPI/Pydantic 可能返回不带时区的ISO格式字符串
  if (!hasTimezone) {
    // 匹配ISO格式：YYYY-MM-DDTHH:mm:ss[.sss]
    const isoMatch = s.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?$/)
    if (isoMatch) {
      const [_, y, mo, da, h, mi, se, ms] = isoMatch
      // 手动解析为UTC时间，然后转换为本地时间显示
      const utcTime = Date.UTC(
        Number(y), 
        Number(mo) - 1, 
        Number(da), 
        Number(h), 
        Number(mi), 
        Number(se), 
        ms ? Number(ms.padEnd(3, '0').substring(0, 3)) : 0
      )
      return new Date(utcTime)
    }
    
    // 处理简单格式：YYYY-MM-DD HH:mm:ss
    const simpleMatch = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/)
    if (simpleMatch) {
      const [_, y, mo, da, h, mi, se] = simpleMatch
      const utcTime = Date.UTC(Number(y), Number(mo) - 1, Number(da), Number(h), Number(mi), Number(se))
      return new Date(utcTime)
    }
  }
  
  // 有时区信息，使用原生Date解析（会自动转换为本地时间）
  try {
    const d = new Date(s)
    if (!isNaN(d.getTime())) return d
  } catch (e) {
    console.warn('解析时间失败:', s, e)
  }
  
  // 如果都失败了，尝试直接解析
  const fallback = new Date(s)
  if (!isNaN(fallback.getTime())) return fallback
  
  console.warn('无法解析时间字符串:', s)
  return new Date()
}

function msgTs(m){ const t = m?.created_at || m?.client_time; return t ? parseDateTime(t).getTime() : Date.now() }
function scrollToRange(){
  const hasStart = !!(filterStart.value && String(filterStart.value).trim())
  const hasEnd = !!(filterEnd.value && String(filterEnd.value).trim())
  if (!hasStart && !hasEnd){ 
    nextTick(() => { 
      if (box.value) box.value.scrollTop = box.value.scrollHeight 
    })
    return 
  }
  
  // 解析时间范围（datetime-local 格式：YYYY-MM-DDTHH:mm）
  let startTs = -Infinity
  let endTs = Infinity
  
  if (hasStart) {
    try {
      // datetime-local 格式需要转换为 Date 对象
      const startDate = new Date(filterStart.value)
      if (!isNaN(startDate.getTime())) {
        startTs = startDate.getTime()
      }
    } catch (e) {
      console.warn('解析开始时间失败:', filterStart.value, e)
    }
  }
  
  if (hasEnd) {
    try {
      const endDate = new Date(filterEnd.value)
      if (!isNaN(endDate.getTime())) {
        endTs = endDate.getTime()
      }
    } catch (e) {
      console.warn('解析结束时间失败:', filterEnd.value, e)
    }
  }
  
  // 在 viewMessages 中查找匹配的消息（优先查找开始时间附近的消息）
  const viewMsgs = viewMessages.value
  let targetIdx = -1
  
  // 优先查找开始时间附近的消息
  if (hasStart) {
    // 查找第一个时间 >= startTs 的消息
    targetIdx = viewMsgs.findIndex(m => {
      const t = msgTs(m)
      return t >= startTs && (hasEnd ? t <= endTs : true)
    })
    
    // 如果没找到，查找最接近开始时间的消息
    if (targetIdx === -1) {
      let minDiff = Infinity
      viewMsgs.forEach((m, i) => {
        const t = msgTs(m)
        const diff = Math.abs(t - startTs)
        if (diff < minDiff && (hasEnd ? t <= endTs : true)) {
          minDiff = diff
          targetIdx = i
        }
      })
    }
  } else if (hasEnd) {
    // 只有结束时间，查找最后一个 <= endTs 的消息
    for (let i = viewMsgs.length - 1; i >= 0; i--) {
      if (msgTs(viewMsgs[i]) <= endTs) {
        targetIdx = i
        break
      }
    }
  }
  
  nextTick(() => {
    if (targetIdx !== -1 && targetIdx < viewMsgs.length) {
      const targetMsg = viewMsgs[targetIdx]
      const id = 'msg-' + targetMsg.id
      const el = box.value?.querySelector(`[data-id="${id}"]`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        highlightId.value = targetMsg.id
        setTimeout(() => { highlightId.value = null }, 2000)
      } else {
        console.warn('未找到消息元素:', id)
        if (box.value) box.value.scrollTop = box.value.scrollHeight
      }
    } else {
      // 没找到匹配的消息，滚动到底部或顶部
      if (hasStart) {
        // 有开始时间但没找到，滚动到顶部（可能是筛选结果为空）
        if (box.value) box.value.scrollTop = 0
      } else {
        if (box.value) box.value.scrollTop = box.value.scrollHeight
      }
    }
  })
}

function scrollBottom(){ if (box.value) box.value.scrollTop = box.value.scrollHeight }
function ensureBottom(){
  if (ensureTimer) return
  ensureTimer = setTimeout(() => {
    nextTick(() => {
      const last = messages.value.length ? messages.value[messages.value.length - 1] : null
      if (last){
        const id = 'msg-' + last.id
        const el = box.value?.querySelector(`[data-id="${id}"]`)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }
      scrollBottom()
      ensureTimer = null
    })
  }, 50)
}
</script>

<style scoped>
.chat { display: grid; grid-template-rows: auto 1fr auto; gap: 12px; height: calc(100vh - 140px); min-height: calc(100vh - 140px); }
.bar { display: flex; align-items: baseline; gap: 12px; position: sticky; top: 0; z-index: 6; background: #fff; padding: 8px 0; }
.messages { display: flex; flex-direction: column; gap: 8px; background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 12px; overflow: auto; }
.msg { display: flex; }
.msg.assistant { justify-content: flex-start; }
.msg.user { justify-content: flex-end; }
.bubble { max-width: 68%; padding: 8px 10px; border-radius: 12px; display: grid; gap: 6px; }
.msg.assistant .bubble { background: #f3f4f6; color: #111827; border-top-left-radius: 4px; }
.input { position: sticky; bottom: 0; background: #fff; padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; z-index: 5; }
.input { position: sticky; bottom: 0; background: #fff; padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; z-index: 5; }
.msg.user .bubble { background: #1d4ed8; color: #fff; border-top-right-radius: 4px; }
.bubble.retracted { background: #9ca3af !important; color: #fff; font-style: italic; }
.content { white-space: pre-wrap; }
.time { font-size: 12px; opacity: 0.7; }
.input { display: flex; gap: 8px; position: sticky; bottom: 0; background: #fff; padding-top: 8px; }
.input input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
.input .model { height: 36px; border: 1px solid #ddd; border-radius: 6px; padding: 0 8px; }
.btn { height: 36px; padding: 0 12px; border: none; border-radius: 6px; background: #1d4ed8; color: #fff; }
.btn.outline { background:#fff; border:1px solid #1d4ed8; color:#1d4ed8; }
.bubble img { max-width: 300px; max-height: 300px; object-fit: contain; border-radius: 8px; }
.bubble.highlight { outline: 2px solid #f59e0b; }
.icon { width: 20px; height: 20px; }
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border:none; border-radius:8px; background:rgba(0,0,0,0.08); cursor:pointer; }
.icon-btn.recording { background:#ef4444; color:#fff; }
.file { 
  display:inline-flex; 
  align-items:center; 
  justify-content:center;
  padding:0 8px; 
  border:1px dashed #ddd; 
  border-radius:6px; 
  cursor:pointer;
  min-width: 36px;
  height: 36px;
  transition: all 0.2s;
}
.file:hover { 
  border-color: #1d4ed8; 
  background: #f3f4f6;
}
.file input { 
  display:none; 
}
.file .icon {
  width: 20px;
  height: 20px;
  color: #374151;
}
.file:hover .icon {
  color: #1d4ed8;
}
.chk { display:inline-flex; align-items:center; gap:4px; color:#374151; }
.attachments { display: flex; align-items: center; gap: 8px; padding: 8px 0; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 8px; background: #fff; }
.chip img { width: 40px; height: 40px; object-fit: cover; border-radius: 6px; }
.chip-x { border: none; background: #ef4444; color: #fff; width: 22px; height: 22px; border-radius: 50%; cursor: pointer; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.attach { display: grid; gap: 8px; }
.attach.image img { width: 100%; max-width: 320px; max-height: 420px; object-fit: contain; border-radius: 8px; }
.attach .actions { display: inline-flex; gap: 8px; }
.attach.file .file-box { display:flex; align-items:center; gap:8px; padding:8px; border-radius:8px; }
.msg.user .attach.file .file-box { background: rgba(255,255,255,0.12); }
.msg.assistant .attach.file .file-box { background: rgba(0,0,0,0.06); }
.notice { margin-top: 4px; font-size: 12px; padding: 6px 8px; border-radius: 6px; }
.notice.info { background: #eef2ff; color: #1d4ed8; }
.notice.warn { background: #fff7ed; color: #b45309; }
.notice.error { background: #fee2e2; color: #b91c1c; }
.recognize-box { border: 1px solid #eee; border-radius: 6px; padding: 8px; background: #fafafa; }
.recognize-text { width: 100%; min-height: 72px; }
.recognize-actions { display: flex; gap: 8px; }
</style>
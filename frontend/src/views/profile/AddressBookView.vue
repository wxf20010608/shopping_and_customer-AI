<template>
  <div class="address-book">
    <h2>地址簿</h2>
    <div class="addr-form">
      <h3>{{ editingId ? '编辑地址' : '新增地址' }}</h3>
      <form @submit.prevent="onSubmit">
        <div class="row">
          <div class="form-item"><label>收件人</label><input v-model="form.receiver_name" required /></div>
          <div class="form-item"><label>联系电话</label><input v-model="form.phone" required /></div>
        </div>
        <div class="row">
          <div class="form-item"><label>省份</label>
            <select v-model="selectedProvince" @change="onProvinceChange" required>
              <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div class="form-item"><label>城市</label>
            <template v-if="cities.length">
              <select v-model="selectedCity" @change="onCityChange" required>
                <option v-for="c in cities" :key="c" :value="c">{{ c }}</option>
              </select>
              <input v-if="selectedCity==='其他城市'" v-model="otherCity" placeholder="请输入城市" @input="syncOtherCity" />
            </template>
            <input v-else v-model="form.city" placeholder="请输入城市" required />
          </div>
          <div class="form-item"><label>区县</label>
            <template v-if="districts.length">
              <select v-model="selectedDistrict" @change="onDistrictChange" required>
                <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
              </select>
              <input v-if="selectedDistrict==='其他区县'" v-model="otherDistrict" placeholder="请输入区县" @input="syncOtherDistrict" />
            </template>
            <input v-else v-model="form.district" placeholder="请输入区县" required />
          </div>
        </div>
        <div class="form-item"><label>详细地址</label><input v-model="form.detail" required /></div>
        <div class="form-item inline"><label>设为默认地址</label><input type="checkbox" v-model="form.is_default" /></div>
        <div class="btns">
          <button type="submit" class="primary">{{ editingId ? '保存' : '添加' }}</button>
          <button type="button" @click="resetForm">重置</button>
        </div>
      </form>
    </div>

    <div class="addr-list">
      <h3>地址列表</h3>
      <div v-if="list.length === 0" class="empty">暂无地址</div>
      <div v-for="item in list" :key="item.id" class="addr-item" :class="{ default: item.is_default }">
        <div class="line">
          <strong>{{ item.receiver_name }}</strong>
          <span>{{ item.phone }}</span>
          <span v-if="item.is_default" class="tag">默认</span>
        </div>
        <div class="line">{{ item.province }} {{ item.city }} {{ item.district }} {{ item.detail }}</div>
        <div class="actions">
          <button @click="edit(item)">编辑</button>
          <button class="danger" @click="del(item)">删除</button>
          <button v-if="!item.is_default" @click="setDefault(item)">设为默认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { api } from '@/api'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const userId = ref(null)

const list = ref([])
const editingId = ref(null)
const form = reactive({ receiver_name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false })

const selectedProvince = ref('')
const selectedCity = ref('')
const selectedDistrict = ref('')
const provinces = ref([])
const cities = ref([])
const districts = ref([])
const otherCity = ref('')
const otherDistrict = ref('')

const regionTree = ref([])
const REGION_CACHE_KEY = 'china_division_pcas_v1'

async function fetchJson(url){
  const res = await fetch(url)
  if (!res.ok) throw new Error('fetch failed')
  return res.json()
}

async function loadRegionData () {
  try {
    const cached = localStorage.getItem(REGION_CACHE_KEY)
    if (cached) {
      const data = JSON.parse(cached)
      if (data && data.length >= 31) { // 确保缓存数据完整（全国34个省级行政区）
        regionTree.value = data
        provinces.value = data.map(p => p.name)
        if (!selectedProvince.value) selectedProvince.value = provinces.value[0] || ''
        onProvinceChange()
        return
      }
    }
    // 优先从本地加载完整数据，然后再尝试CDN
    const urls = [
      '/pcas.json',  // 本地完整数据（优先）
      'https://cdn.jsdelivr.net/npm/china-division@2.6.1/dist/pcas.json',
      'https://unpkg.com/china-division@2.6.1/dist/pcas.json',
    ]
    let data = null
    for (const u of urls){
      try { 
        data = await fetchJson(u)
        if (data && data.length >= 31) break // 确保数据完整（全国34个省级行政区）
        data = null
      } catch(e){ console.warn('加载地区数据失败:', u, e) }
    }
    if (!data || data.length < 31) throw new Error('no data')
    regionTree.value = data
    localStorage.setItem(REGION_CACHE_KEY, JSON.stringify(data))
    provinces.value = data.map(p => p.name)
    if (!selectedProvince.value) selectedProvince.value = provinces.value[0] || ''
    onProvinceChange()
  } catch (e) {
    console.warn('使用本地备用数据', e)
    // 完整的省市区备用数据
    regionTree.value = [
      { name: "北京市", children: [ { name: "北京市", children: ["东城区","西城区","朝阳区","海淀区","丰台区","石景山区","通州区","昌平区","大兴区","顺义区","房山区","门头沟区","怀柔区","平谷区","密云区","延庆区"].map(n=>({ name: n })) } ] },
      { name: "上海市", children: [ { name: "上海市", children: ["黄浦区","徐汇区","长宁区","静安区","普陀区","虹口区","杨浦区","闵行区","宝山区","嘉定区","浦东新区","金山区","松江区","青浦区","奉贤区","崇明区"].map(n=>({ name: n })) } ] },
      { name: "天津市", children: [ { name: "天津市", children: ["和平区","河东区","河西区","南开区","河北区","红桥区","滨海新区","东丽区","西青区","津南区","北辰区","武清区","宝坻区","宁河区","静海区","蓟州区"].map(n=>({ name: n })) } ] },
      { name: "重庆市", children: [ { name: "重庆市", children: ["渝中区","江北区","南岸区","沙坪坝区","九龙坡区","大渡口区","巴南区","北碚区","渝北区","涪陵区","万州区","长寿区","黔江区","江津区","合川区","永川区","南川区"].map(n=>({ name: n })) } ] },
    ]
    provinces.value = regionTree.value.map(p => p.name)
    if (!selectedProvince.value) selectedProvince.value = provinces.value[0] || ''
    onProvinceChange()
  }
}

function initRegions () { loadRegionData() }

function normalizeProvince(name){
  if (!name) return ''
  const candidates = [name, name+"省", name+"市", name+"自治区", name+"特别行政区"]
  const found = regionTree.value.find(p => candidates.includes(p.name))
  return found?.name || name
}

function onProvinceChange () {
  const normalized = normalizeProvince(selectedProvince.value)
  const p = regionTree.value.find(x => x.name === normalized)
  cities.value = (p?.children || []).map(c => c.name)
  if (cities.value.length) {
    if (!cities.value.includes(selectedCity.value)) selectedCity.value = cities.value[0] || ''
  } else {
    const capitals = {
      "北京市":"北京市","天津市":"天津市","上海市":"上海市","重庆市":"重庆市",
      "河北省":"石家庄市","山西省":"太原市","辽宁省":"沈阳市","吉林省":"长春市","黑龙江省":"哈尔滨市",
      "江苏省":"南京市","浙江省":"杭州市","安徽省":"合肥市","福建省":"福州市","江西省":"南昌市",
      "山东省":"济南市","河南省":"郑州市","湖北省":"武汉市","湖南省":"长沙市","广东省":"广州市",
      "广西壮族自治区":"南宁市","海南省":"海口市","四川省":"成都市","贵州省":"贵阳市","云南省":"昆明市",
      "西藏自治区":"拉萨市","陕西省":"西安市","甘肃省":"兰州市","青海省":"西宁市","宁夏回族自治区":"银川市",
      "新疆维吾尔自治区":"乌鲁木齐市","内蒙古自治区":"呼和浩特市","香港特别行政区":"香港","澳门特别行政区":"澳门","台湾省":"台北市"
    }
    const cap = capitals[normalized] || (normalized.replace('省','') + '市')
    cities.value = [cap, '其他城市']
    selectedCity.value = cities.value[0]
    selectedDistrict.value = ''
  }
  form.province = normalized
  onCityChange()
}

function onCityChange () {
  const normalized = normalizeProvince(selectedProvince.value)
  const p = regionTree.value.find(x => x.name === normalized)
  const c = (p?.children || []).find(x => x.name === selectedCity.value)
  districts.value = (c?.children || []).map(a => a.name)
  if (districts.value.length) {
    if (!districts.value.includes(selectedDistrict.value)) selectedDistrict.value = districts.value[0] || ''
    form.city = selectedCity.value === '其他城市' ? (otherCity.value || '') : selectedCity.value
    form.district = selectedDistrict.value || ''
  } else {
    districts.value = ['市辖区','城区','郊区','其他区县']
    selectedDistrict.value = districts.value[0]
    form.city = selectedCity.value === '其他城市' ? (otherCity.value || '') : selectedCity.value
    form.district = selectedDistrict.value === '其他区县' ? (otherDistrict.value || '') : selectedDistrict.value
  }
}

function onDistrictChange () { form.district = selectedDistrict.value === '其他区县' ? (otherDistrict.value || '') : selectedDistrict.value }

function syncOtherCity(){ form.city = otherCity.value }
function syncOtherDistrict(){ form.district = otherDistrict.value }



function resetForm () {
  editingId.value = null
  Object.assign(form, { receiver_name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false })
  selectedProvince.value = ''
  selectedCity.value = ''
  selectedDistrict.value = ''
  initRegions()
}

function edit (item) {
  editingId.value = item.id
  Object.assign(form, item)
  selectedProvince.value = item.province || ''
  onProvinceChange()
  selectedCity.value = item.city || selectedCity.value
  onCityChange()
  selectedDistrict.value = item.district || selectedDistrict.value
  onDistrictChange()
}

async function del (item) {
  if (!confirm('确认删除该地址？')) return
  try {
    await api.deleteAddress(userId.value, item.id)
    await fetchList()
  } catch (err) {
    alert(err?.response?.data?.detail || '删除失败')
  }
}

async function setDefault (item) {
  try {
    await api.updateAddress(userId.value, item.id, { is_default: true })
    await fetchList()
  } catch (err) {
    alert(err?.response?.data?.detail || '设置失败')
  }
}

async function fetchList () {
  try {
    const { data } = await api.listAddresses(userId.value)
    list.value = data
  } catch (err) {
    alert(err?.response?.data?.detail || '拉取地址失败')
  }
}

async function onSubmit () {
  try {
    if (editingId.value) {
      await api.updateAddress(userId.value, editingId.value, form)
    } else {
      await api.createAddress(userId.value, form)
    }
    resetForm()
    await fetchList()
  } catch (err) {
    alert(err?.response?.data?.detail || '保存失败')
  }
}

onMounted(async () => {
  const id = userStore.userId
  const name = userStore.username
  if (!id) return router.replace('/login')
  userId.value = id
  initRegions()
  await fetchList()
})
</script>

<style scoped>
.address-book { max-width: 860px; margin: 24px auto; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.addr-form, .addr-list { padding: 18px; border: 1px solid #eee; border-radius: 8px; }
.form-item { margin-bottom: 12px; }
.row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
label { display: block; margin-bottom: 6px; color: #555; }
input, select { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; }
.btns { display: flex; gap: 8px; }
button.primary { padding: 8px 14px; border: none; border-radius: 6px; background: #42b983; color: #fff; font-weight: 600; cursor: pointer; }
.addr-item { border-bottom: 1px dashed #ddd; padding: 10px 0; }
.addr-item.default { background: #f5fffa; }
.line { display: flex; gap: 12px; align-items: center; }
.tag { background: #42b983; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.actions { display: flex; gap: 8px; margin-top: 8px; }
button.danger { background: #e74c3c; color: #fff; border: none; padding: 8px 14px; border-radius: 6px; }
.empty { color: #888; }
/* 新增：让默认地址与复选框同一行 */
.form-item.inline { display: flex; align-items: center; gap: 8px; }
.form-item.inline label { margin-bottom: 0; }
.form-item.inline input[type="checkbox"] { width: auto; }
</style>
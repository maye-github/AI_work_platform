<template>
  <main class="login-screen">
    <h1>{{ labels.title }}</h1>
    <p class="datetime">{{ now }}</p>

    <label>ユーザーＩＤ
      <input v-model="form.userId" maxlength="7" />
    </label>
    <label>起動区分
      <input v-model="form.startupKbn" maxlength="1" />
    </label>
    <p class="hint">{{ labels.startupHint }}</p>

    <label>画面
      <select v-model="form.screen">
        <option v-for="page in pages" :key="page.value" :value="page.value">
          {{ page.label }}
        </option>
      </select>
    </label>
    <label>権限区分
      <select v-model="form.authorityKbn">
        <option v-for="kbn in kbns" :key="kbn.value" :value="kbn.value">
          {{ kbn.label }}
        </option>
      </select>
    </label>

    <button @click="onLogin">ログイン</button>
    <button @click="onMenu">メニュー</button>

    <label>URL
      <input v-model="form.url" maxlength="150" />
    </label>
    <button @click="onGenerateUrl">URL出力</button>
    <button @click="onClose">閉じる</button>

    <p v-if="error" class="error">{{ error }}</p>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { encryptEmployeeCode } from '../api/cipher'
import { doLogin, generateUrl as generateUrlApi, initLogin } from '../api/login'
import { useSessionStore } from '../stores/session'

const labels = {
  title: '共通マスタ　ログイン',
  startupHint: '1：本店ユーザー、2：工場ユーザー、3：システム管理者',
}
const now = ref('')
const pages = ref<{ value: string; label: string }[]>([])
const kbns = ref<{ value: string; label: string }[]>([])
const error = ref('')
const session = useSessionStore()
const form = reactive({
  userId: '',
  startupKbn: '3',
  screen: '',
  authorityKbn: 'Y',
  url: '',
})

function tick() {
  const date = new Date()
  const pad = (value: number) => String(value).padStart(2, '0')
  now.value = `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} `
    + `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

onMounted(async () => {
  tick()
  window.setInterval(tick, 1000)
  const response = await initLogin() as any
  if (response.errorCode !== '0') {
    error.value = response.messageId ?? '初期表示に失敗しました'
    return
  }
  pages.value = response.pageList
  kbns.value = response.kbnList
  form.screen = response.initial?.screen ?? pages.value[0]?.value ?? ''
  form.authorityKbn = response.initial?.authorityKbn ?? 'Y'
})

async function onLogin() {
  error.value = ''
  const response = await doLogin({
    stfCd: await encryptEmployeeCode(form.userId),
    stfKbn: form.startupKbn,
    gmnId: form.screen,
    kgnKbn: form.authorityKbn,
  }) as any
  if (response.errorCode !== '0') {
    error.value = response.messageId ?? 'ログインできませんでした'
    return
  }
  session.setUser(response.userInfo, response.mngInfo)
  const target = `/R60/Pages/index.jsp?gmnId=${encodeURIComponent(form.screen)}`
    + `&kgnKbn=${encodeURIComponent(form.authorityKbn)}`
  window.open(target, '_blank')
}

function onMenu() {
  window.open(`/R60/Pages/menu.jsp?stfKbn=${encodeURIComponent(form.startupKbn)}`, '_blank')
}

async function onGenerateUrl() {
  error.value = ''
  const response = await generateUrlApi({
    stfCd: form.userId,
    stfKbn: form.startupKbn,
    gmnId: form.screen,
    kgnKbn: form.authorityKbn,
  }) as any
  if (response.errorCode !== '0') {
    error.value = response.messageId ?? 'URL を生成できませんでした'
    return
  }
  form.url = response.url
}

function onClose() {
  if (window.confirm('画面を閉じてもよろしいですか？')) {
    window.close()
  }
}
</script>

<style scoped>
.login-screen { max-width: 480px; margin: 48px auto; display: grid; gap: 12px; }
.datetime { color: #555; }
.hint { color: #666; font-size: 0.9em; }
.error { color: #b00020; }
</style>

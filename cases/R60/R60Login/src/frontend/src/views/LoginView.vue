<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchInit, postGenerateUrl, postLogin, type Item } from "../api/login";

const title = "共通マスタ　ログイン";
const stfCd = ref("");
const stfKbn = ref("3");
const gmnId = ref("");
const kgnKbn = ref("Y");
const url = ref("");
const pageList = ref<Item[]>([]);
const kbnList = ref<Item[]>([]);

onMounted(async () => {
  const r = await fetchInit();
  pageList.value = r.pageList ?? [];
  kbnList.value = r.kbnList ?? [];
  gmnId.value = pageList.value[0]?.value ?? "";
});

async function onLogin() {
  const r = await postLogin({ stfCd: stfCd.value, stfKbn: stfKbn.value, gmnId: gmnId.value, kgnKbn: kgnKbn.value });
  if (r.errorCode !== "0") return;          // 業務エラーはセッションエラー画面へ（共通部品）
  window.open(url.value, "_blank");
}

async function onGenerateUrl() {
  const r = await postGenerateUrl({ stfCd: stfCd.value, stfKbn: stfKbn.value, gmnId: gmnId.value, kgnKbn: kgnKbn.value });
  if (r.errorCode === "0" && r.url) url.value = r.url;
}

function onMenu() { window.open(`/R60/Pages/menu.jsp?stfKbn=${stfKbn.value}`, "_blank"); }
function onClose() { if (window.confirm("画面を閉じます。よろしいですか？")) window.close(); }
</script>

<template>
  <div class="login">
    <h1>{{ title }}</h1>
    <div class="row"><label>ユーザーＩＤ</label>
      <input v-model="stfCd" maxlength="7" placeholder="半角7桁" /></div>
    <div class="row"><label>起動区分</label><input v-model="stfKbn" />
      <span class="hint">1：本店ユーザー、2：工場ユーザー、3：システム管理者</span></div>
    <div class="row"><label>画面</label>
      <select v-model="gmnId">
        <option v-for="p in pageList" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select></div>
    <div class="row"><label>権限区分</label>
      <select v-model="kgnKbn">
        <option v-for="k in kbnList" :key="k.value" :value="k.value">{{ k.label }}</option>
      </select></div>
    <div class="row"><label>URL</label><input v-model="url" maxlength="150" /></div>
    <div class="actions">
      <button @click="onLogin">ログイン</button>
      <button @click="onMenu">メニュー</button>
      <button @click="onGenerateUrl">URL出力</button>
      <button @click="onClose">閉じる</button>
    </div>
  </div>
</template>

<style scoped>
.login { max-width: 720px; margin: 24px auto; font-family: Meiryo, sans-serif; }
.row { display: flex; gap: 12px; align-items: center; margin: 8px 0; }
.row label { width: 120px; }
.row input, .row select { flex: 1; padding: 4px 6px; }
.hint { color: #666; font-size: 12px; }
.actions { display: flex; gap: 12px; margin-top: 16px; }
</style>

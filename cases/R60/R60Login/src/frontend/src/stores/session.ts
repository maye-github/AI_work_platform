import { defineStore } from 'pinia'

export const useSessionStore = defineStore('session', {
  state: () => ({
    userInfo: null as Record<string, unknown> | null,
    mngInfo: null as Record<string, unknown> | null,
  }),
  actions: {
    setUser(userInfo: Record<string, unknown>, mngInfo: Record<string, unknown>) {
      this.userInfo = userInfo
      this.mngInfo = mngInfo
    },
  },
})

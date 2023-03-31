import { ref } from 'vue'
import { defineStore } from 'pinia'

interface User {
    userID: string,
    userHandle: string,
    userAvatar: string,
}
export const useUserStore = defineStore('user', () => {
  const user = ref<User>({ userID: '', userHandle: '', userAvatar: '' })
  function setUser(userID: string, userHandle: string, userAvatar: string) {
    user.value = {
        userID,
        userHandle,
        userAvatar,
    }
  }
  function getUserID() {
    return user.value.userID
  }

  return { user, setUser, getUserID }
})

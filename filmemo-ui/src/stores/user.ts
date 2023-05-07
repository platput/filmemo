import { ref } from 'vue'
import { defineStore } from 'pinia'

interface User {
    userID: string,
    userHandle: string,
    userAvatar: string,
}
export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User>({ userID: '', userHandle: '', userAvatar: '' })
  const players = ref<User[]>([])
  function setCurrentUser(userID: string, userHandle: string, userAvatar: string) {
    currentUser.value = {
        userID,
        userHandle,
        userAvatar,
    }
  }
  function addPlayer(userID: string, userHandle: string, userAvatar: string) {
    const playerIdExists = players.value.some((player) => player.userID === userID);
      if (!playerIdExists) {
        players.value.push({
          userID,
          userHandle,
          userAvatar,
        });
      }
  }
  function getCurrentUserID() {
    return currentUser.value.userID
  }
  function getPlayersList() {
    return players.value
  }
  function clear() {
    currentUser.value = {userID: '', userHandle: '', userAvatar: ''};
    players.value = []
  }
  return { currentUser, setCurrentUser, getCurrentUserID, addPlayer, getPlayersList, clear }
})

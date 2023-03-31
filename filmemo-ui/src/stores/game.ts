import { ref } from 'vue'
import { defineStore } from 'pinia'

interface Game {
  gameID: string;
  createdBy: string;
  userCount: number;
  roundCount: number;
  roundDuration: number;
}

export const useGameStore = defineStore('game', () => {
  const game = ref<Game>({ gameID: '', createdBy: '', userCount: 0, roundCount: 0, roundDuration: 0 })
  function setGame(gameID: string,  createdBy: string, userCount: number, roundCount: number, roundDuration: number) {
    game.value = {
        gameID,
        createdBy,
        userCount,
        roundCount,
        roundDuration
    }
  }
  function getGameId() {
    return game.value['gameID']
  }
  function getGameCreator() {
    return game.value.createdBy
  }

  return { game, setGame, getGameId, getGameCreator }
})

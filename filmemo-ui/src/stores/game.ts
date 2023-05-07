import { ref } from 'vue'
import { defineStore } from 'pinia'

interface Game {
  gameID: string;
  createdBy: string;
  userCount: number;
  roundCount: number;
  roundDuration: number;
  startedFlag: boolean;
}

export const useGameStore = defineStore('game', () => {
  const game = ref<Game>({ gameID: '', createdBy: '', userCount: 0, roundCount: 0, roundDuration: 0, startedFlag: false })
  function setGame(gameID: string,  createdBy: string, userCount: number, roundCount: number, roundDuration: number, startedFlag: boolean) {
    game.value = {
        gameID,
        createdBy,
        userCount,
        roundCount,
        roundDuration,
        startedFlag
    }
  }
  function getGameId() {
    return game.value['gameID']
  }
  function getGameCreator() {
    return game.value.createdBy
  }
  function checkIfGameHasStarted() {
    return game.value.startedFlag;
  }
  function setGameStartedFlag() {
    game.value.startedFlag = true;
  }
  function clear() {
    game.value = { gameID: '', createdBy: '', userCount: 0, roundCount: 0, roundDuration: 0, startedFlag: false }
  }

  return { game, setGame, getGameId, getGameCreator, clear, checkIfGameHasStarted, setGameStartedFlag }
})

const apiHost = import.meta.env.VITE_API_SERVER_URL;
const wsHost = import.meta.env.VITE_API_SERVER_WS_URL;

export default {
    apiCreateGameUrl: apiHost + "/game/create",
    apiAddPlayerUrl: apiHost + "/player/add",
    apiSubmitGuessUrl: apiHost + "/game/submit",
    apiVerifyGameUrl: apiHost + "/game/verify",
    apiGameWithResultsUrl: apiHost + "/game/results",
    apiStartGameUrl: apiHost + "/game/start",
    websocketUrl: wsHost + "/ws"
}
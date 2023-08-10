import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:5000/';
// 设置默认请求头为 JSON
axios.defaults.headers.common['Content-Type'] = 'application/json';

export const startGame = createAsyncThunk('game/start', async (board_size) => {
  const res = await axios.post('/create_session', {
    size: board_size,
    hum_first: 0
  });
  return res.data;
});

export const movePiece = createAsyncThunk('game/move', async ({player, position, sessionId}) => {
  const res = await axios.post(`/move/${sessionId}`, {
    location: position
  });
  return res.data;
});

export const endGame = createAsyncThunk('game/end', async (sessionId) => {
  const res = await axios.get(`/end_session/${sessionId}`);
  return res.data;
});

export const undoMove = createAsyncThunk('game/undo', async (sessionId) => {
  const res = await axios.get(`/undo/${sessionId}`);
  return res.data;
});

const initialState = {
  board: [],
  currentPlayer: null,
  winner: null,
  history: [],
  status: 'idle',
  sessionId: null,
  size: 15,
  loading: false,
  winner: 0,
};

export const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    tempMove: (state, action) => {
      const p = action.payload
      state.board[p[0]][p[1]] = state.currentPlayer;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(startGame.pending, (state) => {
        state.loading = true;
      })
      .addCase(startGame.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.current_player;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.status = 'playing';
        state.sessionId = action.payload.session_id;
        state.size = action.payload.size;
        state.loading = false;
      })
      .addCase(movePiece.pending, (state, action) => {
        state.loading = true;
      })
      .addCase(movePiece.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.current_player;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.loading = false;
      })
      .addCase(undoMove.pending, (state, action) => {
        state.loading = true;
      })
      .addCase(undoMove.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.current_player;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.loading = false;
      })
      .addCase(endGame.fulfilled, () => {
        return initialState;
      });
  },
});
export const { tempMove } = gameSlice.actions;
export default gameSlice.reducer;

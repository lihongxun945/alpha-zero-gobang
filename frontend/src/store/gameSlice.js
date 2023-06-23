import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:5000/';

export const startGame = createAsyncThunk('game/start', async (board_size) => {
  console.log('startGame', board_size)
  const res = await axios.post('/create_session');
  return res.data;
});

export const movePiece = createAsyncThunk('game/move', async (sessionId, move) => {
  const res = await axios.post(`/move/${sessionId}`, move);
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
};

export const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
  },
  extraReducers: (builder) => {
    builder
      .addCase(startGame.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.currentPlayer;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.status = 'playing';
      })
      .addCase(movePiece.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.currentPlayer;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
      })
      .addCase(undoMove.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.currentPlayer;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
      })
      .addCase(endGame.fulfilled, () => {
        return initialState;
      });
  },
});

export default gameSlice.reducer;

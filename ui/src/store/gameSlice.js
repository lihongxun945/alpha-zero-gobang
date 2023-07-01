import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { STATUS, board_size } from '../config';

axios.defaults.baseURL = 'http://127.0.0.1:5000/';

const config = {
  headers: {
    'Content-Type': 'application/json',
  }
}

export const startGame = createAsyncThunk('game/start', async (board_size) => {
  const data = {
    size: board_size,
    hum_first: 0,
    simulation_num: 100,
  }
  const res = await axios.post('/create_session', data, config);
  return res.data;
});

export const movePiece = createAsyncThunk('game/move', async ({ sessionId, location }) => {
  const res = await axios.post(`/move/${sessionId}`, { location }, config);
  return res.data;
});

export const endGame = createAsyncThunk('game/end', async (sessionId) => {
  const res = await axios.get(`/end_session/${sessionId}`, config);
  return res.data;
});

export const undoMove = createAsyncThunk('game/undo', async (sessionId) => {
  const res = await axios.get(`/undo/${sessionId}`, config);
  return res.data;
});

const initialState = {
  board: [],
  currentPlayer: null,
  winner: null,
  history: [],
  sessionId: null,
  status: 'idle',
};

export const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    setStatus: (state, action) => {
      state.status = action.payload;
    },
    doHumMove: (state, action) => {
      const location = action.payload
      state.board[Math.floor(location / board_size)][location % board_size] = state.currentPlayer;
      state.currentPlayer = -state.currentPlayer;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(startGame.pending, (state) => {
        state.status = STATUS.REQUESTING;
      })
      .addCase(startGame.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.current_player;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.sessionId = action.payload.session_id;
        state.status = STATUS.PLAYING;
      })
      .addCase(movePiece.pending, (state) => {
        state.status = STATUS.REQUESTING;
      })
      .addCase(movePiece.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.currentPlayer;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.status = STATUS.PLAYING;
      })
      .addCase(undoMove.pending, (state) => {
        state.status = STATUS.REQUESTING;
      })
      .addCase(undoMove.fulfilled, (state, action) => {
        state.board = action.payload.board;
        state.currentPlayer = action.payload.currentPlayer;
        state.winner = action.payload.winner;
        state.history = action.payload.history;
        state.status = STATUS.PLAYING;
      })
      .addCase(endGame.pending, (state) => {
        state.status = STATUS.REQUESTING;
      })
      .addCase(endGame.fulfilled, (state) => {
        state.status = STATUS.FINISHED;
        return initialState;
      });
  },
});

export default gameSlice.reducer;

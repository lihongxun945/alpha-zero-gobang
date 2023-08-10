import Board from './components/board';
import './App.css';
import { useDispatch, useSelector } from 'react-redux';
import { startGame } from './store/gameSlice';
import { useEffect } from 'react';
import { board_size } from './config';

function App() {
  const dispatch = useDispatch();
  const { loading, winner } = useSelector((state) => state.game);
  const start = () => {
    dispatch(startGame(board_size));
  };
  return (
    <div className="App">
      <Board />
      <div className="buttons">
        <button onClick={start} disabled={loading}>开始游戏</button>
      </div>
      <div className="status"></div>
    </div>
  );
}

export default App;

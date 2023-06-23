import Board from './components/board';
import './App.css';
import { useDispatch, useSelector } from 'react-redux';
import { startGame } from './store/gameSlice';
import { useEffect } from 'react';
import { board_size } from './config';

function App() {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(startGame(board_size));
  }, [])
  return (
    <div className="App">
      <Board />
    </div>
  );
}

export default App;

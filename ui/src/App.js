import logo from './logo.svg';
import './App.css';
import Board from './components/board'
import Controls from './components/controls'
import { startGame } from './store/gameSlice';
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { board_size } from './config';


function App() {
  const dispatch = useDispatch();
  useEffect(() => {
    console.log('dispatching startGame');
    dispatch(startGame(board_size));
  }, [])
  return (
    <div className="App">
      <div className="title">Alpha Zero Gobang</div>
      <Board />
      <Controls />
    </div>
  );
}

export default App;

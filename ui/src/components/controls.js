import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button } from 'antd-mobile';
import { startGame, endGame, undoMove } from '../store/gameSlice'; // 请将 'yourSlicePath' 替换为实际的文件路径
import { STATUS } from '../config';
import './controls.css';

// 帮我用React写一个组件，有开始、悔棋、认输三个按钮，在不同的状态下要禁用对应的按钮，这是对应的store代码
const Controls = () => {
  const dispatch = useDispatch();
  const { status, sessionId } = useSelector(state => state.game);

  const handleStartGame = () => {
    dispatch(startGame(15)); // 假设棋盘大小为 15
  };

  const handleUndoMove = () => {
    dispatch(undoMove(sessionId)); // 假设 sessionId 是可用的
  };

  const handleEndGame = () => {
    dispatch(endGame(sessionId)); // 假设 sessionId 是可用的
  };

  return (
    <div className="controls">
      <Button color='success' fill='solid' onClick={handleStartGame} disabled={status !== STATUS.FINISHED}>
        开始游戏
      </Button>
      <Button color='warning' fill='solid' onClick={handleUndoMove} disabled={status !== STATUS.PLAYING}>
        悔棋
      </Button>
      <Button color='danger' fill='solid' onClick={handleEndGame} disabled={status !== STATUS.PLAYING}>
        认输
      </Button>
    </div>
  );
};

export default Controls;


import React, { useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { startGame, movePiece } from '../store/gameSlice';
import './board.css';
import bg from '../assets/bg.jpg';
import { board_size } from '../config';

/*
帮我用React实现一个Board组件，实现的功能是：
显示五子棋棋盘，当用户点击棋盘的时候，可以把点击位置换算成对应的棋子坐标。内部状态包括棋盘上所有棋子的坐标，历史记录，以及下一步轮到谁下。
不要用图片，直接用CSS画棋盘和棋子。
*/

const Board = () => {
  const dispatch = useDispatch();
  const { board, currentPlayer, history } = useSelector((state) => state.game);
  
  const handleClick = (i, j) => {
    console.log(i, j)
    if (board[i][j] === null) {
      dispatch(movePiece({ player: currentPlayer, position: [i, j] }));
    }
  };

  const cellStyle = {
    width: `${350/board_size}px`,
    height: `${350/board_size}px`,
  };

  return (
    <div className="board" style={{backgroundImage: `url(${bg})`}}>
      {board.map((row, i) => (
        <div key={i} className="board-row">
          {row.map((cell, j) => {
            let cellClassName = 'cell';
            if (i === 0) {
              cellClassName += ' top';
            }
            if (i === board_size - 1) {
              cellClassName += ' bottom';
            }
            if (j === 0) {
              cellClassName += ' left';
            }
            if (j === board_size - 1) {
              cellClassName += ' right';
            }
            return (
              <div key={j} className={cellClassName} style={cellStyle} onClick={() => handleClick(i, j)}>
                  {cell && <div className={`piece ${cell === 1 ? 'black': 'white'}`}></div>}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  );
};

export default Board;

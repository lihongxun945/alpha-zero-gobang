# -*- coding: utf-8 -*-
'''
帮我用Flask写一个服务端，以API的形式提供五子棋AI服务，用已经完成的Board、Net、MCTS 类来实现，要能支持多个会话，以支持多个用户同时接入，实现以下API 接口：
2. start: 启动服务，监听端口，接收用户请求，根据用户请求的不同，调用不同的方法
3. create_session: 创建一个会话，返回会话ID, 会话ID是一个hash值，用于标识一个会话。创建会话的时候可以指定棋盘大小，默认为15，指定先手角色，默认为AI先手，指定蒙特卡洛树搜索次数，默认为100. 默认保存最多100个会话，超过100个会话，删除最早创建的会话
4. get_session: 获取会话的状态，接收sessionid，返回一个json对象，包含棋盘状态、落子历史记录、当前落子方、胜利方、棋盘大小、蒙特卡洛树搜索次数等
5. move: 落子，接收sessionid和落子位置，返回落子结果，如果用户落子合法，则调用AI走棋，并返回AI走棋之后的结果，和get_session 保持一致，如果落子不合法，返回错误信息
6. undo: 悔棋，接收sessionid，返回悔棋结果，每一次悔棋2步
7. end_session: 结束会话，接收sessionid，返回结束结果
依赖的三个类的说明如下：
Board 包含这几个方法
1. __init__(size=15, first_player=1) 初始化
2. move(location, color=None) 走棋
3. undo() 悔棋
4. get_current_player_color()  返回当前走棋的角色
5. get_winner() 返回胜利方，如果没有胜利方，返回0
Board 还包含有一个 board 属性，用于保存棋盘状态，board 是一个一维数组，长度为 size * size，每个元素的值为 0, 1, -1，分别表示空位、黑子、白子. history 属性，用于保存落子历史记录，history 是一个二维数组，每个元素是一个二元组，第一个元素是落子位置，第二个元素是落子颜色
Net 有初始化方法 __init__(board_size=15)
MCST 包含这几个方法:
1. __init__(board, net, simulation_num)  初始化
2. move() 走棋
'''
import numpy as np
from alpha_zero.net import Net
from alpha_zero.board import Board
from alpha_zero.mcts import MCTS
from flask import Flask, request, jsonify
import json
from collections import OrderedDict
from uuid import uuid4

app = Flask(__name__)

# 会话池
sessions = OrderedDict()

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/create_session', methods=['POST'])
def create_session():
  if len(sessions) > 100:
    sessions.popitem(last=False) # 删除最早创建的会话

  session_id = str(uuid4()) # 生成唯一会话ID
  size = request.json.get('size', 15)
  first_player = request.json.get('first_player', 1)
  simulation_num = request.json.get('simulation_num', 100)

  board = Board(size=size, first_player=first_player)
  net = Net(size=size)
  mcts = MCTS(board, net, simulation_num=simulation_num)

  sessions[session_id] = {
    'board': board,
    'net': net,
    'mcts': mcts
  }

  return jsonify({'session_id': session_id})

@app.route('/get_session/<session_id>', methods=['GET'])
def get_session(session_id):
  print("get_session", session_id, "sessions", sessions.keys(), "len", len(sessions))
  session = sessions.get(session_id)
  if session is None:
    return jsonify({'error': 'Invalid session_id'}), 400

  board = session['board']
  mcts = session['mcts']

  return jsonify({
    'board': board.board,
    'history': board.history,
    'current_player': board.get_current_player_color(),
    'winner': board.get_winner(),
    'size': board.size,
    'simulation_num': mcts.simulation_num
  })

@app.route('/move/<session_id>', methods=['POST'])
def move(session_id):
  session = sessions.get(session_id)
  if session is None:
    return jsonify({'error': 'Invalid session_id'}), 400

  location = request.json.get('location')
  if location is None:
    return jsonify({'error': 'Missing location'}), 400

  board = session['board']
  mcts = session['mcts']
  board.move(location)
  action = mcts.move()
  print(action)
  board.move(action)

  return get_session(session_id)

@app.route('/undo/<session_id>', methods=['POST'])
def undo(session_id):
  session = sessions.get(session_id)
  if session is None:
    return jsonify({'error': 'Invalid session_id'}), 400

  board = session['board']
  board.undo()
  board.undo()

  return get_session(session_id)

@app.route('/end_session/<session_id>', methods=['DELETE'])
def end_session(session_id):
  session = sessions.pop(session_id, None)
  if session is None:
    return jsonify({'error': 'Invalid session_id'}), 400

  return jsonify({'status': 'success'})


if __name__ == '__main__':
  app.run(port=5000, debug=True)

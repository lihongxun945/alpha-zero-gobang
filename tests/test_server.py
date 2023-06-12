# -*- coding: utf-8 -*-
'''
给上面写的服务端写一个测试用例
'''

import sys
sys.path.append(r"..")
import unittest
from server import app
from alpha_zero.board import Board

class GobangServerTest(unittest.TestCase):
  def setUp(self):
    self.app = app
    self.client = self.app.test_client()

  def create_session(self):
    response = self.client.post('/create_session', json={'size': 15, 'first_player': 1, 'simulation_num': 10})
    return response.get_json()['session_id']

  def test_create_session(self):
    response = self.client.post('/create_session', json={'size': 15, 'first_player': 1, 'simulation_num': 10})
    self.assertEqual(response.status_code, 200)
    json_data = response.get_json()
    self.assertIn('session_id', json_data)

  def test_get_session(self):
    # First, create a session
    session_id = self.create_session()

    # Then, get the session
    response = self.client.get(f'/get_session/{session_id}')
    self.assertEqual(response.status_code, 200)
    json_data = response.get_json()
    self.assertEqual(json_data['board'], Board(size=15).board)
    self.assertEqual(json_data['history'], [])
    self.assertEqual(json_data['current_player'], 1)
    self.assertEqual(json_data['winner'], 0)
    self.assertEqual(json_data['size'], 15)

  def test_move(self):
    # First, create a session
    session_id = self.create_session()

    # Then, make a move
    response = self.client.post(f'/move/{session_id}', json={'location': 120})
    self.assertEqual(response.status_code, 200)
    json_data = response.get_json()
    board = Board(size=15)
    board.move(120)
    self.assertNotEqual(json_data['board'], board.board)

  def test_undo(self):
    # First, create a session and make a move
    session_id = self.create_session()
    self.client.post(f'/move/{session_id}', json={'location': 120})

    # Then, undo the move
    response = self.client.post(f'/undo/{session_id}')
    self.assertEqual(response.status_code, 200)
    json_data = response.get_json()
    self.assertEqual(json_data['board'], Board(size=15).board)
  def test_end_session(self):
    # First, create a session
    session_id = self.create_session()

    # Then, end the session
    response = self.client.delete(f'/end_session/{session_id}')
    self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
  unittest.main()

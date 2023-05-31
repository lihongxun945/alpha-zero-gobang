## Alpha Zero Gobang

Alpha Zero原理实现的五子棋AI，主要参考了Alpha Zero相关论文和github上的一些开源项目（见下文），代码主要由chatgpt生成但是做了一些调整。写这个项目的目的是为了研究Alpha Zero，同时测试chatgpt在较复杂的项目中的表现。

## 如何运行

第一步，安装依赖 `pip install -r requirements.txt`

第二步，启动训练 `python start_train.py`

## 如何启用GPU加速

TODO

## 单元测试

根目录下执行命令 `python -m unittest discover tests` 可以启动单元测试

## 代码说明

TODO

- `Board`: 

## 功能开发
- [x] 完成基本代码逻辑，能正常训练
- [x] 完善单元测试
- [x] 增加狄利克雷噪声以增加探索可能性
- [x] 增加棋盘镜像和翻转功能以增加训练数据
- [ ] 增加UI界面
- [ ] 优化训练速度
- [ ] 增加多进程支持，多显卡并行训练

## 参考代码

主要参考了如下两个项目的代码：
- [alpha-zero-general](https://github.com/suragnair/alpha-zero-general)
- [Alpha-Gobang-Zero](https://github.com/zhiyiYo/Alpha-Gobang-Zero)

非常感谢上述两个项目的作者，你们的开源项目和博客给我非常大的帮助。个人不是AI专业的，业余研究使用，有任何错误欢迎指正。

## 参考文档
- [Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm](https://arxiv.org/pdf/1712.01815.pdf)
- [Mastering the game of Go without human knowledge](https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ)
- [如何使用自对弈强化学习训练一个五子棋机器人Alpha Gobang Zero](https://www.cnblogs.com/zhiyiYo/p/14683450.html)
- [A Simple Alpha(Go) Zero Tutorial](http://web.stanford.edu/~surag/posts/alphazero.html)

## 协议

MIT License

Copyright (c) 2018 Surag Nair

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

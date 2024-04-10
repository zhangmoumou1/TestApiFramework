#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 装饰器
# @@Copyright © zhangmoumou, Inc. All rights reserved.

from flask import Flask, request, jsonify
from flasgger import Swagger

template_config = {
  "info": {
    "title": "接口项目示例",
    "description": "",
    "version": "1.0.0"
  }
}

app = Flask(__name__)
app.json.ensure_ascii = False
Swagger(app, template=template_config)

# 假设博客文章数据存储在一个列表中
articles = [
    {"id": 1, "title": "行路难", "content": "长风破浪会有时，直挂云帆济沧海。"},
    {"id": 2, "title": "酬乐天扬州初逢席上见赠", "content": "沉舟侧畔千帆过，病树前头万木春。"}
]

# 假设的有效token
VALID_TOKEN = "9779dd9e-aa3d-435f-a431-e699a67fe616"

@app.route('/api/login', methods=['POST'])
def login():
    """
    登录获取token
    ---
    tags:
      - 注册登录
    parameters:
      - in: body
        name: body
        required: true
        description: json传参
        schema:
          type: object
          required:
            - message
          properties:
            username:
              type: string
              description: 用户名
              example: "test"
            password:
              type: string
              description: 密码
              example: "123456"
    responses:
      200:
        description: 登录成功
      402:
        description: 登录失败，账号不存在
      403:
        description: 登录失败，密码错误
      404:
        description: 登录失败，传参有误
    """
    data = request.get_json()
    if "username" in data and "password" in data:
        if data["username"] != 'test':
            return jsonify({'success': False, 'code': '402', 'message': '登录失败，账号不存在！'}), 402
        if data["password"] != '123456':
            return jsonify({'success': False, 'code': '402', 'message': '登录失败，密码错误！'}), 402
        return jsonify({'success': True, 'code': '200', 'message': u'登录成功！', 'data': VALID_TOKEN}), 200
    else:
        return jsonify({'success': False, 'code': '400', 'message': '登录失败，传参有误！'}), 404


@app.route('/api/articleList', methods=['GET'])
def get_article_list():
    """
    文章列表
    ---
    tags:
      - 文章管理
    responses:
      200:
        description: 返回文章列表数据
      401:
        description: 登录失效，无效的token
    """
    token = request.headers.get('token')
    if token != VALID_TOKEN:
        return jsonify({'success': False, 'code': '401', 'message': '登录失效，无效的token！'}), 401
    return jsonify({'success': True, 'code': '200', 'data': articles})

@app.route('/api/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    获取文章信息
    ---
    tags:
      - 文章管理
    parameters:
      - article_id: language
        in: path
        type: int
        required: true
        description: 文章id
    responses:
      200:
        description: 返回具体文章数据
      401:
        description: 登录失效，无效的token
      404:
        description: 未找到对应的文章
    """
    token = request.headers.get('token')
    if token != VALID_TOKEN:
        return jsonify({'success': False, 'code': '401', 'message': '登录失效，无效的token！'}), 401
    article = next((p for p in articles if p["id"] == article_id), None)
    if article:
        return jsonify({'success': True, 'code': '200', 'data': article})
    else:
        return jsonify({'success': False, 'code': '404', "message": "未找到对应的文章！"}), 404

@app.route('/api/addArticle', methods=['POST'])
def create_article():
    """
    创建新文章
    ---
    tags:
      - 文章管理
    parameters:
      - in: body
        name: body
        required: true
        description: json传参
        schema:
          type: object
          required:
            - message
          properties:
            id:
              type: int
              description: 文章id
              example: 文章id
            title:
              type: string
              description: 文章标题
              example: "文章标题"
            content:
              type: string
              description: 文章内容
              example: "文章内容"
    responses:
      200:
        description: 添加新文章成功
      401:
        description: 登录失效，无效的token
      404:
        description: 创建新文章数据有误
    """
    token = request.headers.get('token')
    if token != VALID_TOKEN:
        return jsonify({'success': False, 'code': '401', 'message': '登录失效，无效的token！'}), 401
    data = request.get_json()
    if "title" in data and "content" in data:
        new_article = {
            "id": len(articles) + 1,
            "title": data["title"],
            "content": data["content"]
        }
        articles.append(new_article)
        return jsonify({'success': True, 'code': '200', 'message': '添加新文章成功！'}), 200
    else:
        return jsonify({'success': False, 'code': '400', "message": "创建新文章数据有误！"}), 404

@app.route('/api/updateArticle/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """
    更新文章
    ---
    tags:
      - 文章管理
    parameters:
      - id: language
        in: path
        type: int
        required: true
        description: 文章id
      - in: body
        name: body
        required: true
        description: json传参
        schema:
          type: object
          required:
            - message
          properties:
            id:
              type: int
              description: 文章id
              example: 文章id
            title:
              type: string
              description: 文章标题
              example: "文章标题"
            content:
              type: string
              description: 文章内容
              example: "文章内容"
    responses:
      200:
        description: 更新文章信息成功
      401:
        description: 登录失效，无效的token
      400:
        description: 更新文章失败，文章不存在
    """
    token = request.headers.get('token')
    if token != VALID_TOKEN:
        return jsonify({'success': False, 'code': '401', 'message': '登录失效，无效的token！'}), 401
    article = next((p for p in articles if p["id"] == article_id), None)
    if article:
        data = request.get_json()
        article["title"] = data.get("title", article["title"])
        article["content"] = data.get("content", article["content"])
        return jsonify({'success': True, 'code': '200', 'message': '更新文章信息成功！'})
    else:
        return jsonify({'success': False, 'code': '404', "message": "更新文章失败，文章不存在！"}), 404

@app.route('/api/deleteArticle/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """
    删除文章
    ---
    tags:
      - 文章管理
    parameters:
      - article_id: language
        in: path
        type: int
        required: true
        description: 文章id
    responses:
      200:
        description: 删除文章成功
      401:
        description: 登录失效，无效的token
      404:
        description: 文章不存在，删除失败
    """
    token = request.headers.get('token')
    if token != VALID_TOKEN:
        return jsonify({'success': False, 'code': '401', 'message': '登录失效，无效的token！'}), 401
    global articles
    article = [p for p in articles if p["id"] != article_id]
    num = 0
    if article:
        for this_article in articles:
            if this_article['id'] == article_id:
                articles.pop(num)
            num += 1
        return jsonify({'success': True, 'code': '200', 'message': '删除文章成功！'})
    else:
        return jsonify({'success': False, 'code': '404', "message": "文章不存在，删除失败！"}), 404

if __name__ == '__main__':
    app.run()
    app.json.ensure_ascii = False
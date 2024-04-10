#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @@Author: 张某某
# @@Create Date: 2023/02/16 10:28
# @@Description: 发送消息功能构造
# @@Copyright © zhangmoumou, Inc. All rights reserved.

from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard
from app.core.methods import env, ding_token
class MessageConstructor(object):

    @staticmethod
    def send_ding_msg(*args):
        """
        发送钉钉消息
        :return:
        """
        try:
            btns1 = [{"title": "查看报告详情", "actionURL": '报告地址'}]
            content = "项目：多保鱼  \n" \
                      "环境：{}  \n" \
                      "总用例数：{}  \n" \
                      "通过数：{}  \n" \
                      "错误/失败数：{}  \n" \
                      "忽略数：{}  \n" \
                      "覆盖率：{}  \n" \
                      "接口完成率：80%  \n" \
                      "耗费时间：{}  \n" \
                      "账密：qa/qa".format(env, args[0], args[1], args[2] + args[3], args[4],
                                          '50%', args[5])
            actioncard1 = ActionCard(title='{}环境执行结果'.format(env),
                                     text=content,
                                     btns=btns1
                                     )
            if (args[2] + args[3]) > 0:
                ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=' + ding_token
                robot1 = DingtalkChatbot(ding_url)
                robot1.send_action_card(actioncard1)
        except:
            raise

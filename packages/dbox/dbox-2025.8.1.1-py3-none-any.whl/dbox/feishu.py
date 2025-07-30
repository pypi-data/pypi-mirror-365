#!/usr/bin/env python
# coding = utf-8
"""功能简要说明
author：dqy
邮箱：yu12377@163.com
time：2021/6/15 16:57
"""
import json
import hmac
import base64
import hashlib
import logging
import requests
from dbox import time as time_utils
from dbox import my_http as http_utils


logger = logging.getLogger("DBoxUtils")

url_model = "https://open.feishu.cn/open-apis/bot/v2/hook/{0}"
headers = {"Content-Type": "application/json; charset=utf-8"}


def get_sign(secret: str) -> tuple:
    timestamp = time_utils.get_timestamp(length=10)
    raw_str = f"{timestamp}\n{secret}".encode("utf-8")
    hmac_code = hmac.new(raw_str, "".encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign, timestamp


def send_text_alert_message(message: str, receiver: dict, app_name: str = ""):
    """发送文本消息
    :param app_name: 消息来源应用
    :param message: 消息内容
    :param receiver: dict, 必须包含id与secret字段，消息接收者——飞书群自定义消息机器人
    """
    try:
        sign, timestamp = get_sign(receiver["secret"])
        url = f"{url_model}{receiver['id']}"
        if app_name:
            message += f"。消息来源：{app_name}"
        payload = {
            "sign": sign,
            "timestamp": timestamp,
            "msg_type": "text",
            "content": {"text": message},
        }

        res = requests.post(url, headers=headers, json=payload)
        content_type = res.headers.get("Content-Type")
        if (
            res.status_code == 200
            and content_type is not None
            and "application/json" in content_type
            and res.json()["StatusCode"] == 0
        ):
            http_utils.format_output(payload)
            logger.info("消息发送成功")
        else:
            http_utils.format_output(res, level="error")
            logger.error("消息发送失败")
    except Exception as _error:
        logger.exception(_error)


def send_post_message(title: str, content_list: list, receiver: dict, app_name: str = ""):
    """发送富文本消息"""
    try:
        sign, timestamp = get_sign(receiver["secret"])
        url = f"{url_model}{receiver['id']}"
        if app_name:
            title += f"({app_name})"
        payload = {
            "sign": sign,
            "timestamp": timestamp,
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content_list,
                    }
                }
            },
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
        except Exception as _e:
            logger.exception(_e)
            logger.error(f"访问FeiShu接口失败")
            logger.info(payload)
            raise
        else:
            try:
                content_type = res.headers.get("Content-Type")
                if (
                    res.status_code == 200
                    and content_type is not None
                    and "application/json" in content_type
                    and res.json()["StatusCode"] == 0
                ):
                    http_utils.format_output(payload)
                    logger.info(f"消息发送成功")
                else:
                    http_utils.format_output(res, level="error")
                    logger.error(f"消息发送失败")
            except Exception as _e:
                logger.exception(_e)
                logger.error(res.text)
                logger.info(payload)
    except Exception as _error:
        logger.exception(_error)


if __name__ == "__main__":
    pass

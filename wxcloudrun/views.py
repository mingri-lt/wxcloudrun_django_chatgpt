# -*- coding: utf-8 -*-
import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters

import openai
# 设置openai的api key
openai.api_key = "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"
messages = [{"role": "system", "content": "You are a helpful assistant."}]

logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})

def dialogue(request, _):
    # GET 请求，返回hello world
    if request.method == 'GET' or request.method == 'get':
        return JsonResponse({'code': 0, 'data': 'hello world'},
                            json_dumps_params={'ensure_ascii': False})
    # POST 请求，返回请求体
    elif request.method == 'POST' or request.method == 'post':
        logger.info('dialogue req: {}'.format(request.body))
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if 'content' not in body:
            return JsonResponse({'code': -1, 'errorMsg': '缺少content参数'},
                                json_dumps_params={'ensure_ascii': False})
        global messages
        messages.append({"role": "user", "content": body['content']})
        reponse = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        res_content = reponse["choices"][0]["message"]["content"]
        res_content = res_content.encode('utf-8').decode('utf-8')
        messages.append({"role": "assistant", "content": res_content})
        return JsonResponse({'code': 0, 'data': res_content},
                            json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})

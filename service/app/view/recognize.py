# -*- coding:utf-8 -*-
from flask import Flask, render_template, request, session, Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse

import os
import cv2
import json
import numpy as np
import traceback
import threading
import time

from ..model.doc import RecResultModel, DepositoryDocModel
from ..modules.create_result_data import write_to_file

recognize = Blueprint('recognize', __name__)
api = Api(recognize)
rec_result = RecResultModel()

"""錯誤訊息追蹤"""
def exception_to_string(excp):
   stack = traceback.extract_stack()[:-3] + traceback.extract_tb(excp.__traceback__)
   pretty = traceback.format_list(stack)
   return ''.join(pretty) + '\n  {} {}'.format(excp.__class__,excp)


# 存管公文辨識
class DepositoryDoc(Resource):
    def post(self):
        # 讀取post來的資訊
        try:
            post_case_type = request.form.get('case_type', '') # 文件種類
            post_image = request.files['file'].read() # 影像
            post_seqNo = request.form.get('seqNo', '') # 案件號
            print(f'post_case_type : {post_case_type}')
            print(f'post_seqNo : {post_seqNo}')
            img = cv2.imdecode(np.frombuffer(post_image, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except Exception as err:
            response = make_response(jsonify(
                statusCode=-1,
                statusDesc=f"解析post資料時錯誤，請確認json內容無誤"
            ), 200)
            response.headers['Content-Type'] = 'application/json;charset=UTF-8'
            return response
            
        try:

            t_job = threading.Thread(
                target=write_to_file,
                args=(post_seqNo, img, post_case_type),
                name=f't_{post_seqNo}'
            )
            t_job.start()
            time.sleep(1)

            response = make_response(jsonify(
                statusCode=0,
                statusDesc=f"已確認收到任務請求，案件號{post_seqNo}"
            ), 200)
            response.headers['Content-Type'] = 'application/json;charset=UTF-8'
            return response

        except Exception as err:
            response = make_response(jsonify(
                statusCode=-2,
                statusDesc=f"建立線程失敗，案件號{post_seqNo}"
            ), 500)
            response.headers['Content-Type'] = 'application/json;charset=UTF-8'
            return response

    def get(self):
        # 取得辨識結果
        try:
            seqNo = request.args.get('seqNo')
            print(seqNo)
            path = f'app/data/{seqNo}.json'
            if os.path.exists(path):
                f = open(path, encoding='utf-8')
                data = json.load(f)
                response = make_response(data, 200)
                response.headers['Content-Type'] = 'application/json;charset=UTF-8'
                return response
            else:
                response = make_response(jsonify(
                    Status=0,
                    Msg=f"查無此件號{seqNo}辨識結果，可能還在辨識或是件號錯誤"
                ), 200)
                response.headers['Content-Type'] = 'application/json;charset=UTF-8'
                return response
        except Exception as err:
            response = make_response(jsonify(
                Status=-1,
                Msg=f"取得辨識結果失敗，案件號{seqNo}"
            ), 500)
            response.headers['Content-Type'] = 'application/json;charset=UTF-8'
            return response


api.add_resource(DepositoryDoc, '/depository')

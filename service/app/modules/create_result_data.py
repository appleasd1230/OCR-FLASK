# -*- coding:utf-8 -*-
from .predict import *
import os
import json

# 將結果寫入檔案
def write_to_file(seqNo, img, caseType):
    file_path = f'app/data/{seqNo}.json'

    if caseType == 'LE2' or caseType == 'LE3':
        jsonStr = depository_doc_rec(img)
    
        print('開始')
        # 如果存在檔案就將結果加入，若無重新建置
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    preJsonObj = json.load(f)
                    f.close()

                JsonObj = json.loads(jsonStr)

                # 如果新的欄位辨識結果較長，取新的
                for i in range(len(JsonObj['value'])):
                    if len(JsonObj['value'][i]['text']) > len(preJsonObj['value'][i]['text']):
                        preJsonObj['value'][i]['text'] = JsonObj['value'][i]['text']

                # 寫入更新過的json
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(preJsonObj, ensure_ascii=False))
                    f.close()

            except:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(jsonStr)
                    f.close()

        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(jsonStr)
                f.close()

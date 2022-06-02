# -*- coding:utf-8 -*-
from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
import re
import json
import traceback

"""paddle parameter"""
ocr = PaddleOCR(
    det_model_dir=r'app/ml_models/ppocv_server_v2.0/ch_ppocr_server_v2.0_det_infer/',
    rec_model_dir=r'app/ml_models/ppocv_server_v2.0/ch_ppocr_server_v2.0_rec_infer/',
    # rec_model_dir=r'../models/cathay_models/le/',
    rec_char_dict_path=r'app/dict/dict.txt',
    cls_model_dir=r'app/ml_models/ppocr_mobile_v2.0/ch_ppocr_mobile_v2.0_cls_infer/',
    use_gpu=False,
    det_db_thresh = 0.1,
    det_db_box_thresh=0.1,
    use_angle_cls=True,
    use_space_char=True,
    lang="ch",
)

"""錯誤訊息追蹤"""
def exception_to_string(excp):
   stack = traceback.extract_stack()[:-3] + traceback.extract_tb(excp.__traceback__)
   pretty = traceback.format_list(stack)
   return ''.join(pretty) + '\n  {} {}'.format(excp.__class__,excp)

"""存管公文辨識"""
def depository_doc_rec(img):
    """公文辨識結果class"""
    class depository_doc(object):
        def __init__(self):
            self.documentType = '公文' # 文件類型
            self.documentName = '' # 檔案名稱
            self.status = '0' # 狀態 0:處理中 / 1:完成 / -1:異常
            self.msg = '' # 如果異常紀錄訊息
            self.value = [] # 欄位and值

    # Create Object
    rec_result = depository_doc()
    
    try:
        res = ocr.ocr(img) # 開始辨識
    except Exception as err:
        rec_result.status = '-1' # 異常
        rec_result.msg = '辨識過程失敗，請至log查看原因。' # 辨識失敗
        print(exception_to_string(err))
        return json.dumps(rec_result.__dict__, ensure_ascii=False)

    """正規辨識結果"""
    results = ''
    results_lst = [res[i][1][0] for i in range(len(res))] # 將辨識出來的陣列儲存起來
    results = '|'.join(results_lst) # 將辨識出來的文字用「|」join起來
    results_txt = ''.join(results_lst) # 全文結果，無分割

    # 發文機關
    try:
        new_results = '|' + results # 避免關鍵字出現在第一排
        authority = re.search(r'([|][\w\s]{1,25})(執行署|地方法院|公路局|檢察署|監理所|法務部|稅捐|交通部|移民署|內政部|稅務局|警察局)(.*?)[|]', new_results).group()
        authority = re.sub(r'[^\w\s]', '', authority) # 去除符號
        authority = re.sub(r'台', '臺', authority) # 去除符號
        authority = re.sub(r'臺南', '台南', authority) # 去除符號
    except IndexError:
        try:
            address_index = results.find('址：') # 找出地址位置
            authority = results_lst[results[:address_index].count('|')-1] # 發文機關，找出地址位於陣列第幾列之後取前一列
            authority = re.sub(r'台', '臺', authority) # 去除符號
            authority = re.sub(r'臺南', '台南', authority) # 去除符號
        except:
            authority = ''
    except:
        authority = ''

    # 發文日期
    try:
        date = re.findall(r'中華民國(\d*?年\d*?月\d*?日)', results_txt) # 日期
        date = date[0]
        date = re.sub(u'[^\u0030-\u0039]', '-', date) # 只保留數字部分
        date = re.split('-', date) # 將日期轉為List
        date = [x for x in date if x != ''] # 將空白資料移出list
        date = str(int(date[0]) + 1911) + str('{:0>2d}'.format(int(date[1]))) + str('{:0>2d}'.format(int(date[2]))) # 將日期轉為西元
    except IndexError:
        try:
            date_index = results.find('文日期') # 找出日期位置
            date = results_lst[results[:date_index].count('|')] # 發文日期
            date = re.sub(u'[^\u0030-\u0039]', '-', date) # 只保留數字部分
            date = re.split('-', date) # 將日期轉為List
            date = [x for x in date if x != ''] # 將空白資料移出list
            date = str(int(date[0]) + 1911) + str('{:0>2d}'.format(int(date[1]))) + str('{:0>2d}'.format(int(date[2]))) # 將日期轉為西元
        except:
            date = ''
    except:
        date = ''

    # 發文字號
    try:
        documentId = re.findall(r'發文字號[^\w\s](.*?)[^\w\s]', results) # 發文字號
        documentId = documentId[0]
    except IndexError:
        try:
            documentId_index = results.find('文字號') # 找出發文字號
            documentId = results_lst[results[:documentId_index].count('|')] # 發文字號
            documentId = re.split('[：]', documentId)[1] # 發文字號用冒號切開
        except:
            documentId = ''
    except:
        documentId = ''

    # 主旨
    try:
        subject = re.findall(r'主旨[^\w\s](.*?)[^\w\s]說明[^\w\s]', results_txt) # 主旨
        subject = subject[0]
    except IndexError:
        try:
            subject_index = results.find('主旨') # 找出主旨
            description_idnex = results.find('|說明') # 找出說明
            subject = ''.join(results_lst[results[:subject_index].count('|'):results[:description_idnex].count('|') + 1])
        except:
            subject = ''
    except:
        subject = ''

    # 義務人 / 債務人
    try:
        debtor = re.findall(r'[發受債義存][^權耀][人]([\w\s]{1,10})[（( ]', results_txt) # 找出 發票人　債務人　義務人　受刑人
        debtor = debtor[0]
    except IndexError:
        try:
            debtor = re.findall(r'[發受債義存][^權耀][人]([\w\s]{3})', results_txt) # 找出 發票人　債務人　義務人　受刑人
            debtor = debtor[0]
        except:
            debtor = ''
    except:
        debtor = ''

    # 帳號
    try:
        account = re.findall(r'[^\d]([0][0-9]{11})[^\d]', results_txt) # 找出帳號
        account = account[0]
    except:
        account = ''

    # 身分證統一編號
    try:
        idNumber = re.findall(r'[a-zA-Z][12][0-9]{8}', results_txt) # 找出身分證
        idNumber = idNumber[0]
    except:
        idNumber = ''

    # 營運事業編號
    try:
        businessNumber =  re.findall(r'[\D]([0-9]{8})號', results_txt) # 找出營運事業編號(公司統編)
        businessNumber = businessNumber[0]
    except:
        businessNumber = ''

    """將辨識結果寫入json"""

    rec_result.value.append({'name':'發文機關', 'text':authority})
    rec_result.value.append({'name':'發文日期', 'text':date})
    rec_result.value.append({'name':'發文字號', 'text':documentId})
    rec_result.value.append({'name':'主旨', 'text':subject})
    rec_result.value.append({'name':'義務人', 'text':debtor})
    rec_result.value.append({'name':'帳號', 'text':account})
    rec_result.value.append({'name':'身分證統一編號', 'text':idNumber})
    rec_result.value.append({'name':'營利事業編號', 'text':businessNumber})
    rec_result.status = '1' # 完成
    rec_result.msg = '辨識完成'
    
    #convert to JSON string
    jsonStr = json.dumps(rec_result.__dict__, ensure_ascii=False)
    return jsonStr

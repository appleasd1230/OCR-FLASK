# -*- coding:utf-8 -*-

"""辨識結果class"""
class RecResultModel(object):
    def __init__(self):
        self.status = '' # 結果 0:處理中 / 1:完成 / -1:異常
        self.msg = '' # 如果異常紀錄訊息
        self.result = [] # 文件類型

"""公文辨識結果class"""
class DepositoryDocModel(object):
    def __init__(self):
        self.documentType = '公文' # 文件類型
        self.documentName = '' # 檔案名稱
        self.status = '0' # 狀態 0:處理中 / 1:完成 / -1:異常
        self.msg = '' # 如果異常紀錄訊息
        self.value = [] # 欄位and值

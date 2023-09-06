import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

from config import TX_SECRET_ID, TX_SECRET_KEY



class Translator:
    def __init__(self, SECRET_ID, SECRET_KEY):
        self.cred = credential.Credential(SECRET_ID, SECRET_KEY)

        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
        httpProfile.reqTimeout = 2

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = tmt_client.TmtClient(
            self.cred, "ap-guangzhou", clientProfile)

    def translate(self, text, dest_lang, source_lang="auto"):
        try:

            req = models.TextTranslateRequest()
            params = {
                "SourceText": text,
                "Source": source_lang,
                "Target": dest_lang,
                "ProjectId": 0
            }
            req.from_json_string(json.dumps(params))

            resp = self.client.TextTranslate(req)
            return json.loads(resp.to_json_string())['TargetText']

        except TencentCloudSDKException as err:
            print(err)

    def batch_translate(self, text_list, dest_lang, source_lang="auto", max_chunk_size=6000):
        try:
            translated_texts = []
            chunk = []
            for text in text_list:
                if len(chunk) + len(text) <= max_chunk_size:
                    chunk.append(text)
                else:
                    translated_texts.extend(self.translate_chunk(chunk, dest_lang, source_lang))
                    chunk = []

            if chunk:
                translated_texts.extend(self.translate_chunk(chunk, dest_lang, source_lang))

            return translated_texts

        except TencentCloudSDKException as err:
            print(err)
            raise ValueError("Tencent Translate Failed")

    def translate_chunk(self, chunk, dest_lang, source_lang):
        req = models.TextTranslateBatchRequest()
        params = {
            "Source": source_lang,
            "Target": dest_lang,
            "ProjectId": 0,
            "SourceTextList": chunk
        }

        req.from_json_string(json.dumps(params))

        resp = self.client.TextTranslateBatch(req)
        return json.loads(resp.to_json_string())['TargetTextList']


if __name__ == "__main__":
    tr=Translator(TX_SECRET_ID, TX_SECRET_KEY)
    print(tr.translate("你好，世界","en"))
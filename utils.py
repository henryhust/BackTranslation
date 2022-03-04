import time
import json
import csv
import random
import logging
from tqdm import tqdm
from googletrans import Translator
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='../log/log.txt')
logger = logging.getLogger()


GOOGLE_TRANSLATOR = Translator()


def tencent_translate(content, src, tgt="zh"):
    """腾讯翻译引擎, 详细API接口：https://cloud.tencent.com/document/api/551/15619"""
    time.sleep(0.1)
    try:
        cred = credential.Credential("AKID5yby96qNfleJjZEeqlPp55oGRM0OXR4Q", "6vsYx6yavznJYXGjuoRnslRt51h7IDtK")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-shanghai", clientProfile)

        # if len(content) >= 200:
        #     content = content[:200]

        req = models.TextTranslateRequest()
        params = {
            "SourceText": content,
            "Source": src,
            "Target": tgt,
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        resp = client.TextTranslate(req)
        result = resp.to_json_string()
        result = eval(result)
        return result["TargetText"]

    except TencentCloudSDKException as err:
        print(err.message)
        print("翻譯結構報錯")
        return None


def google_translate(content, src, tgt="zh-CN", factor=1):
    """
    API:https://github.com/ssut/py-googletrans
    :param content:文本内容 or 文本列表
    :param tgt:目标语言
    :return:
    """
    time.sleep(random.randint(1, 3))

    translation = GOOGLE_TRANSLATOR.translate(src=src, dest=tgt, text=content, service_urls=["translate.google.com"])

    if content == translation.text:      # 等待时间，呈指数增长。
        print("翻译接口异常,程序会等待{}秒".format(str(factor * 20)))
        logger.info("翻译接口异常, 程序会等待{}秒".format(str(factor * 20)))

        time.sleep(1200 * factor)
        factor *= 2
        translation = google_translate(content, src, tgt="zh-CN", factor=factor)

    return translation.text


if __name__ == '__main__':

    with open("../data/kbs.csv", "r", encoding="utf8") as fr, open("../data/kbs_new4117-15000.csv", "w", encoding="utf8", newline="") as fw:
        csv_reader = csv.reader(fr)
        csv_writer = csv.writer(fw)

        for idx, line in tqdm(enumerate(list(csv_reader))):
            print(idx)
            if 0 < idx < 4117:
                continue

            if idx == 0:
                line.append("chinese_content")
                line.append("chinese_title")
                csv_writer.writerow(line)
                continue

            combine = line[4] + "&" + line[1]   # 避免两次调用，效率翻倍
            # combine = google_translate(combine, src="ko")
            combine = tencent_translate(combine, src="ko")
            print(combine)
            line.extend(combine.rsplit("&", 1)[::-1])
            csv_writer.writerow(line)

        print("finished")


# -*- coding: utf-8 -*-
"""
@File    : single.py
@Author  : AlanStar
@Contact : alan233@vip.qq.com
@License : MIT
Copyright (c) 2022-2023 AlanStar
"""
import os
import json
import requests


class DataScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }

    def saveImg(self, url, savePath, imgName):
        """
        下载并保存图片
        :param url: 图片 URL
        :param savePath: 存储路径, 默认给加好 "./data" , 即如传入参数为 "/nft/", 则会自动拼接为 "./data/nft/"
        :param imgName: 类似 "myPic.png"
        :return:
        """
        targetSavePath = "./data" + f"{savePath}" + f"{imgName}"
        # 如果文件夹不存在, 则创建
        if not os.path.exists("./data" + f"{savePath}"):
            os.makedirs("./data" + f"{savePath}")
        response = requests.get(url, headers=self.headers)
        with open(targetSavePath, "wb") as file:
            file.write(response.content)

    @staticmethod
    def saveData(jsonData, savePath, csvName):
        """
        json 数据处理器, 将返回的 json 数据写入 csv (只会处理单页)
        :param jsonData:
        :param savePath:
        :param csvName:
        :return:
        """
        targetSavePath = "./data" + savePath + csvName
        # 如果文件夹不存在, 则创建
        if not os.path.exists("./data" + f"{savePath}"):
            os.makedirs("./data" + f"{savePath}")
        if jsonData["code"] == 0:
            # 文件不存在的情况下, 初始化并执行写入
            if not os.path.exists(targetSavePath):
                with open(targetSavePath, "a") as file:
                    file.write("item_id,item_name,issuer_name\n")  # 藏品基本信息
                    file.write("{},{},{}\n".format(jsonData["data"]["item_id"], jsonData["data"]["item_name"],
                                                   jsonData["data"]["issuer_name"]))
                    # 标题
                    file.write(
                        "item_name,serial_number,token_id,mid,username,avatar,image,animation_url,nft_type,detail_jump,like_number,like_status,nft_id\n")
                    # 开始批量写入
                    for i in range(len(jsonData["data"]["nft_list"])):
                        file.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                            jsonData["data"]["nft_list"][i]["item_name"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["serial_number"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["token_id"],
                            jsonData["data"]["nft_list"][i]["mid"],
                            jsonData["data"]["nft_list"][i]["username"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["avatar"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["image"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["animation_url"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["nft_type"],
                            jsonData["data"]["nft_list"][i]["detail_jump"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["like_number"],
                            jsonData["data"]["nft_list"][i]["like_status"],
                            jsonData["data"]["nft_list"][i]["nft_id"].encode("utf-8").decode("utf-8")
                        ))
            # 文件存在的情况下, 执行追加写入, 不写表头
            else:
                with open(targetSavePath, "a") as file:
                    # 开始批量写入
                    for i in range(len(jsonData["data"]["nft_list"])):
                        file.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                            jsonData["data"]["nft_list"][i]["item_name"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["serial_number"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["token_id"],
                            jsonData["data"]["nft_list"][i]["mid"],
                            jsonData["data"]["nft_list"][i]["username"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["avatar"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["image"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["animation_url"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["nft_type"],
                            jsonData["data"]["nft_list"][i]["detail_jump"].encode("utf-8").decode("utf-8"),
                            jsonData["data"]["nft_list"][i]["like_number"],
                            jsonData["data"]["nft_list"][i]["like_status"],
                            jsonData["data"]["nft_list"][i]["nft_id"].encode("utf-8").decode("utf-8")
                        ))

    def simpleDataGetter(self, item_id: int) -> dict:
        """
        只是请求一页数据, 不会进行数据处理, 供进一步判断逻辑
        :param item_id:
        :return:
        """
        url = f"https://baselabs.bilibili.com/x/gallery/nft/collect/list?mid=0&pn=1&ps=1&item_id={item_id}"
        data = json.loads(requests.get(url, self.headers).text)
        return data

    def pageNumCalculator(self, item_id: int) -> int:
        """
        计算 NFT 发行量, 从而确定页数
        :param item_id:
        :return:
        """
        url = f"https://baselabs.bilibili.com/x/gallery/nft/collect/list?mid=0&pn=1&ps=1&item_id={item_id}"
        data = json.loads(requests.get(url, self.headers).text)
        totalMount = data["data"]["nft_list"][0]["serial_number"]
        # 找到 / , 切分字符串, 取后半部分
        index = totalMount.find("/")
        totalMount = totalMount[index + 1:]
        return int(totalMount)

    def core(self, start_item_id, end_item_id):
        """
        爬虫核心
        :param start_item_id: 起始 item_id
        :param end_item_id: 结束 item_id
        :return:
        """
        # 根据用户输入的遍历范围进行遍历
        for item_id in range(start_item_id, end_item_id + 1):
            # Light: 如果 item_id 有效, 则进行请求
            if self.simpleDataGetter(item_id)["code"] == 0:
                # 针对 item_id 进行请求 (遍历单页)
                for pageNum in range(1, int(self.pageNumCalculator(item_id) / 100) + 1):
                    response = requests.get(f"https://baselabs.bilibili.com/x/gallery/nft/collect/list?mid=0&pn={pageNum}&ps=100&item_id={item_id}")
                    nftData = json.loads(response.text)
                    # 保存数据
                    print(f"---------- {nftData['data']['item_name']} 第 {pageNum} 页----------")
                    # Light: 检查 csv 是否存在, 有则删除
                    if os.path.exists(f"./data/{item_id}/{item_id}.csv"):
                        os.remove(f"./data/{item_id}/{item_id}.csv")
                    self.saveData(nftData, f"/{item_id}/", f"{item_id}.csv")
                    print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} -> 第 {pageNum} 页 csv 数据已保存")
                    # 保存图片
                    for i in range(len(nftData["data"]["nft_list"])):
                        # print("nft_list 长度:", len(nftData["data"]["nft_list"]))
                        # 如果 image 不为空则下载
                        if nftData["data"]["nft_list"][i]["image"] != "":
                            if os.path.exists(f"./data/{item_id}/{int(nftData['data']['nft_list'][i]['token_id'])}.png"):
                                print("\033[93m[warning]\033[0m", f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} image 已存在, 跳过")
                            else:
                                self.saveImg(nftData["data"]["nft_list"][i]["image"], f"/{item_id}/", f"{int(nftData['data']['nft_list'][i]['token_id'])}.png")
                                print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} image 已保存")
                        # 如果 animation_url 不为空则下载
                        if nftData["data"]["nft_list"][i]["animation_url"] != "":
                            if os.path.exists(f"./data/{item_id}/{int(nftData['data']['nft_list'][i]['token_id'])}.mp4"):
                                print("\033[93m[warning]\033[0m", f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} animation 已存在, 跳过")
                            else:
                                self.saveImg(nftData["data"]["nft_list"][i]["animation_url"], f"/{item_id}/", f"{int(nftData['data']['nft_list'][i]['token_id'])}.mp4")
                                print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} animation 已保存")
            # Light: 否则跳过
            else:
                print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} 不存在, 跳过")
                pass


if __name__ == '__main__':
    start_id = int(input("请输入起始 item_id: "))
    end_id = int(input("请输入结束 item_id: "))
    nftSpider = DataScraper()
    nftSpider.core(start_id, end_id)

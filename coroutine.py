# -*- coding: utf-8 -*-
"""
@File    : single.py
@Author  : AlanStar
@Contact : alan233@vip.qq.com
@License : MIT
Copyright (c) 2022-2023 AlanStar
"""
import os
import csv
import json
import requests
import aiohttp
import aiologger
import logging
import asyncio


class DataScraper:
    def __init__(self):
        self.pageSize = 100  # 每页最大数量 -> 对应 API 中的 ps
        self.isSaveImg = False  # 是否保存图片
        self.logger = aiologger.Logger.with_default_handlers()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }

    async def saveImg(self, session, url, savePath, imgName):
        """
        下载并保存图片
        :param session: aiohttp 客户端会话对象
        :param url: 图片 URL
        :param savePath: 存储路径, 默认给加好 "./data" , 即如传入参数为 "/nft/", 则会自动拼接为 "./data/nft/"
        :param imgName: 类似 "myPic.png"
        :return:
        """
        if not self.isSaveImg:
            return
        targetSavePath = "./data" + f"{savePath}" + f"{imgName}"
        # 如果文件夹不存在, 则创建
        if not os.path.exists("./data" + f"{savePath}"):
            os.makedirs("./data" + f"{savePath}")
        async with session.get(url, headers=self.headers) as response:
            with open(targetSavePath, "wb") as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

    async def download_images(self, item_id, nftData):
        """
        异步下载图片
        :param item_id: 系列编号
        :param nftData: 系列数据
        :return:
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for i in range(len(nftData["data"]["nft_list"])):
                # 如果 image 不为空则下载
                if nftData["data"]["nft_list"][i]["image"] != "":
                    if os.path.exists(f"./data/{item_id}/{int(nftData['data']['nft_list'][i]['token_id'])}.png"):
                        print("\033[93m[warning]\033[0m",
                              f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} image 已存在, 跳过")
                    else:
                        url = nftData["data"]["nft_list"][i]["image"]
                        task = asyncio.ensure_future(self.saveImg(session, url, f"/{item_id}/",
                                                                  f"{int(nftData['data']['nft_list'][i]['token_id'])}.png"))
                        tasks.append(task)

                # 如果 animation_url 不为空则下载
                if nftData["data"]["nft_list"][i]["animation_url"] != "":
                    if os.path.exists(f"./data/{item_id}/{int(nftData['data']['nft_list'][i]['token_id'])}.mp4"):
                        print("\033[93m[warning]\033[0m",
                              f"NFT 系列编号: {item_id} -> #{int(nftData['data']['nft_list'][i]['token_id'])}/{self.pageNumCalculator(item_id)} animation 已存在, 跳过")
                    else:
                        url = nftData["data"]["nft_list"][i]["animation_url"]
                        task = asyncio.ensure_future(self.saveImg(session, url, f"/{item_id}/",
                                                                  f"{int(nftData['data']['nft_list'][i]['token_id'])}.mp4"))
                        tasks.append(task)

            await asyncio.gather(*tasks)

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
                with open(targetSavePath, "a", encoding="utf-16", newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["item_id", "item_name", "issuer_name"])  # 藏品基本信息
                    writer.writerow(
                        [jsonData["data"]["item_id"], jsonData["data"]["item_name"], jsonData["data"]["issuer_name"]])
                    writer.writerow(["item_name", "serial_number", "token_id", "mid", "username", "avatar", "image",
                                     "animation_url", "nft_type", "detail_jump", "like_number", "like_status",
                                     "nft_id"])  # 标题
                    for i in range(len(jsonData["data"]["nft_list"])):
                        writer.writerow([
                            jsonData["data"]["nft_list"][i]["item_name"],
                            jsonData["data"]["nft_list"][i]["serial_number"],
                            jsonData["data"]["nft_list"][i]["token_id"],
                            jsonData["data"]["nft_list"][i]["mid"],
                            jsonData["data"]["nft_list"][i]["username"],
                            jsonData["data"]["nft_list"][i]["avatar"],
                            jsonData["data"]["nft_list"][i]["image"],
                            jsonData["data"]["nft_list"][i]["animation_url"],
                            jsonData["data"]["nft_list"][i]["nft_type"],
                            jsonData["data"]["nft_list"][i]["detail_jump"],
                            jsonData["data"]["nft_list"][i]["like_number"],
                            jsonData["data"]["nft_list"][i]["like_status"],
                            jsonData["data"]["nft_list"][i]["nft_id"]
                        ])
            # 文件存在的情况下, 执行追加写入, 不写表头
            else:
                with open(targetSavePath, "a", encoding="utf-16", newline='') as file:
                    appendWriter = csv.writer(file)
                    for i in range(len(jsonData["data"]["nft_list"])):
                        appendWriter.writerow([
                            jsonData["data"]["nft_list"][i]["item_name"],
                            jsonData["data"]["nft_list"][i]["serial_number"],
                            jsonData["data"]["nft_list"][i]["token_id"],
                            jsonData["data"]["nft_list"][i]["mid"],
                            jsonData["data"]["nft_list"][i]["username"],
                            jsonData["data"]["nft_list"][i]["avatar"],
                            jsonData["data"]["nft_list"][i]["image"],
                            jsonData["data"]["nft_list"][i]["animation_url"],
                            jsonData["data"]["nft_list"][i]["nft_type"],
                            jsonData["data"]["nft_list"][i]["detail_jump"],
                            jsonData["data"]["nft_list"][i]["like_number"],
                            jsonData["data"]["nft_list"][i]["like_status"],
                            jsonData["data"]["nft_list"][i]["nft_id"]
                        ])

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

    async def core(self, start_item_id, end_item_id):
        """
        爬虫核心
        :param start_item_id: 起始 item_id
        :param end_item_id: 结束 item_id
        :return:
        """
        # 根据用户输入的遍历范围进行遍历
        async with aiohttp.ClientSession() as session:
            for item_id in range(start_item_id, end_item_id + 1):
                # Light: 检查 csv 是否存在, 有则删除
                if os.path.exists(f"./data/{item_id}/{item_id}.csv"):
                    os.remove(f"./data/{item_id}/{item_id}.csv")
                # Light: 如果 item_id 有效, 则进行请求
                if self.simpleDataGetter(item_id)["code"] == 0:
                    # 针对 item_id 进行请求 (遍历单页)
                    for pageNum in range(1, int(self.pageNumCalculator(item_id) / self.pageSize) + 1):
                        url = f"https://baselabs.bilibili.com/x/gallery/nft/collect/list?mid=0&pn={pageNum}&ps={self.pageSize}&item_id={item_id}"
                        try:
                            async with session.get(url, headers=self.headers) as response:
                                response_text = await response.text()
                                if response_text:
                                    try:
                                        nftData = json.loads(response_text)
                                        # Light: 调试
                                        # print(nftData)
                                    except json.decoder.JSONDecodeError as e:
                                        print("\033[91m[error]\033[0m", f"发生解析错误: {e}")
                                        continue
                                else:
                                    break
                        except aiohttp.client_exceptions.ClientConnectorError:
                            print("\033[91m[error]\033[0m", f"疑似触发服务器风控, 请稍后再试")
                            break
                        # 如果发生超出页数的问题
                        if nftData["code"] == 12003003:
                            print("\033[91m[error]\033[0m",
                                  f"在尝试遍历第 {pageNum} 页时发生超出页数错误, 可能为发行方保留部分 NFT, 程序结束")
                            print("\033[91m[error]\033[0m", f"第 {pageNum} 页错误信息如下: {nftData}")
                            break
                        # 保存数据
                        print(f"---------- {nftData['data']['item_name']} 第 {pageNum} 页----------")
                        self.saveData(nftData, f"/{item_id}/", f"{item_id}.csv")
                        print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} -> 第 {pageNum} 页 csv 数据已保存")
                        await self.download_images(item_id, nftData)
                # Light: 否则跳过
                else:
                    print("\033[92m[message]\033[0m", f"NFT 系列编号: {item_id} 不存在, 跳过")
                    pass


if __name__ == '__main__':
    start_id = int(input("请输入起始 item_id: "))
    end_id = int(input("请输入结束 item_id: "))
    nftSpider = DataScraper()
    asyncio.run(nftSpider.core(start_id, end_id))

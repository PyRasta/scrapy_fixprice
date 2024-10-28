import json
from datetime import datetime

import scrapy


def get_categories():
    with open('categories.txt', 'r') as file:
        categories = file.readlines()
    categories = list(map(lambda x: x.replace('\n', ''), categories))
    return categories


class CategoryParsingSpider(scrapy.Spider):
    name = "category_parsing"
    allowed_domains = ["fix-price.com"]
    url = "https://fix-price.com/catalog/"

    def start_requests(self):
        start_urls = get_categories()
        needed = "catalog"
        for start_url in start_urls:
            if needed in start_url:
                index_need = start_url.find(needed) + len(needed) + 1
                category_url = start_url[index_need:]
                url = f"https://api.fix-price.com/buyer/v1/product/in/{category_url}?page=1"
                body = {
                    "category": category_url,
                    "brand": [],
                    "price": [],
                    "isDividedPrice": False,
                    "isNew": False,
                    "isHit": False,
                    "isSpecialPrice": False
                }
                request = scrapy.Request(url=url, method="POST", callback=self.parse, body=json.dumps(body))
                request.meta['category_url'] = category_url
                yield request

    def parsing_data(self, i):
        product_url = self.url + i["url"]
        section = [i["category"]["title"]]
        if i["category"]["parentCategory"]:
            section.append(i["category"]["parentCategory"]["title"])
        price = float(i["price"])
        special_price = i["specialPrice"]
        if special_price:
            special_price = float(special_price["price"])
        else:
            special_price = price
        discount_percentage = round(((price - special_price) / price) * 100, 2)
        images = list(map(lambda image: image["src"], i["images"]))
        brand = i["brand"]
        if brand:
            brand = brand["title"]
        else:
            brand = None
        data = {
            "timestamp": int(datetime.utcnow().timestamp()),
            "RPC": i["sku"],
            "url": product_url,
            "title": i["title"],
            "marketing_tags": [],
            "brand": brand,
            "section": section,
            "price_data": {
                "current": special_price,
                "original": price,
                "sale_tag": f"Скидка {discount_percentage}%"
            },
            "stock": {
                "in_stock": i["inStock"] > 0,
                "count": i["inStock"]
            },
            "assets": {
                "main_image": images[0],
                "set_images": images,
                "view360": [],
                "video": []
            },
            "metadata": {
                "__description": "",
            },
            "variants": i["variantCount"],
        }
        return data

    def parse(self, response):
        response_json = json.loads(response.text)
        for i in response_json:
            data = self.parsing_data(i)
            url = f"https://api.fix-price.com/buyer/v1/product/{i['url']}"
            request = response.follow(url, callback=self.parse_detail_product)
            request.meta['data'] = data
            yield request
        if response_json:
            category_url = response.meta['category_url']
            page = int(response.url[-1]) + 1
            body = {
                "category": response.meta['category_url'],
                "brand": [],
                "price": [],
                "isDividedPrice": False,
                "isNew": False,
                "isHit": False,
                "isSpecialPrice": False
            }
            url = f"{response.url[:-1]}{page}"
            request = scrapy.Request(url=url, method="POST", callback=self.parse, body=json.dumps(body))
            request.meta['category_url'] = category_url
            yield request

    def parse_detail_product(self, response):
        r_json = json.loads(response.text)
        data = response.meta['data']
        description = r_json['description']
        data['metadata']['__description'] = description
        for i in r_json['properties']:
            data['metadata'][i['title']] = i['value']
        for i in r_json['variants']:
            if data['RPC'] == i['barcode']:
                data['metadata']['Ширина, мм.'] = str(i['width'])
                data['metadata']['Высота, мм.'] = str(i['height'])
                data['metadata']['Длина, мм.'] = str(i['length'])
                data['metadata']['Вес, гр.'] = str(i['weight'])
                data['metadata']['Код товара'] = str(i['barcode'])
                break
        yield data

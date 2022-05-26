from math import nan
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import glob
import itertools
import sys
import json
from multiprocessing import Pool
import time
import random
import pandas as pd
import traceback
import os
import io
import hashlib
from random import choice
import math
import sys
import asyncio

asset_path = './components/'
asset_layer =['background','body', 'hat', 'cloth', 'earring', 'eyewear', 'nacklace',  'drink', 'props'] 
images_path = './images/'
jsons_path = './jsons/'
font_path_ = './kenvector_future.ttf'

name = 'Sample'
description = 'Sample' 
static_path = '/IMG_ROOT/'

width = 2000
height = 2000

#配件概率
def _Choices(count):
    choices = {
        'background':count, 
        'body': count, 
        'cloth': count, 
        'nacklace': int(count / 3), 
        'hat': count, 
        'eyewear': int(count / 3), 
        'earring': int(count / 3), 
        'mouth': int(count / 10), 
        'drink': int(count/ 3),
        'props': int(count/ 5)
    }
    return choices
    
# 取中间
def _getBetween(str, left, right):
    try:
        return str.split(left)[1].split(right)[0]
    except:
        return None

# 获取layer
def _getLayers():
    Path(asset_path).mkdir(parents=True, exist_ok=True)
    for l in asset_layer:
        Path(asset_path+l).mkdir(parents=True, exist_ok=True)
    return asset_layer
    
# 获取所有配件路径
def _getAllPath():
    all = {}
    total_count = 0
    kind = 1
    for l in layers:
        file_path = asset_path + l
        # \\ -> /
        s = glob.glob(file_path + '/*.png')
        for _ in range(len(s)):
            s[_] = s[_].replace('\\', '/')
        # print('file_paths:',s)
        all[l] = s
        # 确认layer里配件数
        print('layers:', l, 'len:', len(all[l]))
        total_count = total_count + len(all[l])
        kind *= len(all[l])
    print('total count:', total_count)
    print('total kind:', kind)
    print('--------------------------------------')
    return all


layers = _getLayers()
all_paths = _getAllPath()





#example
def build_one():

    #
    background = './components/background/Chartreuse_120.png'
    body = './components/body/2-rose/10{<Fur>Natural&<Eye>Brown&<Face>Happy Rose}.png'
    hat = './components/hat/curls.png'
    cloth = './components/cloth/hawaii_340.png'
    earring = './components/earring/gold.png'
    eyewear = './components/eyewear/yellow.png'
    nacklace = './components/nacklace/bitcoin.png'
    drink = './components/drink/martini.png'
    props = './components/props/roninbird.png'

    arr =  [background,body, hat, cloth, earring, eyewear, nacklace,  drink, props] 
    generateImage(arr,1)

    
# 生成csv
def generateCSV(count):

    print('build count:', count)

    # 配件概率
    prop_limit = {}
    choices = _Choices(count)

    for l in layers:
        n = choices.get(l, count)
        prop_limit.update({l: n})
    #print('set count:', prop_limit)

    data = {'id': range(count)}
    df = pd.DataFrame(data)
    for l in layers:

        #print('get', prop_limit[l], all_paths[l])
        layer_list = []
        for i in range(prop_limit[l]):
           # print(choice(all_paths[l]))
            layer_list.append(choice(all_paths[l]))
        #print('xxx', len(layer_list))
        if count - prop_limit[l] > 0:
            null_list = [''] * (count - prop_limit[l])
            print('get null list:', len(null_list))
            layer_list = layer_list + null_list
        random.shuffle(layer_list)
        print('get layer lenth:', l, len(layer_list))
        df[l] = layer_list

    print('--------------------------------------')
    df = checkCSV(df, 0)

    df.to_csv('generate.csv', index=None)

# 检查重复项
def checkCSV(df, time):
    df = df.drop(columns=['id'])
    # 标识重复项
    count = df[df.duplicated(keep='first')].count()[0]
    if count <= 0:
        df.insert(0, 'id', range(1, df.count()[0]+1))
        print("rebuild times:", time)
        return df
    # 需要多少项
    need = df.count()[0]
    # 删除重复项
    df1 = df.drop_duplicates(keep='first')
    now = df1.count()[0]

    print('rebuild count:', count)
    print('rebuild %d ~ %d' % (now, need))
    print('rebuilding……')
    # 配件概率
    prop_limit = {}
    choices = _Choices(count)
    
    for l in layers:
        n = choices.get(l, count)
        prop_limit.update({l: n})
    

    data = {'id': range(now, need)}
    df2 = pd.DataFrame(data)

    for l in layers:


        layer_list = []
        for i in range(prop_limit[l]):
            layer_list.append(choice(all_paths[l]))
        if count - prop_limit[l] > 0:
            null_list = [''] * (count - prop_limit[l])
            layer_list = layer_list + null_list
        random.shuffle(layer_list)
        df2[l] = layer_list

    print('--------------------------------------')
    frames = [df1, df2]
    df = pd.concat(frames)

    time += 1
    df = checkCSV(df, time)
    df = df.drop(columns=['id'])
    df.insert(0, 'id', range(1, df.count()[0]+1))
    return df

# 读取csv文件生成图像
def genrateFromCSV():
    save = True
    word = ''
    df = pd.read_csv('generate.csv')
    df = df.fillna('')
    df_list = df.values.tolist()
    n = len(df_list)
    md5_list = []
    for i in df_list:
        i = [x for x in i if x != '']
        no = i[0]
        # print(i,len(i))
        i.pop(0)

        hash = hashlib.md5(''.join(i).encode())
        name_ = hash.hexdigest()
        generateImage(i, save, word)
        md5_list.append(name_)
        print('generate:', no, name_)
    df['md5'] = md5_list
    df.to_csv('generate_file.csv', index=None)


def generateImage(arr, save=False, word=''):
    #name = str("%06d" % int(arr[0]))
    hash = hashlib.md5(''.join(arr).encode())
    name_ = hash.hexdigest()
    properties = []
    data = {
        'name': name,
        'description': description,
    }

    toImage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    try:

        for i in range(len(arr)):

            # load attributes
            p_path = arr[i].replace(
                asset_path, '').replace('.png', '').split('/')
            traits_str = _getBetween(p_path[-1], "{", "}").split("&")
            # print('traits_str:', traits_str)
            traits = list(map(lambda x: (x.split("_")), traits_str))
            # print('traits:', traits)
            for t in traits:
                #print(t)
                prop = {'trait_type': t[0], 'value': t[1]}
                #print('prop', prop)
                properties.append(prop)

            # load image
            file_path = arr[i]
            # print(file_path)
            if os.path.exists(file_path):
                fromImage = Image.open(file_path).convert('RGBA')
                #fromImge = fromImge.resize(toImage.size)
                #fromImage.show()
                toImage = Image.alpha_composite(toImage, fromImage)

            else:
                print('file is wrong size or file_path no exist:', file_path)

        # add text
        if word != '':
            wimg = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            d = ImageDraw.Draw(wimg)
            fontSize = 200
            font = ImageFont.truetype(font_path_, fontSize)
            d.text((50, height - 250), word, fill=(255,
                                                   255, 255), font=font, align='center')

            toImage = toImage.rotate(90)
            toImage = Image.alpha_composite(toImage, wimg)
            toImage = toImage.rotate(-90)

        if save:
            # save image
            Path(images_path).mkdir(parents=True, exist_ok=True)
            toImage.save(images_path + name_+'.png')

            # static_path?
            data['image'] = static_path + name_ + '.png'
            data['attributes'] = properties

            # save json
            Path(jsons_path).mkdir(parents=True, exist_ok=True)
            with open(jsons_path + name_, 'w') as outfile:
                json.dump(data, outfile)

    except Exception as err:
        print('error:', arr, traceback.print_tb(err.__traceback__))


if __name__ == '__main__':
    generateCSV(10)
    genrateFromCSV()
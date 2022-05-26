from pywebio.input import input, FLOAT
from pywebio import start_server,pin
from pywebio.session import go_app
from pywebio.pin import put_select,pin_update
from pywebio.output import put_text,put_image,put_buttons,put_collapse,put_tabs,put_grid,use_scope,put_row
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import glob
import asyncio
import sys
import os
import shutil
import json
from sympy import content

k=['KK','Pet']
num=0
asset_path = './components/'
asset_layer = { 'KK': ['background','body', 'hat', 'cloth', 'earring', 'eyewear', 'nacklace', 'mouth', 'drink', 'props'],
                'Pet': [ 'background' ,  'tail' , 'body' ,  'eyes' ,    'line' ,'nacklace' , 'leg','earring', 'other' ],
                }
images_path = './images/'
jsons_path = './jsons/'

name = 'Sample'
description = 'Sample.' 
static_path = '/IMG_ROOT/'

width = 2000
height = 2000

img = open('./none.png', 'rb').read()  
#配件概率
def _Choices(count):
    choices = {
        'background':count, 
        'tail': count, 
        'body': count, 
        'eyes': count, 
        'nacklace': int(count / 2), 
        'line': int(count / 2),
        'leg': count,
        'earring': int(count / 5),
        'other': int(count / 10),
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
    for _ in k:
        Path(asset_path+_+'/').mkdir(parents=True, exist_ok=True)
        for l in asset_layer[_]:
            Path(asset_path+_+'/'+l).mkdir(parents=True, exist_ok=True)
    return asset_layer
    
# 获取所有配件路径
def _getAllPath():
    all = {}
    for _ in k:
        all[_]={}
        total_count = 0
        kind = 1
        
        for l in layers[_]:
            print(_)
            file_path = asset_path + _ + '/' + l
            
            # \\ -> /
            s = glob.glob(file_path + '/*.png')
           
            for __ in range(len(s)):
                s[__] = s[__].replace('\\', '/')
            # print('file_paths:',s)
            all[_][l] = s
            # 确认layer里配件数
            print('layers:', l, 'len:', len(all[_][l]))
            total_count = total_count + len(all[_][l])
            kind *= len(all[_][l])
        print('total count:', total_count)
        print('total kind:', kind)
        print('--------------------------------------')
    #print(all)
    return all


layers = _getLayers()
all_paths = _getAllPath()
components={}
imgs={}
for _ in k:
    components[_]={}
    imgs[_]={}
    for l in layers[_]:
        components[_][l]=''
        imgs[_][l]=[]
        for p in all_paths[_][l]:
            imgs[_][l].append(p)

#print(all_paths)
def _changePage(p):
    global num
    print(p)
    for _ in range(len(k)):
        if k[_] == p:
            num=_
            go_app('nie',False)
    
def index():
    put_buttons([dict(label=_,value=_) for _ in ['KK','Pet']],onclick=_changePage)

def nie():
    global img,num
    tabs=[]
    for l in layers[k[num]]:
        t={}
        t['title']=l
        t['content']=[]
        #[t['content'].append(put_image(open(_, 'rb').read(), width='128px').onclick(lambda:changeImage(_))) for _ in imgs[l]]
        t['content'].append(put_buttons([dict(label=_.replace(_.split('-')[0]+'-','').split('{')[0],value=_) for _ in imgs[k[num]][l]],onclick=changeImage))
        tabs.append(t)
    with use_scope('scope2'):
        put_image(img, width='400px')
        #put_grid([[put_image(img, width='400px'),put_text('test')],],cell_width='400px', cell_height='400px')
    put_tabs(tabs)
    put_buttons(['save','clean'],onclick=[_save,_clean])


def changeImage(text):
    global components,img,num
    components[k[num]][text.split('/')[-2]] = text if components[k[num]][text.split('/')[-2]] != text else './none.png'

    c = components[k[num]]
    
    toImage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for l in layers[k[num]]:
        if c[l]!='':
                print(c[l])
                fromImage = Image.open(c[l]).convert('RGBA')
                toImage = Image.alpha_composite(toImage, fromImage)
                Path(images_path).mkdir(parents=True, exist_ok=True)
                toImage.save('./result/result.png')
        img = open('./result/result.png', 'rb').read()  
    with use_scope('scope2', clear=True):
        put_image(img, width='400px')

def _save():
    global componets
    properties=[]
    data = {
        'name': name,
        'description': description,
    }
    print('save')
    arr=[]
    for l in layers[k[num]]:
        c = components[k[num]]
        if c[l]!='':
            arr.append(c[l])
    
    hash = hashlib.md5(''.join(arr).encode())
    name_ = hash.hexdigest()
        
    for i in range(len(arr)):
            p_path=arr[i].replace('.png', '').split('/')[-1]
            traits_str = _getBetween(p_path, "{", "}").split("&")
            traits = list(map(lambda x: (x.split("_")), traits_str))
            for t in traits:
                if t[0]!='Special':
                    prop = {'trait_type': t[0], 'value': t[1]}
                    properties.append(prop)
    data['image'] = static_path + name_ + '.png'
    data['attributes'] = properties
    #print(properties)
    Path(images_path +k[num] +'/').mkdir(parents=True, exist_ok=True)
    shutil.copy('./result/result.png',images_path +k[num] +'/'+name_+'.png')
    #toImage.save(images_path + name_+'.png')
    Path(jsons_path +k[num] +'/').mkdir(parents=True, exist_ok=True)
    with open(jsons_path +k[num] +'/'+name_, 'w') as outfile:
        json.dump(data, outfile)
        
def _clean():
    global componets,num
    for l in layers[k[num]]:
        components[l]=''
    img = open('./none.png', 'rb').read()  
    with use_scope('scope2', clear=True):
        put_grid([[put_image(img, width='400px'),put_text('test')],],cell_width='400px', cell_height='400px')


if __name__ == '__main__':

    if sys.platform == 'win32': 
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start_server([index,nie], port=8091)#, host='0.0.0.0',debug=True)


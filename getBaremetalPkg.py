#!/usr/bin/env python    
# coding:utf-8
"""
 ベアメタルのインストール・パッケージのリストを表示します。

 環境変数を事前にセットしてください。
   export SOFTLAYER_API_KEY=<API KEYをセット>
   export SOFTLAYER_USERNAME=<USER NAMEをセット>
   環境変数は、IBM Cloud Infrastructure （旧SoftLayer カスタマーポータル）
   のメニューバーから Accout -> Users -> API KEY で参照できます。
"""
 
import os
import pprint
import SoftLayer 

client = SoftLayer.Client()

mask = 'id, name, description, type.keyName, items.id, items.description, items.categories.categoryCode'
pkgs = client['Product_Package'].getAllObjects(mask=mask)

for p in pkgs:
    for i in p['items']:
        for c in i['categories']:
            if c['categoryCode'] == 'server':
                if not 'server' in p:  p['server'] = []
                p['server'].append(i['description'])
    del p['items']
pprint.pprint(pkgs)

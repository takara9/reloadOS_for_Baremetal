#!/usr/bin/env python    
# coding:utf-8
"""
 ベアメタルにインストールできるOSイメージをリストします。

 location と pkgId を自身の環境に合わせて変更してください。

 location はデータセンターを表す記号です。 
   東京DC tok02

 pkgIdは、ベアメタルのパッケージの番号です。
   getBaremetalPkg.pyでリストできます。

 環境変数を事前にセットしてください。
   export SOFTLAYER_API_KEY=<API KEYをセット>
   export SOFTLAYER_USERNAME=<USER NAMEをセット>
   環境変数は、IBM Cloud Infrastructure （旧SoftLayer カスタマーポータル）
   のメニューバーから Accout -> Users -> API KEY で参照できます。
"""
import SoftLayer
import getOrderItemsDict as ItemsDict

client = SoftLayer.Client()
location = 'tok02'
pkgId = 551

items = ItemsDict.getOrderItemsDict(client, pkgId, location=location)
item = items['os']['items']
for key in item:

    # Ubuntu のみを選択表示
    #if key.startswith("OS_U"):
    print key,",",item[key]['description'],",",item[key]['priceId']

#!/usr/bin/env python    
# coding:utf-8
"""
 ベアメタルサーバーにインストールされたOSのスペックを表示する 

 serverId を自身のベアメタルのIDに置き換えて利用ください。
   slcli server list でIDを表示することができます。

 環境変数を事前にセットしてください。
   export SOFTLAYER_API_KEY=<API KEYをセット>
   export SOFTLAYER_USERNAME=<USER NAMEをセット>
   環境変数は、IBM Cloud Infrastructure （旧SoftLayer カスタマーポータル）
   のメニューバーから Accout -> Users -> API KEY で参照できます。
"""

import SoftLayer
from pprint import pprint as pp

class installedOSonBaremetal():

    def __init__(self):
        self.client = SoftLayer.Client()

    def main(self):
        serverId = 866447
        output = self.client['Hardware_Server'].getOperatingSystem(id=serverId)
        print "RESULT\n"
        pp(output)

if __name__ == "__main__":
    main = installedOSonBaremetal()
    main.main()

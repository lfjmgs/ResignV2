# Android v2签名写渠道

**用于apk加固后重新进行v2签名并写渠道**
使用多渠道打包工具[walle](https://github.com/Meituan-Dianping/walle)打完渠道包，上传360市场加固之后需要重新签名并写渠道号

## 条件
Python 2.7+

## 运行
请先在settings.py配置相关变量
python resignv2.py *apk_path* *channels* 
示例：  
python resignv2.py xxx.apk 360  
python resignv2.py xxx.apk 360,yingyongbao  
python resignv2.py xxx.apk // 配置文件指定渠道文件
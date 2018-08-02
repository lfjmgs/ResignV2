#!/usr/bin/env python
# coding=utf-8

import subprocess
import json
import sys
import os
import locale
import settings

"""
apk加固后重新进行v2签名并写渠道
"""

# 读取配置
keystore_file = settings.keystore_file
keystore_pass = settings.keystore_pass
channels_file = settings.channels_file
sdk_dir = settings.sdk_dir


def execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.read().decode(locale.getpreferredencoding()).strip()
    ret = p.wait()
    if ret != 0:
        print(out)
    return (ret, out)


def mkdir(path):
    path = path.strip().rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)


def startfile(filename):
    try:
        os.startfile(filename)
    except:
        try:
            subprocess.Popen(['xdg-open', filename])
        except:
            print('文件生成在output目录下')


if len(sys.argv) < 2:
    print('缺少参数：第一个参数为apk文件路径，必选；第二个参数为渠道号，可选，不指定的话请在配置文件settings.py中配置')
    sys.exit(0)

# 切换到脚本所在目录
script_dir = os.path.split(os.path.realpath(__file__))[0]
print('script_dir:', script_dir)
os.chdir(script_dir)

# 已加固apk路径(命令行第一个参数)
apk_path = sys.argv[1]
apk_name = os.path.split(apk_path)[1]  # apk文件名
print('apk_name:', apk_name)

# 渠道号(命令行第二个参数，可指定多个渠道，以逗号分隔)
channels = sys.argv[2] if len(sys.argv) >= 3 else ''
if not channels and not channels_file and not os.path.exists(channels_file):
    print('没有提供渠道号并且没有配置渠道文件路径（或渠道文件不存在）')
    sys.exit(0)

if not sdk_dir:
    # 从ANDROID_HOME环境变量读取SDK目录
    sdk_dir = os.getenv('ANDROID_HOME', '')

if sdk_dir:
    tools_dir = os.path.join(sdk_dir, 'build-tools')
else:
    print('sdk_dir未配置且ANDROID_HOME环境变量不存在')
    sys.exit(0)

for d in os.listdir(tools_dir):
    level = d.split('.')[0]
    if level.isdigit() and int(level) >= 25:
        tools_dir = os.path.join(tools_dir, d)
        break
else:
    print('v2签名需要build-tools 25+版')
    sys.exit(0)
print('tools_dir:', tools_dir)

output_dir = os.path.realpath('output')  # 输出目录
print('output_dir:', output_dir)
mkdir(output_dir)  # 创建输出目录

# 对齐
apk_tmp = os.path.join(output_dir, apk_name)
print('apk_tmp:', apk_tmp)

if os.path.exists(apk_tmp):
    os.remove(apk_tmp)

cmd_path = os.path.join(tools_dir, 'zipalign')
cmd = '{cmd_path} -v 4 {apk_path} {apk_tmp}'
ret, out = execute(cmd.format(**vars()))
print('align:', ret)

if ret == 0 and out.endswith('Verification succesful'):
    # v2签名
    cmd_path = os.path.join(tools_dir, 'lib', 'apksigner.jar')
    cmd = 'java -jar {cmd_path} sign --ks {keystore_file} --ks-pass pass:{keystore_pass} {apk_tmp}'
    ret, out = execute(cmd.format(**vars()))
    print('sign:', ret)
    # 检查v2签名
    cmd = 'java -jar CheckAndroidV2Signature.jar {apk_tmp}'
    ret, out = execute(cmd.format(**vars()))
    print('check-sign:', ret)
    isV2OK = json.loads(out)['isV2OK']
    print('isV2OK:', isV2OK)

    if ret == 0 and isV2OK:
        # 写入渠道号
        if channels:
            cmd = 'java -jar walle-cli-all.jar batch -c {channels} {apk_tmp} {output_dir}'
        else:
            cmd = 'java -jar walle-cli-all.jar batch -f {channels_file} {apk_tmp} {output_dir}'
        ret, out = execute(cmd.format(**vars()))
        print('write-channel:', ret)
        # 删除中间生成文件
        os.remove(apk_tmp)
        if ret == 0:
            print('v2签名并写渠道号成功！')
            startfile(output_dir)

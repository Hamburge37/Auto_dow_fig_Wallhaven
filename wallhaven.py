'''
	作者: 子非鱼
	时间: 2020.4.17
'''
import requests
import os
import random
import re
from bs4 import BeautifulSoup


def get_html(url):
	'''
		本函数获取目标链接页面
		参数 : 
			 url : 目标链接 
			 encoding : 文本编码,默认 utf-8
	'''
	try :
		kvs = [
		'''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36''',
		'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36''',
		'''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36''',
		'''Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'''
		] # 浏览器标识
		user_agent = random.choice(kvs) # 每次随机选一个
		headers = {"User-Agent" : user_agent}
		r = requests.get(url,headers = headers)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		r = r.text
		return r
	except :
		return ''

def parser_html(url_html,info_list):
	'''
		解析 html 页面,获取每张图片的唯一标识
		参数 :
			url_html : 要解析的页面
			info list : 存放标识的列表
	'''
	soup = BeautifulSoup(url_html,"html.parser")
	for children in soup.find("section").ul.children :
		info_list.append(children.find("figure").get("data-wallpaper-id"))  # 获取图片关键字

def down_image(info,keyword):
	'''
		根据标识下载图片
		参数 :
			info : 图片的标识
			keyword : 输入的图片关键字
	'''
	kv = {'user-agent':'Mozilla/5.0'}
	info_1 = info[0:2]
	root = 'D://{}//'.format(keyword) # 图片下载的文件夹
	if not os.path.exists(root) :
		os.mkdir(root) # 没有的话创建
	try :
		url = "https://w.wallhaven.cc/full/"+info_1+"/wallhaven-"+info+".jpg"
		path = root + '{}.jpg'.format(info) # 命名并添加在路径
		if not os.path.exists(path) :
			# 没有的话下载
			r = requests.get(url,headers = kv)
			r.raise_for_status()
			with open(path,'wb') as f :
				f.write(r.content)
				f.close
	except :
		url = "https://w.wallhaven.cc/full/"+info_1+"/wallhaven-"+info+".png"
		path = root + '{}.png'.format(info) # 命名并添加在路径
		if not os.path.exists(path) :
			# 没有的话下载
			r = requests.get(url,headers = kv)
			with open(path,'wb') as f :
				f.write(r.content)
				f.close

def	image_num(soup) :
	'''
		根据网页信息提取图片总数量
		参数：
			soup: html网页
	'''
	try :
		#num = re.findall(r"\d+",soup.find("h1").get_text())[0]  # 正则表达式提取图片总页数
		complex_num = re.findall(r"\d+",soup.find("h1").get_text()) 
		if len(complex_num) == 1  :
			# 如果匹配到逗号分隔的数字，则将其合并为一个数字
			num = int(complex_num[0])
		else:
			# 如果没有逗号，则直接提取数字
			num = int(complex_num[0]+complex_num[1])
	except Exception as e:
		print(f"发生异常: {type(e).__name__} - {e}")
		input("\n发生异常,请检查网络，任意键结束:")
	return num
	
def get_image_link(num_page,keyword) :
	info_list = []
	for page in range(num_page) :   # 遍历全部页码
		url = "https://wallhaven.cc/search?q="+keyword+"&page={}".format(page+1)
		url_html = get_html(url)
		try :
			parser_html(url_html,info_list)
		except Exception as e:
			print(f"发生异常: {type(e).__name__} - {e}")
			continue
	return info_list

def prograss(num,i,len_info_list):
	num_1 = int((i / int(num))*35)
	a = ">" * num_1
	b = "." * (35-num_1)               # 进度条
	print("\r[{}{}]{:3}%".format(a,b,'%.2f'%((i/int(len_info_list))*100)),end="")
	return i + 1

def main():
	# 获取搜索图片的关键字
	keyword = input("请输入要下载图片的主题名字(英文) : ")
	url = "https://wallhaven.cc/search?q="+keyword
	url_html = get_html(url)   # 获取目标链接的页面信息
	soup = BeautifulSoup(url_html,"html.parser")    # 解析页面


	num = image_num(soup)
	if num == '0' :   # 图片总数为 0,给出提示，程序结束
		print("\n没有此关键词的图片 :")
		input("\n任意键结束 :")
		return
	

	flage = input("\n共有{}张,输入 0 取消,其他任意键下载 :  ".format(num))  # 提示总图片数,是否确认下载
	if flage == '0' :
		print("\n下载已取消")
		return
	else :
		print("\n正在获取照片信息 : ")
	print("\n")
	num_page = (int(num) // 24) + 1   # 获取总页数


	info_list = get_image_link(num_page,keyword)

	print("\n正在下载 : ")
	try :
		i = 0
		for info in info_list :
			down_image(info,keyword)
			i = prograss(num,i,len(info_list))
	except Exception as e:
		print(f"发生异常: {type(e).__name__} - {e}")
		input("\n发生异常,请检查网络，任意键结束:")
	input("\n\n图片保存至  D:/{}\n\n任意键结束 :".format(keyword)).format(keyword)

if __name__ == '__main__':
    # Put that needs to run here
	main()

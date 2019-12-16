# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 14:04:35 2019

@author: Jie Ren
"""

import re
import os




def read_diff_file(diff_file_name):
    diff_file = diff_file_name + ".diff"
    path_function_list = []
    path_function_element = ["path", "class_function_name"]
    function_pattern_cpp = re.compile(r'^\s*([a-zA-Z\_][a-zA-Z0-9\_\<\>\:]*\s+)?([a-zA-Z\_][a-zA-Z0-9\_]*)\:\:(\~?[a-zA-Z\_][a-zA-Z0-9\_]*)\s*\([^\)]*[\)\:]{1,2}$')
    function_pattern_one_cpp = re.compile(r'([a-zA-Z\_][a-zA-Z0-9\_\<\>\:]*\s+)?([a-zA-Z\_][a-zA-Z0-9\_]*)\:\:(\~?[a-zA-Z\_][a-zA-Z0-9\_]*)\($')
    function_pattern_cpp_in_diff = re.compile(r'^[\+\-]\s*([a-zA-Z\_][a-zA-Z0-9\_\<\>\:]*\s+)?([a-zA-Z\_][a-zA-Z0-9\_]*)\:\:(\~?[a-zA-Z\_][a-zA-Z0-9\_]*)\s*\([^\)]*[\)\:]{1,2}$')
    function_pattern_head_in_diff= re.compile(r'^[\+\-]\s*([a-zA-Z0-9\_]*)?\s*[a-zA-Z\_][a-zA-Z0-9\_\<\>\:]*\s+(\~?[a-zA-Z\_][a-zA-Z0-9\_]+)\s*\<?[a-zA-Z0-9\_\,]*\>?\s*\([^\)]*[\)\:\;]{1,3}$')
    function_pattern_head_one_in_diff = re.compile(r'^[\+\-]\s*([a-zA-Z0-9\_]*)?\s*[a-zA-Z\_][a-zA-Z0-9\_\<\>\:]*\s+(\~?[a-zA-Z\_][a-zA-Z0-9\_]+)\s*\<?[a-zA-Z0-9\_\,]*\>?\s*\([^\)]*\)\s*\{[^\}]*\}$')
    define_pattern_in_diff = re.compile(r'^[\+\-]\s*\#define.*')
    comment_pattern_in_diff = re.compile(r'^[\+\-]\s*\/\/.*')
    include_pattern_in_diff = re.compile(r'^[\+\-]\s*#include.*')
    class_pattern_in_diff = re.compile(r'^[\+\-]\s*class\s*([a-zA-Z0-9\_]*)\s.*')
    class_pattern_in_head = re.compile(r'^\s*class\s*([a-zA-Z0-9\_]*)\s*.*')
    FileIsHead = False
    NameIsModified = False
    Rename = False
    with open(diff_file) as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0 or len(line) == 1 :
                continue
            if line[:3] == "+++":
                file_path = line[5:].replace("/","\\")
                path_function_element[0] = file_path
                class_name = " "
                if line[-1] == "h":
                    FileIsHead = True
                else:
                    FileIsHead = False
            if FileIsHead:
             #保留上文的class Name
             #改类名需要更新class Name +-区别对待
             #删除一个class，pass
             #添加一个class,更新class Name之后，添加所有的 function Name
             #rename 
             #暂时不考虑.h中的modify done
                if class_pattern_in_head.search(line):
                    class_name = class_pattern_in_head.search(line).group(1)
                if class_pattern_in_diff.search(line):
                    class_name = class_pattern_in_diff.search(line).group(1)
                elif function_pattern_head_in_diff.search(line):
                    if line[0] == '-': #head修改内容删除了一个函数 done
                       class_name_old = class_name
                       function_name_old = function_pattern_head_in_diff.search(line).group(2)
                       class_function_name_old = class_name_old + '.' + function_name_old
                       Rename = True
                       continue
                    else:#head修改内容添加了一个函数 done
                       function_name = function_pattern_head_in_diff.search(line).group(2)
                       class_function_name = class_name + '.' + function_name
                       path_function_element[1] = class_function_name
                       path_function_list.append(path_function_element[:])
                       if Rename:
                           line = class_function_name_old + ',' + class_function_name + '\n'
                           file = open("rename_reference.txt", "a+")
                           file.write(line)
                           file.close()
                elif function_pattern_head_one_in_diff.search(line):
                    if line[0] == '-':#head修改内容删除了一个函数
                       class_name_old = class_name
                       function_name_old = function_pattern_head_one_in_diff.search(line).group(2)
                       class_function_name_old = class_name_old + '.' + function_name_old
                       Rename = True
                       continue
                    else:#head修改内容添加了一个函数
                       function_name = function_pattern_head_one_in_diff.search(line).group(2)
                       class_function_name = class_name + '.' + function_name
                       path_function_element[1] = class_function_name
                       path_function_list.append(path_function_element[:])
                       if Rename:
                           line = class_function_name_old + ',' + class_function_name + '\n'
                           file = open("rename_reference.txt", "a+")
                           file.write(line)
                           file.close()
                else:
                    pattern = re.compile(r'^[\+\-]\s+([a-zA-Z0-9\_\~]+).*')
                    if pattern.search(line):
                        item = pattern.search(line).group(1)
                        if(item == class_name or item[1:] == class_name):
                            function_name = item
                            class_function_name = class_name + '.' + function_name
                            path_function_element[1] = class_function_name
                            path_function_list.append(path_function_element[:])
            else:
               #如搜到上文中的类名，保留
               #如搜到上文中的函数名，保留
               #如搜到+ 注释，宏定义，include，pass
               #如搜到- 注释，宏定义，include，pass
               #如搜到+- 函数体修改，用上文的类名+函数名
               #如搜到+ 一个或多个函数
               #rename
               #如搜到- 一个或多个函数
               if function_pattern_cpp.search(line):#找出cpp修改内容上文中的类名+函数名  done
                   class_name = function_pattern_cpp.search(line).group(2)
                   function_name = function_pattern_cpp.search(line).group(3)
                   class_function_name = class_name + '.' + function_name
                   NameIsModified = True
                   path_function_element[1] = class_function_name
               if function_pattern_one_cpp.search(line):#找出cpp修改内容上文中的类名+函数名  done
                   class_name = function_pattern_one_cpp.search(line).group(2)
                   function_name = function_pattern_one_cpp.search(line).group(3)
                   class_function_name = class_name + '.' + function_name
                   NameIsModified = True
                   path_function_element[1] = class_function_name
               if define_pattern_in_diff.search(line) or\
                   comment_pattern_in_diff.search(line) or\
                   include_pattern_in_diff.search(line):#过滤cpp中注释，宏定义，头文件等改动 done
                   continue
               elif function_pattern_cpp_in_diff.search(line):
                   if line[0] == '+':#cpp修改内容添加了一个函数 done 
                       class_name = function_pattern_cpp_in_diff.search(line).group(2)
                       function_name = function_pattern_cpp_in_diff.search(line).group(3)
                       class_function_name = class_name + '.' + function_name
                       path_function_element[1] = class_function_name
                       path_function_list.append(path_function_element[:])
                       if Rename:
                           line = class_function_name_old + ',' + class_function_name + '\n'
                           file = open("rename_reference.txt", "a+")
                           file.write(line)
                           file.close()
                       NameIsModified = False
                   else:#cpp修改内容删除了一个函数 done
                       class_name_old = function_pattern_cpp_in_diff.search(line).group(2)
                       function_name_old = function_pattern_cpp_in_diff.search(line).group(3)
                       class_function_name_old = class_name_old + '.' + function_name_old
                       Rename = True
                       NameIsModified = False
                       continue
               elif NameIsModified and (line[0] == '+' or line[0] == '-') and \
                         line[1] == ' ':#cpp中修改了函数体的内容 done
                   path_function_element[1] = class_function_name
                   path_function_list.append(path_function_element[:])
                   NameIsModified = False
        Rename = False
    f = open("Func_changed.txt",'a+')
    for item in path_function_list:
        line = item[0] + ',' + item[1] + "()" + '\n'
        f.write(line)
    f.close()              

         
def creat_git_diff(driver_path, commit_sha_1, commit_sha_2):#sha_1是sha_2的下一次commit
    output_file = "commit.diff"
    file_path = os.path.join(os.getcwd(), output_file)
    cd_cmd = "cd " + driver_path
    if commit_sha_1:
        git_cmd = "&& git diff " + commit_sha_1 + " " +commit_sha_2 + " -U100 > " + file_path
    else:
        git_cmd = "&& git diff HEAD~1 HEAD -U100 > " + file_path
    cmd = cd_cmd + git_cmd
    os.system(cmd)

def test(commit_before = '', commit_after = '',input_driver_path = r"C:\Users\jieren1\gfx\gfx-driver"):
    #input_driver_path = input("please input your driver path: ")
    if commit_before:
        with open("Func_changed.txt", 'w') as f:
            f.write(sha_1 + '\n')
    creat_git_diff(input_driver_path, commit_before, commit_after)
    diff_name = "commit"
    read_diff_file(diff_name)

if __name__ == '__main__':

    #sha_1 = "6ede08adeab5b17b2128a841e6bd3e11f2ec63f1"
    #sha_1 = "a8d33a86b8fe8225b8ef9a24aff1692d704314c1"
    #sha_1 = "599e42c8c06df04e651268dc3354961d62ab5864"
    #sha_1 =  "c1b362747e50f8bf94808b12c45d52f580fb75df" 
    #sha_1 =  "2de9e60897e2b3b50fd87abcfed04b412f974f79"
    #sha_1 = "9df4515e976f33b6e4c37a0eb69e91d0d510e278"
    #sha_1 = "3efc7bc1e858705b0b560dc6f32ac5fff07b678a"
    sha_1 = "9beebb12620d1243362c1ec2bac117b04d14bd49"
    sha_2 = sha_1 + "~1"
    test(sha_2, sha_1)

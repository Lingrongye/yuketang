# 注意，目前只能刷本学期的形策
import random
import time
import requests
import re
import json

# 以下的csrftoken和sessionid需要改成自己登录后的cookie中对应的字段！！！！而且脚本需在登录雨课堂状态下使用
# 登录上雨课堂，然后按右键->检查-->选Application-->找到雨课堂的cookies，寻找csrftoken、sessionid字段，并复制到下面两行即可
csrftoken = '' # 需改成自己的
sessionid = '' # 需改成自己的
university_id = "2627"  # 华南理工大学的id，不用改
url_root = "https://changjiang.yuketang.cn/"
learning_rate = 200  # 学习速率，好像再改大一点也没什么用

# 以下字段不用改，下面的代码也不用改动
cookies = {
    'login_type': 'WX',
    'csrftoken': csrftoken,
    'sessionid': sessionid,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'x-csrftoken': csrftoken,
'referer': 'https://changjiang.yuketang.cn/v2/web/studentLog/15025097',
    # 'uv-id': '2627',
# 'classroom-id': '15025097',
    'xtbz': 'ykt',
# 'university-id': '2627',
}


def one_video_watcher(video_name, video_id, classroomid, cid, user_id, skuid):
    user_id = str(user_id)
    cid = str(cid)
    skuid = str(skuid)
    video_id = str(video_id)
    classroomid = str(classroomid)
    url = url_root + "video-log/heartbeat/"
    get_url = url_root + "video-log/get_video_watch_progress/?cid=" + str(
        cid) + "&user_id=" + user_id + "&classroom_id=" + classroomid + "&video_type=video&vtype=rate&video_id=" + str(
        video_id) + "&snapshot=1"
    progress = requests.get(url=get_url, headers=headers,cookies=cookies)
    if_completed = '0'
    try:
        if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
    except:
        pass
    if if_completed == '1':
        print(video_name + "已经学习完毕，跳过")
        return 1
    else:
        print(video_name + "，尚未学习，现在开始自动学习")
        time.sleep(2)

    # 默认为0（即还没开始看）
    video_frame = 0
    val = 0
    # 获取实际值（观看时长和完成率）
    try:
        res_rate = json.loads(progress.text)
        tmp_rate = res_rate["data"][video_id]["rate"]
        if tmp_rate is None:
            return 0
        val = tmp_rate
        video_frame = res_rate["data"][video_id]["watch_length"]
    except Exception as e:
        print(e.__str__())
    print("当前进度：" + str(val))

    t = time.time()
    timstap = int(round(t * 1000))
    heart_data = []
    while float(val) <= 0.95:
        for i in range(3):
            heart_data.append(
                {
                    "i": 5,
                    "et": "loadeddata",
                    "p": "web",
                    "n": "ali-cdn.xuetangx.com",
                    "lob": "ykt",
                    "cp": video_frame,
                    "fp": 0,
                    "tp": 0,
                    "sp": 2,
                    "ts": str(timstap),
                    "u": int(user_id),
                    "uip": "",
                    "c": cid,
                    "v": int(video_id),
                    "skuid": skuid,
                    "classroomid": classroomid,
                    "cc": video_id,
                    "d": 4976.5,
                    "pg": video_id + "_" + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', 4)),
                    "sq": i+1,
                    "t": "video"
                }
            )
            video_frame += learning_rate

        data = {"heart_data": heart_data}
        r = requests.post(url=url, headers=headers, json=data,cookies=cookies)
        print(r.text)
        heart_data = []
        submit_url = 'https://changjiang.yuketang.cn/video-log/heartbeat/'
        try:
            delay_time = re.search(r'Expected available in(.+?)second.', r.text).group(1).strip()
            print("由于网络阻塞，万恶的雨课堂，要阻塞" + str(delay_time) + "秒")
            time.sleep(float(delay_time) + 0.5)
            print("恢复工作啦～～")
            r = requests.post(url=submit_url, headers=headers, data=data)
            print(r.status_code)
        except Exception as e:
            pass
        try:
            progress = requests.get(url=get_url, headers=headers,cookies=cookies)
            res_rate = json.loads(progress.text)
            tmp_rate = res_rate["data"][video_id]["rate"]
            if tmp_rate is None:
                return 0
            val = str(tmp_rate)
            print("学习进度为：\t" + str(float(val) * 100) + "%/100%")
            time.sleep(2)
        except Exception as e:
            print(e.__str__())
            pass
    print("视频" + video_id + " " + video_name + "学习完成！")
    return 1

def discuss(discuss_title, leaf_id,classroomid,skuid,topic_type):
    params1 = {
        'classroom_id':classroomid,
        'sku_id': skuid,
        'leaf_id': leaf_id,
        'topic_type': topic_type,
        'channel': 'xt',
    }
    # 获取讨论课题的id，以及用户id
    response = requests.get('https://changjiang.yuketang.cn/v/discussion/v2/unit/discussion/', params=params1,
                            cookies=cookies, headers=headers)
    discuss_user_info = json.loads(response.text)
    discuss_user_id = discuss_user_info['data']['user_id']
    discuss_id = discuss_user_info['data']['id']

    # 获取别人发送的讨论的内容
    discuss_url = "https://changjiang.yuketang.cn/v/discussion/v2/comment/list/"+str(discuss_id)+"/"
    params2 = {
        'offset': 0,
        'limit': 10,
        'web': 'web'
    }
    response = requests.get(discuss_url, params=params2, cookies=cookies, headers=headers)
    discuss_info = json.loads(response.text)
    discuss_content = discuss_info['data']['new_comment_list']['results'][0]['content']['text']

# 发表评论的参数
    json_data = {
        'to_user': int(discuss_user_id),
        'topic_id': int(discuss_id),
        'content': {
            'text': str(discuss_content),
            'upload_images': [],
            'accessory_list': [],
        },
    }
# 评论
    comment_response = json.loads(requests.post('https://changjiang.yuketang.cn/v/discussion/v2/comment/', cookies=cookies,
                             headers=headers,
                             json=json_data).text)
    if comment_response['success']:
        print(discuss_title,'的讨论任务已经完成')


if __name__ == "__main__":
    user_info_url = "https://changjiang.yuketang.cn/v2/api/web/userinfo"
    user_id = json.loads(requests.get(url=user_info_url,headers=headers,cookies=cookies).text)['data'][0]['user_id']
    time.sleep(random.randint(1,3))
    course_name = '2024春-形势与政策课'
    course_info = requests.get('https://changjiang.yuketang.cn/v2/api/web/courses/list?identity=2',headers=headers,cookies=cookies)
    time.sleep(random.randint(1, 3))
    # course_lists = json.loads(course_info.text)['data']['list']
    # with open ('course_list.json','w',encoding='utf-8') as f:
    #     f.write(json.dumps(course_lists))
    # print("课程列表如下：")
    # print("====================================")
    # print(course_lists)
    course_id = '2588039'
    classroom_id = '16978956'
    # for list in course_lists:
    #     print(list['course']['name'])
    #     if list['name'] == course_name:
    #         course_id = list['course']['id']
    #         classroom_id = list['classroom_id']
    #         break
    # if course_id == '':
    #     print("未找到该课程,请检查课程名称是否正确")
    #     exit(0)

    headers['classroom-id'] = str(classroom_id)
    video_info = json.loads(requests.get('https://changjiang.yuketang.cn/c27/online_courseware/xty/kls/pub_news/673117/',headers=headers,cookies=cookies).text)
    time.sleep(random.randint(1, 3))
    content_info_all = video_info['data']['content_info']

    print(content_info_all)
    sku_id = video_info['data']['s_id']
    all_video_info = []
    all_discuss_info = []
    for content_info in content_info_all:
        section_list = content_info['section_list']
        discuss_leaf_list = content_info['leaf_list']
        for discuss_leaf in discuss_leaf_list:
            all_discuss_info.append([discuss_leaf['title'],discuss_leaf['id'],discuss_leaf['leaf_type']])
        for list in section_list:
            leaf_list = list['leaf_list']
            for leaf in leaf_list:
                video_name = leaf['title']
                video_id = str(leaf['id'])
                all_video_info.append([video_name,video_id])
    for discuss_info in all_discuss_info:
        title = discuss_info[0]
        leaf = discuss_info[1]
        type = discuss_info[2]
        discuss(title,leaf,classroom_id,sku_id,type)

    for video_info in all_video_info:
        one_video_watcher(video_info[0],video_info[1],classroom_id,course_id,user_id,sku_id)





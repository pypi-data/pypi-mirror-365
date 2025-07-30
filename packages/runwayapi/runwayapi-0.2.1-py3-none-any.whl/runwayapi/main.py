import requests
from runwayapi.response import LoginResponse
from typing import Optional, Dict
import random
import time
import os
import traceback
import urllib3
from requests.exceptions import ConnectionError, RequestException
from urllib3.exceptions import ProtocolError
import hashlib
# 用户代理配置
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

# 内容类型映射
CONTENT_TYPE_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', 
    '.png': 'image/png',
    '.gif': 'image/gif'
}

# 分辨率类型
RESOLUTION_MAP = {
    '16:9': (1920, 1088),  # 16:9 标准宽屏
    '21:9': (2112, 912),   # 21:9 超宽屏
    '4:3': (1456, 1088),   # 4:3 标准屏
    '1:1': (1088, 1088),   # 1:1 正方形
    '3:4': (1088, 1456),   # 3:4 竖屏
    '9:16': (1088, 1920)   # 9:16 手机屏幕
}

GEN4_RESOLUTION_MAP = {
    '16:9': (1280, 720),
    '9:16': (720, 1280)
}

# 最大重试次数
MAX_RETRIES = 3
# 重试间隔(秒)
RETRY_INTERVAL = 5

# Runway账号登录
def login(username: str, password: str) -> str:
    """
    调用 Runway API 进行登录并获取 token
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        str: JWT token
        
    Raises:
        Exception: 当登录失败时抛出异常
    """
    print("RunwayAPI ----> 开始登录")
    url = "https://api.runwayml.com/v1/login"
    # 判断是否为邮箱
    if '@' in username:
        payload = {
            "email": username,
            "password": password,
            "machineId": None
        }
    else:
        payload = {
            "username": username,
            "password": password, 
            "machineId": None
        }

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.post(url, json=payload, headers=headers)  # 使用model_dump代替dict
        response_data = response.json()
        
        if response.status_code != 200:
            print(f"RunwayAPI ----> 登录失败，状态码: {response.status_code}")
            return None

        login_response = LoginResponse(**response_data)
        print("RunwayAPI ----> 登录成功")
        return login_response.token
    except requests.exceptions.RequestException as e:
        print(f"RunwayAPI ----> 登录请求异常: {e}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"RunwayAPI ----> 登录异常: {e}")
        print(traceback.format_exc())
        return None

# Runway 获取用户ID
def get_user_team_id(token: str) -> str:
    """
    获取Runway用户信息并返回状态码
    
    Args:
        token: JWT token
        
    Returns:
        int: 
            - 801: 账号已过期
            - 200: 账号正常
            
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("RunwayAPI ----> 获取用户ID")
    url = "https://api.runwayml.com/v1/profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            print("RunwayAPI ----> 获取用户ID失败，认证失败")
            return 401
        if response.status_code != 200:
            print(f"RunwayAPI ----> 获取用户ID失败，状态码: {response.status_code}")
            return None
        
        data = response.json()
        user_data = data["user"]
        
        # 检查账号是否过期
        print(f"RunwayAPI ----> 获取用户ID成功: {user_data['id']}")
        return user_data['id']
        
    except requests.exceptions.RequestException as e:
        print(f"RunwayAPI ----> 获取用户ID请求异常: {e}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"RunwayAPI ----> 获取用户ID异常: {e}")
        print(traceback.format_exc())
        return None
    
# 获取到用户任务数最小的SessionID
def get_min_session_id(token: str, team_id: str) -> str:
    """
    获取Runway会话列表并返回taskCount最小的会话ID
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: taskCount最小的会话ID
        
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("RunwayAPI ----> 获取任务数最小的会话ID")
    url = "https://api.runwayml.com/v2/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    params = {
        "asTeamId": team_id,
        "limit": 50,
        "sortBy": "sortTimestamp",
        "orderBy": "DESC"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            print("RunwayAPI ----> 获取会话列表失败，认证失败")
            return 401

        if response.status_code != 200:
            print(f"RunwayAPI ----> 获取会话列表失败，状态码: {response.status_code}")
            return None
            
        data = response.json()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("RunwayAPI ----> 没有找到会话")
            return None
            
        # 找到taskCount最小的会话
        min_session = min(sessions, key=lambda x: x.get("taskCount", 0))
        
        print(f"RunwayAPI ----> 获取到任务数最小的会话ID: {min_session['id']}")
        return min_session['id']
        
    except Exception as e:
        print(f"RunwayAPI ----> 获取会话列表异常: {e}")
        print(traceback.format_exc())
        return None

# 获取到用户最近的50个Session
def get_sessions(token: str, team_id: str) -> list:
    """
    获取Runway会话列表并返回taskCount最小的会话ID
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: taskCount最小的会话ID
        
    Raises:
        Exception: 当请求失败时抛出异常
    """
    print("RunwayAPI ----> 获取用户最近的50个会话")
    # 百分之10的几率创建Session
    if random.random() < 0.1:
        print("RunwayAPI ----> 随机创建新会话")
        create_session(token, team_id)

    url = "https://api.runwayml.com/v2/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    params = {
        "asTeamId": team_id,
        "limit": 50,
        "sortBy": "sortTimestamp",
        "orderBy": "DESC"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 401:
            print("RunwayAPI ----> 获取会话列表失败，认证失败")
            return 401

        if response.status_code != 200:
            print(f"RunwayAPI ----> 获取会话列表失败，状态码: {response.status_code}")
            return None
            
        data = response.json()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("RunwayAPI ----> 没有找到会话")
            return None
        
        print(f"RunwayAPI ----> 获取到 {len(sessions)} 个会话")
        return sessions
        
    except Exception as e:
        print(f"RunwayAPI ----> 获取会话列表异常: {e}")
        print(traceback.format_exc())
        return None

# 创建session，返回SessionID
def create_session(token: str, team_id: str) -> str:
    """
    创建新的Runway会话
    
    Args:
        token: JWT token
        team_id: 团队ID
        
    Returns:
        str: 会话ID
        
    Raises:
        Exception: 当创建会话失败时抛出异常
    """
    print("RunwayAPI ----> 创建新会话")
    url = "https://api.runwayml.com/v1/sessions"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    payload = {
        "asTeamId": team_id,
        "taskIds": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 401:
            print("RunwayAPI ----> 创建会话失败，认证失败")
            return 401

        if response.status_code != 200:
            print(f"RunwayAPI ----> 创建会话失败，状态码: {response.status_code}")
            return None
            
        data = response.json()
        session_data = data["session"]
        print(f"RunwayAPI ----> 创建会话成功，ID: {session_data['id']}")
        return session_data['id']
        
    except requests.exceptions.RequestException as e:
        print(f"RunwayAPI ----> 创建会话请求异常: {e}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"RunwayAPI ----> 创建会话异常: {e}")
        print(traceback.format_exc())
        return None

# 获取assetGroupID，如果获取不到，则创建assetGroup
def get_asset_group_id(token: str, session_id: str, team_id: int) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    print(f"RunwayAPI ----> 获取资源组ID，会话ID: {session_id}")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT
        }
        
        response = requests.get(
            f"https://api.runwayml.com/v1/sessions/{session_id}",
            headers=headers,
            params={"asTeamId": team_id}
        )

        if response.status_code == 401:
            print("RunwayAPI ----> 获取资源组ID失败，认证失败")
            return 401

        if response.status_code != 200:
            print(f"RunwayAPI ----> 获取资源组ID失败，状态码: {response.status_code}")
            return None
        
        data = response.json()        
        # 从session对象中获取assetGroupId
        asset_group_id = data.get('session', {}).get('assetGroupId')
        if asset_group_id:
            print(f"RunwayAPI ----> 获取到资源组ID: {asset_group_id}")
            return asset_group_id
        else:
            print("RunwayAPI ----> 未找到资源组ID，尝试创建")
            return get_asset_group(token, session_id, team_id)  
    except Exception as e:
        print(f"RunwayAPI ----> 获取资源组ID异常: {e}")
        print(traceback.format_exc())
        return None

# 获取assetGroupID，如果获取不到，则创建assetGroup
def get_asset_group(token: str, session_id: str, team_id: int) -> Optional[str]:
    """
    获取assetGroupId
    
    Args:
        session_id: 会话ID
        account: 账号信息
        
    Returns:
        str: 成功时返回assetGroupId，失败返回None
    """
    print(f"RunwayAPI ----> 创建资源组，会话ID: {session_id}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    response = requests.post(
        f"https://api.runwayml.com/v1/sessions/{session_id}/assetGroup",
        headers=headers,
        params={"asTeamId": team_id}
    )

    if response.status_code == 401:
        print("RunwayAPI ----> 创建资源组失败，认证失败")
        return 401

    if response.status_code != 200:
        print(f"RunwayAPI ----> 创建资源组失败，状态码: {response.status_code}")
        return None
    
    data = response.json()        
    # 从assetGroup对象中获取id
    asset_group_id = data.get('assetGroup', {}).get('id')
    if asset_group_id:
        print(f"RunwayAPI ----> 创建资源组成功，ID: {asset_group_id}")
        return asset_group_id
    else:
        print("RunwayAPI ----> 创建资源组失败，未返回ID")
        return None


# 生成图片
def generate_image(
    token: str,
    team_id: str,
    session_id: str,
    prompt: str,
    resolution: str = '9:16',
    num_images: int = 1,
    seed: int = random.randint(1, 1000000)
) -> list[str]:
    print(f"RunwayAPI ----> 开始生成图片，提示词: {prompt}, 分辨率: {resolution}")
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("RunwayAPI ----> 获取资源组ID失败，无法生成图片")
        return None
    width, height = RESOLUTION_MAP[resolution]
    # 准备正确的API请求参数
    payload={
        "taskType": "text_to_image",
        "internal": False,
        "options": {
            "text_prompt": prompt,
            "seed": seed,
            "exploreMode": True,
            "width": width,
            "height": height,
            "flip": True,
            "num_images": num_images,
            "diversity": 2,
            "name": f"Frames {prompt} a-2 {str(seed)[:-2]}",
            "assetGroupId": asset_group_id
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }

    while True:
        try:
            if not is_can_generate_image(token, team_id):
                print("RunwayAPI ----> 当前无法生成图片，等待中...")
                time.sleep(1)
                continue

            print("RunwayAPI ----> 发送生成图片请求")
            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 401:
                print("RunwayAPI ----> 生成图片失败，认证失败")
                return 401
                
            if response.status_code == 429:
                print("RunwayAPI ----> 请求过于频繁，等待3秒后重试")
                time.sleep(3)
                continue
                
            if response.status_code == 200:
                print("RunwayAPI ----> 生成图片请求成功")
                break
            
            if response.status_code == 400:
                return "FAILED"
            print(f"RunwayAPI ----> 生成图片请求失败，状态码: {response.status_code}，等待3秒后重试")
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"RunwayAPI ----> 生成图片请求异常: {e}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')
    print(f"RunwayAPI ----> 图片生成任务已创建，ID: {task_id}")

    return task_id

def generate_video_for_gen4(
    token: str,
    team_id: str,
    session_id: str,
    image_url: str,
    prompt: str,
    second: int = 5,
    width: int = 1088,
    height: int = 1920,
    seed: int = random.randint(1, 4294967295)
) -> list[str]:
    print(f"RunwayAPI ----> 开始生成Gen4视频，提示词: {prompt}, 时长: {second}秒")
    model = "gen4_turbo"
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("RunwayAPI ----> 获取资源组ID失败，无法生成视频")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }

    if width > height:
        width = 1280
        height = 720
    else:
        width = 720
        height = 1280
    
    payload = {
        "taskType": model,
        "internal": False,
        "options": {
            "name": f"Gen-4 Turbo {prompt}",
            "seed": seed,
            "route": "i2v",
            "exploreMode": True,
            "watermark": False,
            "width": width,
            "height": height,
            "seconds": second,
            "init_image": image_url,
            "flip": True,
            "assetGroupId": asset_group_id,
            "text_prompt": prompt
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    while True:
        try:
            if not is_can_generate_video(token, team_id, model, second):
                print("RunwayAPI ----> 当前无法生成Gen4视频，等待中...")
                time.sleep(1)
                continue

            print("RunwayAPI ----> 发送生成Gen4视频请求")
            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            
            if response.status_code == 401:
                print("RunwayAPI ----> 生成Gen4视频失败，认证失败")
                return 401
                
            if response.status_code == 429:
                print("RunwayAPI ----> 请求过于频繁，等待3秒后重试")
                time.sleep(3)
                continue
            
            if response.status_code == 200:
                print("RunwayAPI ----> 生成Gen4视频请求成功")
                break
                
            print(f"RunwayAPI ----> 生成Gen4视频请求失败，状态码: {response.status_code}，等待3秒后重试")
            print(f"response : {response.content}")
            print(f"payload: {payload}")
            if response.status_code == 400:
                return "FAILED"
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"RunwayAPI ----> 生成Gen4视频请求异常: {e}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')
    print(f"RunwayAPI ----> Gen4视频生成任务已创建，ID: {task_id}")

    return task_id


# 生成视频
def generate_video_for_gen3a(
    token: str,
    team_id: str,
    session_id: str,
    image_url: str,
    prompt: str,
    second: int = 5,
    seed: int = random.randint(1, 4294967295)
) -> list[str]:
    print(f"RunwayAPI ----> 开始生成Gen3a视频，提示词: {prompt}, 时长: {second}秒")
    model = "gen3a_turbo"
    asset_group_id = get_asset_group_id(token, session_id, team_id)
    if not asset_group_id:
        print("RunwayAPI ----> 获取资源组ID失败，无法生成视频")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT
    }
    
    payload = {
        "taskType": model,
        "internal": False,
        "options": {
            "name": f"Gen-3 Alpha Turbo {prompt}",
            "seed": seed,
            "exploreMode": True,
            "watermark": False,
            "enhance_prompt": True,
            "seconds": second,
            "keyframes": [
                {
                    "image": image_url,
                    "timestamp": 0
                }
            ],
            "text_prompt": prompt,
            "flip": True,
            "assetGroupId": asset_group_id
        },
        "asTeamId": team_id,
        "sessionId": session_id
    }

    while True:
        try:
            if not is_can_generate_video(token, team_id, model, second):
                print("RunwayAPI ----> 当前无法生成Gen3a视频，等待中...")
                time.sleep(1)
                continue

            print("RunwayAPI ----> 发送生成Gen3a视频请求")
            response = requests.post(
                f"https://api.runwayml.com/v1/tasks",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 401:
                print("RunwayAPI ----> 生成Gen3a视频失败，认证失败")
                return 401
                
            if response.status_code == 429:
                print("RunwayAPI ----> 请求过于频繁，等待3秒后重试")
                time.sleep(3)
                continue
            
            if response.status_code == 200:
                print("RunwayAPI ----> 生成Gen3a视频请求成功")
                break
                

            print(f"RunwayAPI ----> 生成Gen3a视频请求失败，状态码: {response.status_code}，等待3秒后重试")
            print(f"response : {response.content}")
            print(f"payload: {payload}")
            if response.status_code == 400:
                return "FAILED"
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"RunwayAPI ----> 生成Gen3a视频请求异常: {e}")
            print(traceback.format_exc())
            return None
    
    data = response.json()
    task_id = data.get('task', {}).get('id')
    print(f"RunwayAPI ----> Gen3a视频生成任务已创建，ID: {task_id}")

    return task_id
    
# 获取视频任务状态, 返回视频URL
def get_video_task_detail(token: str, team_id: str, task_id: str) -> Optional[Dict]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    print(f"RunwayAPI ----> 获取视频任务状态，任务ID: {task_id}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    while True:
        try:
            response = requests.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers=headers,
                params={"asTeamId": team_id}
            )
            
            if response.status_code == 401:
                print("RunwayAPI ----> 获取视频任务状态失败，认证失败")
                return 401

            if response.status_code == 404:
                print(f"RunwayAPI ----> 获取视频任务状态失败，任务ID: {task_id} 被取消")
                return "CANCELLED"
            
            if response.status_code != 200:
                print(f"RunwayAPI ----> 获取视频任务状态失败，状态码: {response.status_code}")
                return None
                
            data = response.json()
            task = data.get('task', {})
            status = task.get('status')
            if status is None:
                print("RunwayAPI ----> 获取视频任务状态失败，未返回状态")
                return None

            # 任务完成且成功
            if status == 'SUCCEEDED' and task.get('artifacts'):
                artifact = task['artifacts'][0]
                url = artifact.get('url')
                print(f"RunwayAPI ----> 视频任务已完成，URL: {url}")
                return url
            # 任务失败或取消    
            if status in ['FAILED']:
                print(f"RunwayAPI ----> 视频任务{status}，生成失败")
                return "FAILED"
            if status == 'CANCELLED':
                print(f"RunwayAPI ----> 视频任务{status}，生成取消")
                return "CANCELLED"
            # 任务仍在进行中,等待3秒后继续查询
            print(f"RunwayAPI ----> 视频任务状态: {status}，等待3秒后继续查询")
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"RunwayAPI ----> 获取视频任务状态请求异常: {e}")
            print(traceback.format_exc())
            return None
        except Exception as e:
            print(f"RunwayAPI ----> 获取视频任务状态异常: {e}")
            print(traceback.format_exc())
            return None

# 获取图片任务状态, 返回图片URL列表
def get_image_task_detail(token: str, team_id: str, task_id: str) -> list[str]:
    """
    获取任务详细信息
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict: 包含任务详细信息的字典，失败返回None
    """
    print(f"RunwayAPI ----> 获取图片任务状态，任务ID: {task_id}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    while True:
        try:
            response = requests.get(
                f"https://api.runwayml.com/v1/tasks/{task_id}",
                headers=headers,
                params={"asTeamId": team_id}
            )
            
            data = response.json()
            task = data.get('task', {})
            status = task.get('status')

            if response.status_code == 401:
                print("RunwayAPI ----> 获取图片任务状态失败，认证失败")
                return 401

            if response.status_code == 404:
                print(f"RunwayAPI ----> 获取图片任务状态失败，任务ID: {task_id} 被取消")
                return "CANCELLED"

            if response.status_code != 200:
                print(f"RunwayAPI ----> 获取图片任务状态失败，状态码: {response.status_code}")
                return None

            if status is None:
                print("RunwayAPI ----> 获取图片任务状态失败，未返回状态")
                return None

            # 任务完成且成功
            if status == 'SUCCEEDED' and task.get('artifacts'):
                artifacts = task['artifacts']
                urls = []
                for artifact in artifacts:
                    urls.append(artifact.get('url'))
                print(f"RunwayAPI ----> 图片任务已完成，获取到 {len(urls)} 个URL")
                return urls
            # 任务失败或取消    
            if status in ['FAILED']:
                print(f"RunwayAPI ----> 图片任务{status}，生成失败")
                return "FAILED"
            if status == 'CANCELLED':
                print(f"RunwayAPI ----> 图片任务{status}，生成取消")
                return "CANCELLED"
            # 任务仍在进行中,等待3秒后继续查询
            print(f"RunwayAPI ----> 图片任务状态: {status}，等待3秒后继续查询")
            time.sleep(3)
            
        except Exception as e:
            print(f"RunwayAPI ----> 获取图片任务状态异常: {e}")
            print(traceback.format_exc())
            return None

# 上传图片，获取图片链接
def upload_image(token: str, file_path: str) -> Optional[str]:
    """
    上传图片
    """
    print(f"RunwayAPI ----> 开始上传图片: {file_path}")
    try:
        file_name = os.path.basename(file_path)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        }
        payload = {
            "filename": file_name,
            "numberOfParts": 1,
            "type": "DATASET"
        }

        # 重试机制
        for retry in range(MAX_RETRIES):
            try:
                print(f"RunwayAPI ----> 请求上传链接，尝试第 {retry+1} 次")
                response = requests.post(
                    f"https://api.runwayml.com/v1/uploads",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 401:
                    print("RunwayAPI ----> 上传图片失败，认证失败")
                    return 401

                if response.status_code != 200:
                    print(f"RunwayAPI ----> 请求上传链接失败，状态码: {response.status_code}")
                    if retry < MAX_RETRIES - 1:
                        print(f"RunwayAPI ----> {RETRY_INTERVAL}秒后重试")
                        time.sleep(RETRY_INTERVAL)
                        continue
                    return None

                data = response.json()
                upload_url = data['uploadUrls'][0]
                upload_id = data['id']
                print(f"RunwayAPI ----> 获取上传链接成功，ID: {upload_id}")

                file_ext = os.path.splitext(file_path)[1].lower()
                content_type = CONTENT_TYPE_MAP.get(file_ext, 'application/octet-stream')
                headers = {
                    "Accept": "*/*",
                    "Content-Type": content_type,
                    "sec-fetch-site": "cross-site",
                    "User-Agent": USER_AGENT
                }

                file_size = os.path.getsize(file_path)
                headers["Content-Length"] = str(file_size)
                print(f"RunwayAPI ----> 开始上传文件，大小: {file_size} 字节")

                with open(file_path, 'rb') as f:
                    response = requests.put(upload_url, data=f, headers=headers)
                    response.raise_for_status()

                    etag = response.headers.get('ETag')
                    url = etag.strip('"')
                    if url:
                        print("RunwayAPI ----> 文件上传成功，完成上传流程")
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        }
                        payload = {
                            "parts": [
                                {
                                    "PartNumber": 1,
                                    "ETag": url
                                }
                            ]
                        }
                        response = requests.post(
                            f"https://api.runwayml.com/v1/uploads/{upload_id}/complete",
                            headers=headers,
                            json=payload
                        )

                        if response.status_code == 401:
                            print("RunwayAPI ----> 完成上传流程失败，认证失败")
                            return 401

                        if response.status_code != 200:
                            print(f"RunwayAPI ----> 完成上传流程失败，状态码: {response.status_code}")
                            if retry < MAX_RETRIES - 1:
                                print(f"RunwayAPI ----> {RETRY_INTERVAL}秒后重试")
                                time.sleep(RETRY_INTERVAL)
                                continue
                            return None

                        data = response.json()
                        image_url = data.get('url')
                        print(f"RunwayAPI ----> 图片上传完成，URL: {image_url}")
                        return image_url

                break

            except (ConnectionError, ProtocolError) as e:
                print(f"RunwayAPI ----> 上传图片连接异常: {e}")
                print(traceback.format_exc())
                if retry < MAX_RETRIES - 1:
                    print(f"RunwayAPI ----> {RETRY_INTERVAL}秒后重试")
                    time.sleep(RETRY_INTERVAL)
                    continue
                return None

            except RequestException as e:
                print(f"RunwayAPI ----> 上传图片请求异常: {e}")
                print(traceback.format_exc())
                if retry < MAX_RETRIES - 1:
                    print(f"RunwayAPI ----> {RETRY_INTERVAL}秒后重试")
                    time.sleep(RETRY_INTERVAL)
                    continue
                return None

    except Exception as e:
        print(f"RunwayAPI ----> 上传图片发生异常: {e}")
        print(traceback.format_exc())
        return None

# 检查是否可以生成图片
def is_can_generate_image(token: str, team_id: str) -> bool:
    """
    检查是否可以生成图片
    """
    print("RunwayAPI ----> 检查是否可以生成图片")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    payload = {
        "feature": "text_to_image",
        "count": 1,
        "asTeamId": team_id,
        "taskOptions": {
            "width": 0,
            "height": 0,
            "num_images": 4
        }
    }
    response = requests.post(
        "https://api.runwayml.com/v1/billing/estimate_feature_cost_credits",
        headers=headers,
        json=payload
    )
    if response.status_code == 401:
        print("RunwayAPI ----> 检查生成图片权限失败，认证失败")
        return 401
    if response.status_code != 200:
        print(f"RunwayAPI ----> 检查生成图片权限失败，状态码: {response.status_code}")
        return None
    data = response.json()
    result = data.get('canUseExploreMode')
    print(f"RunwayAPI ----> 是否可以生成图片: {result}")
    return result

# 检查是否可以生成视频,模型分类
def is_can_generate_video(
        token: str, 
        team_id: str,
        model: str,
        second: int) -> bool:
    """
    检查是否可以生成视频
    """
    print(f"RunwayAPI ----> 检查是否可以生成视频，模型: {model}，时长: {second}秒")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    payload = {
        "feature": model,
        "count": 1,
        "asTeamId": team_id,
        "taskOptions": {
            "seconds": second
        }
    }
    response = requests.post(
        "https://api.runwayml.com/v1/billing/estimate_feature_cost_credits",
        headers=headers,
        json=payload
    )
    if response.status_code == 401:
        print("RunwayAPI ----> 检查生成视频权限失败，认证失败")
        return 401
    if response.status_code != 200:
        print(f"RunwayAPI ----> 检查生成视频权限失败，状态码: {response.status_code}")
        return None
    data = response.json()
    result = data.get('canUseExploreMode')
    print(f"RunwayAPI ----> 是否可以生成视频: {result}")
    return result

# 对日期做个加密/ 对年月日做md5加密
def encrypt_date(date: str) -> str:
    """
    对日期做个加密
    """
    print(f"RunwayAPI ----> 对日期进行MD5加密: {date}")
    md5 = hashlib.md5()
    md5.update(date.encode('utf-8'))
    result = md5.hexdigest()
    print(f"RunwayAPI ----> 加密结果: {result}")
    return result

def fetch_runway_assets(token: str, team_id: str):
    """
    获取Runway资源列表
    """
    print(f"RunwayAPI ----> 获取Runway资源列表，团队ID: {team_id}")
    url = "https://api.runwayml.com/v1/assets_pending"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    params = {
        "privateInTeam": "true", 
        "asTeamId": team_id
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"RunwayAPI ----> 获取资源列表失败: {e}")
        print(traceback.format_exc())
        return None
    
def check_and_process_assets(data, token: str, list_task_id: list):
    """
    检查和处理资源列表
    """
    if not data or 'pendingAssets' not in data:
        print("RunwayAPI ----> 没有可处理的资源")
        return
    
    for asset in data['pendingAssets']:
        asset_id = asset.get('id', '')
        progress_ratio = asset.get('progressRatio', 0)
        if (progress_ratio == '0' or progress_ratio == 0) and asset_id not in list_task_id:
            print(f"RunwayAPI ----> 发现未进行的任务: {asset_id}，进度: {progress_ratio}，准备删除")
            delete_task(token, asset_id)
    


def delete_task(token: str, asset_id: str):
    print(f"RunwayAPI ----> 删除任务，ID: {asset_id}")
    url = f"https://api.runwayml.com/v1/tasks/{asset_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        print(f"RunwayAPI ----> 成功删除任务: {asset_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"RunwayAPI ----> 删除任务失败: {e}")
        print(traceback.format_exc())
        return False

def delete_other_task(token: str, team_id: str, list_task_id: list):
    """
    删除其他任务
    """
    assets = fetch_runway_assets(token, team_id)
    if assets:
        check_and_process_assets(assets, token, list_task_id)
    else:
        print("RunwayAPI ----> 获取资源列表失败，无法清理任务")

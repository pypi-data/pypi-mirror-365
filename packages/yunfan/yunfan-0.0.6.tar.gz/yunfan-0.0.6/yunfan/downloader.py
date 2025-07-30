import os
import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm
from PIL import Image
import io
import torch
from torch.utils.data import Dataset
from torchvision import transforms 

CONTENT_TYPE="application/json"

def parse_url(url):

     # 解析 URL
    parsed_url = urlparse(url)
    
    # 提取 IP_port
    IP_port = parsed_url.netloc

    # 提取 ID
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 3 and path_parts[0] == "projects":
        ID = path_parts[1]
    else:
        raise ValueError("Invalid URL format: dataset ID not found")
    
    # 提取 token
    query_params = parse_qs(parsed_url.query)
    token = query_params.get('token', [None])[0]

    if token is None:
        raise ValueError("Invalid URL format: token not found")

    return IP_port, ID, token

def get_dataset_detail(url, token, arg_json):
    if arg_json != None:
        is_review = arg_json.get("is_review", 0)
        token_download = arg_json.get("token", None)
        params = {
        "is_review": int(is_review),
        "token": token_download
        }
    else:
        params = {
        "is_review": 0,
        "token": None
        }
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": CONTENT_TYPE
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # 解析响应JSON数据
        dataset_info = response.json()
        
        # 提取所需字段
        result = dataset_info.get("result")
        dataset_id = result.get("id")
        dataset_name = result.get("name")
        task_number = result.get("task_number")

        # 打印提取的信息
        print(f"Dataset ID: {dataset_id}")
        print(f"Dataset Name: {dataset_name}")
        print(f"Task Number: {task_number}")
        return task_number
        # 在这里可以添加保存或进一步处理逻辑
    else:
        print(f"Failed to get dataset detail info. Status code: {response.status_code}")
        print(f"Response: {response.text}")

        return None

def xml_indent(elem, level=0):
        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                xml_indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

class DetectionDataset(Dataset):
    def __init__(self, IP_port, dataset_ID, task_number, token, transform=None):
        self.IP_port = IP_port
        self.dataset_ID = dataset_ID
        self.task_number = task_number
        self.token = token
        # 强制等于1
        self.page_size = 1
        self.transform = transform if transform is not None else transforms.ToTensor()  # 初始化 ToTensor 转换
        self.labels_list = []
        self.labels_dict = {}
        self.headers = {
        "Authorization": f"Token {self.token}",
        "Content-Type": CONTENT_TYPE
        }

        # 假设我们有两个类别: 'person' 和 'car'
        settings_url = f"http://{self.IP_port}/api/projects/{self.dataset_ID}"

        # 发送请求
        settings_response = requests.get(settings_url, headers=self.headers)

        if settings_response.status_code == 200:
            # 解析响应JSON数据
            self.labels_list = settings_response.json().get("parsed_label_config", []).get("label", []).get("labels", [])
            self.labels_dict = {label: idx + 1 for idx, label in enumerate(self.labels_list)}

    def __len__(self):
        return self.task_number

    def __getitem__(self, idx):
        # 构建请求URL
        idx = idx + 1
        url = f"http://{self.IP_port}/api/tasks/?page={idx}&page_size={self.page_size}&project={self.dataset_ID}"

        # 发送请求
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            # 解析响应JSON数据
            tasks = response.json().get("tasks", [])
            task = tasks[0]
            for task in tasks:
                obj_path = task.get("object_path")
                img_name = os.path.basename(obj_path)
                data = task.get("data", {})
                img_url = data.get("image", {})

                if img_url:
                    # 下载图像
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content)).convert("RGB")
                    else:
                        print(f"Failed to download image {img_name}. Status code: {img_response.status_code}")

                    # 保存标签信息
                    boxes = []
                    labels = []
                    annotations = task.get("annotations", [{}])
                    if annotations:
                        for ann in annotations[0].get("result", []):
                            xmin_value = float(ann["value"]["x"]) * float(task.get("data_details", {}).get("width")) / 100.0
                            ymin_value = float(ann["value"]["y"]) * float(task.get("data_details", {}).get("height")) / 100.0
                            xmax_value = xmin_value + float(ann["value"]["width"]) * float(task.get("data_details", {}).get("width")) / 100.0
                            ymax_value = ymin_value + float(ann["value"]["height"]) * float(task.get("data_details", {}).get("height")) / 100.0
                            boxes.append([xmin_value, ymin_value, xmax_value, ymax_value])
                            name = ann["value"]["rectanglelabels"][0]
                            labels.append(self.class_to_idx[name])

                if self.transform:
                    image = self.transform(image)

                target = {
                    'boxes': torch.tensor(boxes, dtype=torch.float32),
                    'labels': torch.tensor(labels, dtype=torch.int64)
                }

                return image, target
        else:
            print("yunfan get task response not ok!")

    @property
    def class_to_idx(self):
        return self.labels_dict

def download_dataset_task(IP_port, dataset_ID, task_number, img_path, label_path, token, page_size=30):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": CONTENT_TYPE
    }

    #如果是raw数据集需要下载描述信息
    raw_url = f"http://{IP_port}/api/projects/{dataset_ID}/rawinfos/?dataset_id={dataset_ID}"
    # 发送请求
    raw_response = requests.get(raw_url, headers=headers)
    raw_info = raw_response.json().get("message", None)
    if raw_info:
        with open(os.path.join(label_path, 'project-info.json'), 'w', encoding='utf-8') as f:
                    json.dump(raw_info, f, ensure_ascii=False)

    # 计算总页数
    total_pages = (task_number + page_size - 1) // page_size

    __desc = f"Processing pages (Pagesize {page_size})"
    
    for page in tqdm(range(1, total_pages + 1), desc=__desc):
        # 构建请求URL
        url = f"http://{IP_port}/api/tasks/?page={page}&page_size={page_size}&project={dataset_ID}"
        
        # 发送请求
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # 解析响应JSON数据
            tasks = response.json().get("tasks", [])
            for task in tasks:
                task_id = task.get("id")
                obj_path = task.get("object_path")
                img_name = obj_path.replace("/", "_")#os.path.basename(obj_path)
                data = task.get("data", {})
                img_url = data.get("image", {})
                raw = data.get("raw", {})
                video = data.get("video", {})

                if raw:
                    raw_response = requests.get(raw)
                    if raw_response.status_code == 200:
                        with open(os.path.join(img_path, img_name), 'wb') as img_file:
                            img_file.write(raw_response.content)
                    else:
                        print(f"Failed to download raw {img_name}. Status code: {raw_response.status_code}")
                elif video:
                    video_response = requests.get(video)
                    if video_response.status_code == 200:
                        with open(os.path.join(img_path, img_name), 'wb') as img_file:
                            img_file.write(video_response.content)
                    else:
                        print(f"Failed to download video {img_name}. Status code: {raw_response.status_code}")
                elif img_url:
                    # 下载图像
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        with open(os.path.join(img_path, img_name), 'wb') as img_file:
                            img_file.write(img_response.content)
                    else:
                        print(f"Failed to download image {img_name}. Status code: {img_response.status_code}")
                    
                    # 保存标签信息
                    annotations = task.get("annotations", [{}])
                    annotation = ET.Element("annotation")

                    folder = ET.SubElement(annotation, "folder")
                    folder.text = os.path.basename(img_path)
                    filename = ET.SubElement(annotation, "filename")
                    filename.text = img_name
                    path = ET.SubElement(annotation, "path")
                    path.text = os.path.join(img_path, img_name)
                
                    # 添加大小信息
                    size = ET.SubElement(annotation, "size")
                    width = ET.SubElement(size, "width")
                    height = ET.SubElement(size, "height")
                    width.text = str(task.get("data_details", {}).get("width"))
                    height.text = str(task.get("data_details", {}).get("height"))

                    # 添加对象信息
                    if annotations:
                        for ann in annotations[0].get("result", []):
                            obj = ET.SubElement(annotation, "object")
                            name = ET.SubElement(obj, "name")
                            name.text = ann["value"]["rectanglelabels"][0]
                            bndbox = ET.SubElement(obj, "bndbox")
                            xmin = ET.SubElement(bndbox, "xmin")
                            ymin = ET.SubElement(bndbox, "ymin")
                            xmax = ET.SubElement(bndbox, "xmax")
                            ymax = ET.SubElement(bndbox, "ymax")
                            xmin_value = float(ann["value"]["x"]) * float(task.get("data_details", {}).get("width")) / 100.0
                            ymin_value = float(ann["value"]["y"]) * float(task.get("data_details", {}).get("height")) / 100.0
                            xmax_value = xmin_value + float(ann["value"]["width"]) * float(task.get("data_details", {}).get("width")) / 100.0
                            ymax_value = ymin_value + float(ann["value"]["height"]) * float(task.get("data_details", {}).get("height")) / 100.0
                            xmin.text = str(round(xmin_value))
                            ymin.text = str(round(ymin_value))
                            xmax.text = str(round(xmax_value))
                            ymax.text = str(round(ymax_value))
                    
                     # 保存XML文件
                    prefix, _ = os.path.splitext(img_name)
                    label_filename = f"{prefix}.xml"
                    xml_indent(annotation)
                    tree = ET.ElementTree(annotation)
                    tree.write(os.path.join(label_path, label_filename))
                else:
                    print(f"No image/raw/video found in task {task_id}")
        else:
            print(f"Failed to get tasks for page {page}. Status code: {response.status_code}")
            print(f"Response: {response.text}")

def download_dataset(dataset_url, save_path, if_dataloader=False ,transform=None, arg_json=None):
    # dataset_url 的形式应该是 http://<IP_port>/projects/<ID>/data?token=<token>"

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    img_path = os.path.join(save_path, "img")
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    label_path = os.path.join(save_path, "label")
    if not os.path.exists(label_path):
        os.makedirs(label_path)

    IP_port, dataset_ID, token = parse_url(dataset_url)

    #获取数据集信息
    dataset_detail_url = f"http://{IP_port}/api/projects/{dataset_ID}/dataset-detail-info/"
    task_number = get_dataset_detail(dataset_detail_url, token, arg_json)

    print("Downloading dataset...")
    download_dataset_task(IP_port, dataset_ID, task_number, img_path, label_path, token)

    if if_dataloader:
        dataset = DetectionDataset(IP_port, dataset_ID, task_number, token, transform=transform)
        return dataset
    else:
        return
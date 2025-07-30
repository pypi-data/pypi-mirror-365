
import os
import hashlib
from pdf2image import convert_from_path
from xianbao import DictManager, FileScanner
from xianbao.core.context import global_context


def scan(path: str, deep: int) -> list:
    try:
        return FileScanner.catalog_deep_list(path, deep)
    except Exception as e:
        return []


def convert_pdf_to_jpg(pdf_path: str, output_folder: str, poppler_path: str) -> None:
    """
    将指定 PDF 文件转换为 JPG 图像。

    :param poppler_path:
    :param pdf_path: PDF 文件路径
    :param output_folder: 输出文件夹路径
    """
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        for i, image in enumerate(images):
            image.save(os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}.jpg"), "JPEG")
    except Exception as e:
        print(f"Error converting PDF to JPG: {e}")


def scan_and_process_files(directory_: str, file_mapping_: dict, poppler_path: str) -> dict:
    """
    扫描目录下的所有文件，处理 PDF 和图片文件，并将相关信息记录到任务中。

    :param poppler_path:
    :param directory_: 交易路径
    :param file_mapping_: 文件名映射字典
    :return: 失败文件名列表
    """
    failed_files_ = []

    task_manager_op = global_context.get('task_manager')

    if task_manager_op is None:
        raise Exception("任务管理器未初始化")

    task_id = None

    t = directory_.split(os.sep)
    relative_path = str(os.path.join(*t[len(t)-2::]))  # 获取最后两层路径作为相对路径
    path_hash = hashlib.sha256(relative_path.encode()).hexdigest()  # 使用最后两层路径作为hash
    existing_tasks = task_manager_op.list_tasks_by_business_type(path_hash, limit=1, offset=0)
    if existing_tasks:
        return {'id': existing_tasks[0]['id'], 'failed_files': []}

    meta = {
        "relative_path": relative_path,  # 保持最后两层路径
        "ums_receipt": "",
        "ikea_receipt": "",
        "invoice": "",
        "delivery_note": "",
        "errors": []
    }

    errors = []
    status = 0

    for root, dirs, files in os.walk(directory_):
        for file in files:
            try:
                full_path = os.path.abspath(os.path.join(root, file))
                filename, ext = os.path.splitext(file)

                # 如果是 PDF 文件，则转换为 JPG
                if ext.lower() == '.pdf':
                    convert_pdf_to_jpg(full_path, root, poppler_path=poppler_path)  # 转换 PDF 到 JPG，并保存在同一目录下
                    jpg_file = f"{filename}.jpg"  # 生成的 JPG 文件名与 PDF 一致
                    print(f"Converted {file} to {jpg_file}")
                    continue

                matched = False
                file_tmp = file.split('.')
                file_tmp = file_tmp[0].lower()

                for key in file_mapping_:
                    if file_tmp.find(key) > -1:
                        value = file_mapping_[key]
                        meta[value] = file
                        if value == 'ums_receipt':  # 银联小票
                            status |= int('1000000000000000', 2)
                        elif value == 'ikea_receipt':  # 宜家小票
                            status |= int('0100000000000000', 2)
                        elif value == 'invoice':  # 发票
                            status |= int('0010000000000000', 2)
                        elif value == 'delivery_note':  # 送货单
                            status |= int('0001000000000000', 2)
                        matched = True
                        break

                if not matched:
                    failed_files_.append(file)

            except Exception as e:
                print(f"Error processing file {file}: {e}")
                errors.append(f"Error processing file {file}: {e}")
    
    meta['errors'] = errors
    # 第一位: 表示成功识别到的图片数量
    task_id = task_manager_op.add_task(meta, hashlib.sha256(relative_path.encode()).hexdigest(), str(status))
    print(f"Added task with ID: {task_id}")

    return {'id': task_id, 'failed_files': failed_files_}


def fm_mapping() -> dict:
    dict_manager_ = DictManager()
    return dict_manager_.get_dict_as_mapping('ikea_fm')

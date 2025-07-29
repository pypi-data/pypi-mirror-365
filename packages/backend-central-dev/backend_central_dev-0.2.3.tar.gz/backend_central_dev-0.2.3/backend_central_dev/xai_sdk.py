from typing import Any
import requests
import json
import torch
import yaml
import os
import shutil
import glob
from backend_central_dev.data_processing.dataset_utils import (
    NewBasicDataModule
)
from backend_central_dev.constant import *
from .constant import *
from .utils.module_utils import *
from .model_training import lightning_model
from .utils.pytorch_utils import get_device


def register_executor(
    base_url, executor_name,
    executor_endpoint_url,
    executor_type,
    executor_info,
    sys_info
):
    url = f"{base_url}/task_publisher/executor"
    data = {
        "act": "create",
        ExecutorRegInfo.executor_name: executor_name,
        ExecutorRegInfo.executor_endpoint_url: executor_endpoint_url,
        ExecutorRegInfo.executor_type: executor_type,
        ExecutorRegInfo.executor_info: json.dumps(executor_info),
        ExecutorRegInfo.sys_info: json.dumps(sys_info),
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()

        if "application/json" in response.headers.get("Content-Type", ""):
            try:
                return response.json()
            except json.JSONDecodeError:
                # Handling JSON decoding errors
                return {
                    "status": "error",
                    "message": f"Failed to decode JSON. Response content: {response.text}",
                }
        else:
            return {
                "status": "error",
                "message": f"Unexpected response from server: {response.text}",
            }
    except Exception as e:
        raise RuntimeError(e)


def get_and_load_dataset_source_file(
    db_service_url
) -> type[NewBasicDataModule]:

    component_module_path = os.environ['COMPONENT_MODULE_PATH']
    dataset_name = db_service_url.split("/")[-1]
    dataset_module_file_path = os.path.join(
        component_module_path, f"dataset_{dataset_name}.py")

    # [TODO: need an update process]
    # if not os.path.exists(dataset_module_file_path):
    if True:
        get_dataset_file = requests.get(
            db_service_url + "/dataset_source_file"
        )

        dataset_file_src = get_dataset_file.content.decode("utf-8")

        with open(dataset_module_file_path, "w") as f:
            f.write(dataset_file_src)

    module_name = dataset_name
    module = load_module(module_name, dataset_module_file_path)

    dm_class = None
    for obj in vars(module).values():
        if isinstance(obj, type):
            if issubclass(obj, NewBasicDataModule) and obj.__name__ != "NewBasicDataModule":
                dm_class = obj
                break

    return dm_class


def download_model_module_source_code(
    model_service_url
):

    component_module_path = os.environ['COMPONENT_MODULE_PATH']
    model_name = model_service_url.split("/")[-1]
    model_module_file_path = os.path.join(
        component_module_path, f"model_{model_name}.py")

    # if not os.path.exists(model_module_file_path):
    if True:
        get_model_file = requests.get(
            model_service_url + "/model_source_file"
        )

        model_file_src = get_model_file.content.decode("utf-8")

        with open(model_module_file_path, "w") as f:
            f.write(model_file_src)

    return model_module_file_path


def download_xai_modules_source_code_and_load(
    xai_service_url
):
    # 规定最多只有一个文件夹，其内不包含文件夹，并且要包含__init__.py文件
    # 先加载这些包，后再加载不是包的单独文件
    # 如：module_a/__init__.py
    #    module_a/a.py
    #    module_a/b.py
    #    module_a/c.py
    #    xai.py
    # 其中xai模块依赖module_a模块
    # 结果就只会先加载module_a模块 后加载xai模块
    # module_a模块不能有外部本地依赖 只能有外部远程依赖（运行环境里的）
    xai_files_response = requests.get(
        xai_service_url + "/xai_source_files"
    )

    xai_file_dict = json.loads(xai_files_response.content.decode('utf-8'))
    loaded_modules = {}
    single_py_modules = {}
    packed_module_paths = []
    for py_file_name, py_file_content in xai_file_dict.items():
        py_module_file_path = os.path.join(
            os.environ['COMPONENT_MODULE_PATH'], py_file_name)
        os.makedirs(os.path.dirname(py_module_file_path), exist_ok=True)
        with open(py_module_file_path, "w") as f:
            f.write(py_file_content)
        # py_modules[py_module_file_path] = py_file_content
        if py_file_name.endswith('__init__.py'):
            packed_module_paths.append(
                py_module_file_path.replace('/__init__.py', ''))
        elif "/" not in py_file_name:
            single_py_modules[py_file_name.replace(
                '.py', '')] = py_module_file_path

    for packed_module_path in packed_module_paths:
        loaded_modules[packed_module_path.split(
            '/')[-1]] = load_package_and_submodules(packed_module_path)

    for py_module_name, py_module_file_path in single_py_modules.items():
        loaded_modules[py_module_name] = load_module(
            py_module_name, py_module_file_path)

    return loaded_modules


def get_configuration_resp(publisher_endpoint_url, configuration_id):
    response = requests.get(
        f"{publisher_endpoint_url}/task_publisher/configuration",
        params={
            "configuration_id": configuration_id
        }
    )
    return response.json()


def get_configuration(publisher_endpoint_url, configuration_id):
    cfg_resp = get_configuration_resp(
        publisher_endpoint_url, configuration_id)
    return yaml.safe_load(cfg_resp[Configuration.configuration_content]), cfg_resp


def get_lightning_model(model_cfg, datamodule, model_module_file_path=None):
    return lightning_model.MlxOps_LightningModel(
        get_fine_tunable_model_from_model_module_file(model_module_file_path),
        datamodule.num_classes,
        **model_cfg
    )


def get_trainer_configuration(publisher_endpoint_url, trainer_configuration_id):
    cfg, cfg_resp = get_configuration(
        publisher_endpoint_url, trainer_configuration_id
    )
    no_train = False
    if 'no_train' in cfg:
        del cfg['no_train']
        no_train = True
    return init_callbacks_for_trainer_config(cfg), cfg_resp, no_train


def get_exp_name(cfg_resps):
    model_cfg_name = cfg_resps['model_cfg'][Configuration.configuration_name]
    dataset_cfg_names = [dcfg[Configuration.configuration_name]
                         for dcfg in cfg_resps['dataset_cfgs']]
    trainer_cfg_name = cfg_resps['trainer_cfg'][Configuration.configuration_name]

    return f"{model_cfg_name}_{'_'.join(dataset_cfg_names)}_{trainer_cfg_name}"


def get_configurations_and_exp_exp_default_root_dir(publisher_endpoint_url, task_parameters):

    db_service_url = task_parameters[TaskExecution.db_service_url]
    dataset_configuration_ids = task_parameters[Configuration.dataset_configuration_id]
    model_configuration_id = task_parameters[Configuration.model_configuration_id]
    trainer_configuration_id = task_parameters[Configuration.trainer_configuration_id]

    datamodule_class = get_and_load_dataset_source_file(
        db_service_url
    )

    datamodule_cfg = {}
    cfg_resps = {
        'dataset_cfgs': [],
        'model_cfg': None,
        'trainer_cfg': None,
    }
    for dataset_configuration_id in dataset_configuration_ids:
        cfg, cfg_resp = get_configuration(
            publisher_endpoint_url,
            dataset_configuration_id)
        cfg_resps['dataset_cfgs'].append(cfg_resp)
        datamodule_cfg = datamodule_cfg | cfg

    model_cfg, model_cfg_resp = get_configuration(
        publisher_endpoint_url,
        model_configuration_id
    )

    cfg_resps["model_cfg"] = model_cfg_resp

    trainer_cfg, trainer_cfg_resp, no_train = get_trainer_configuration(
        publisher_endpoint_url,
        trainer_configuration_id
    )

    cfg_resps["trainer_cfg"] = trainer_cfg_resp

    return datamodule_class, datamodule_cfg, model_cfg, trainer_cfg, no_train, os.path.join(
        os.environ['COMPONENT_TRAINING_SAVE_PATH'],
        datamodule_class.__name__, f"{get_exp_name(cfg_resps)}"
    )


def get_task_execution_from_ticket(publisher_endpoint_url, task_ticket):
    task_execution_resp = requests.get(
        f"{publisher_endpoint_url}/task_publisher/task_execution",
        params={
            "task_ticket": task_ticket
        }
    )
    task_execution = task_execution_resp.json()
    return task_execution


def get_pipeline_execution_from_ticket(publisher_endpoint_url, pipeline_ticket):
    pipeline_execution_resp = requests.get(
        f"{publisher_endpoint_url}/task_publisher/pipeline_execution",
        params={
            "pipeline_ticket": pipeline_ticket
        }
    )
    pipeline_execution = pipeline_execution_resp.json()
    return pipeline_execution


def download_model_checkpoints_and_source_code(training_task_execution_ticket, publisher_endpoint_url, model_service_url):

    save_dir = os.path.join(
        os.environ['COMPONENT_TMP_PATH'],
        "model_checkpoints")
    os.makedirs(save_dir, exist_ok=True)
    zip_file_name = os.path.join(
        save_dir,
        f"{training_task_execution_ticket}.zip")
    unzip_dir = os.path.join(
        save_dir, training_task_execution_ticket)

    print("Download checkpoint to ", zip_file_name)
    if not os.path.exists(zip_file_name):
        resp = requests.get(
            f"{publisher_endpoint_url}/task_publisher/task_execution_result",
            params={
                "task_ticket": training_task_execution_ticket,
                "act": 'download'
            }
        )
        print("Download task execution result from ",
              resp.content.decode('utf-8'))
        rs_url = resp.content
        # print(rs_url)
        response = requests.get(
            rs_url
        )

        with open(zip_file_name, "wb") as f:
            f.write(response.content)

        shutil.unpack_archive(zip_file_name, unzip_dir)

        os.remove(zip_file_name)

    cpkt_path = get_best_performed_ckpt_path(unzip_dir)

    model_module_file_path = download_model_module_source_code(
        model_service_url)

    return cpkt_path, model_module_file_path


def get_trained_model_and_dataset_from_services(
    publisher_endpoint_url, training_task_execution_ticket,
    task_parameters
):
    ckpt_path, model_module_file_path = download_model_checkpoints_and_source_code(
        training_task_execution_ticket,
        publisher_endpoint_url,
        task_parameters[TaskExecution.model_service_url]
    )
    print("Trained ckpt path: ", ckpt_path)
    print("Model module path: ", model_module_file_path)

    datamodule_class, datamodule_cfg, model_cfg, trainer_cfg, no_train, exp_default_root_dir = \
        get_configurations_and_exp_exp_default_root_dir(
            publisher_endpoint_url, task_parameters)
    datamodule = datamodule_class(**datamodule_cfg)

    model = get_lightning_model(
        model_cfg, datamodule, model_module_file_path=model_module_file_path)

    if ckpt_path is not None:
        checkpoint = torch.load(ckpt_path, map_location=get_device())
        model.load_state_dict(checkpoint["state_dict"])
    else:
        print("No checkpoint is loaded")

    return model, datamodule


def get_model_evaluation_score_from_ckpt(checkpoint_path):
    return float(checkpoint_path.split('=')[-1].replace('.ckpt', ''))


def get_best_performed_ckpt_path(model_check_points_dir):
    print("Find model check points from ",
          model_check_points_dir + "/**/*.ckpt")
    checkpoint_paths = glob.glob(
        model_check_points_dir + "/**/*.ckpt", recursive=True)

    max_score_ckpt_i = 0
    # TODO: checkpoint reading logic

    if len(checkpoint_paths) == 0:
        return None
    return checkpoint_paths[max_score_ckpt_i]


# def load_model_from_ckpt(model_check_points_dir,  exp_default_root_dir, datamodule_class):
    # max_score_ckpt_path = get_best_performed_ckpt_path(model_check_points_dir)

    # print("Loading ckpt for prediction: ", max_score_ckpt_path.replace(
    #     exp_default_root_dir, "{exp_default_root_dir}"))

    # return lightning_model.MlxOps_LightningModel.load_from_checkpoint(
    #     max_score_ckpt_path,
    #     fine_tunable_model=get_fine_tunable_model_from_model_module_file(),
    #     output_features=datamodule_class.dataset_class.num_classes,
    # ).to(get_device())

def load_model_from_ckpt(model_cfg, datamodule, ckpt_path, model_module_file_path):
    print("Load AI model from", ckpt_path)
    model = get_lightning_model(
        model_cfg, datamodule, model_module_file_path=model_module_file_path)

    if ckpt_path is not None:
        checkpoint = torch.load(ckpt_path, map_location=get_device())
        model.load_state_dict(checkpoint["state_dict"])

    return model

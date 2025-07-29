import os
from typing import Optional, List, Dict

import click
import wandb
from tqdm import tqdm

from yms_zsl.tools.tool import get_current_time


def get_wandb_key(key_path):
    with open(key_path, 'r', encoding='utf-8') as f:
        key = f.read()
    return key


def wandb_init(project=None, key_path=None, name=None):
    run = None
    if project is not None:
        if key_path is None:
            raise ValueError("When 'project' is not None, 'key_path' should also not be None.")
        wandb_key = get_wandb_key(key_path)
        wandb.login(key=wandb_key)
        run = wandb.init(project=project, name=name)
    return run


def check_wandb_login_required():
    """兼容旧版的登录检查函数"""
    # 优先检查环境变量
    if os.environ.get("WANDB_API_KEY"):
        return False

    try:
        api = wandb.Api()
        # 方法 1：通过 settings 检查（适用于旧版）
        if hasattr(api, "settings") and api.settings.get("entity"):
            return False

        # 方法 2：通过 projects() 验证（通用性强）
        api.projects(per_page=1)  # 仅请求第一页的第一个项目
        return False
    except Exception as e:
        print(f"检测到意外错误: {str(e)}")
        return True  # 保守返回需要登录


def get_wandb_runs(
        project_path: str,
        default_name: str = "未命名",
        api_key: Optional[str] = None,
        per_page: int = 1000
) -> List[Dict[str, str]]:
    """
    获取指定 WandB 项目的所有运行信息（ID 和 Name）

    Args:
        project_path (str): 项目路径，格式为 "username/project_name"
        default_name (str): 当运行未命名时的默认显示名称（默认："未命名"）
        api_key (str, optional): WandB API 密钥，若未设置环境变量则需传入
        per_page (int): 分页查询每页数量（默认1000，用于处理大量运行）

    Returns:
        List[Dict]: 包含运行信息的字典列表，格式 [{"id": "...", "name": "..."}]

    Raises:
        ValueError: 项目路径格式错误
        wandb.errors.UsageError: API 密钥无效或未登录
    """
    # 参数校验
    if "/" not in project_path or len(project_path.split("/")) != 2:
        raise ValueError("项目路径格式应为 'username/project_name'")

    # 登录（仅在需要时）
    if api_key:
        wandb.login(key=api_key)
    elif not wandb.api.api_key:
        raise wandb.errors.UsageError("需要提供API密钥或预先调用wandb.login()")

    # 初始化API
    api = wandb.Api()

    try:
        # 分页获取所有运行（自动处理分页逻辑）
        runs = api.runs(project_path, per_page=per_page)
        print(f'共获取{len(runs)}个run')
        return [
            {
                "id": run.id,
                "name": run.name or default_name,
                "url": run.url,  # 增加实用字段
                "state": run.state  # 包含运行状态
            }
            for run in runs
        ]

    except wandb.errors.CommError as e:
        raise ConnectionError(f"连接失败: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"获取运行数据失败: {str(e)}") from e


def delete_runs(
        project_path: str,
        run_ids: Optional[List[str]] = None,
        run_names: Optional[List[str]] = None,
        delete_all: bool = False,
        dry_run: bool = True,
        api_key: Optional[str] = None,
        per_page: int = 500
) -> dict:
    """
    多功能WandB运行删除工具

    :param project_path: 项目路径（格式：username/project_name）
    :param run_ids: 指定要删除的运行ID列表（无视状态）
    :param run_names: 指定要删除的运行名称列表（无视状态）
    :param delete_all: 危险模式！删除所有运行（默认False）
    :param dry_run: 模拟运行模式（默认True）
    :param api_key: WandB API密钥
    :param per_page: 分页查询数量
    :return: 操作统计字典

    使用场景：
    1. 删除指定运行：delete_runs(..., run_ids=["abc","def"])
    2. 默认删除失败运行：delete_runs(...)
    3. 删除所有运行：delete_runs(..., delete_all=True)
    """
    preserve_states: List[str] = ["finished", "running"]
    # 参数校验
    if not project_path.count("/") == 1:
        raise ValueError("项目路径格式应为 username/project_name")
    if delete_all and (run_ids or run_names):
        raise ValueError("delete_all模式不能与其他筛选参数同时使用")

    # 身份验证
    if api_key:
        wandb.login(key=api_key)
    elif not wandb.api.api_key:
        raise wandb.errors.UsageError("需要API密钥或预先登录")

    api = wandb.Api()
    stats = {
        "total": 0,
        "candidates": 0,
        "deleted": 0,
        "failed": 0,
        "dry_run": dry_run
    }

    try:
        runs = api.runs(project_path, per_page=per_page)
        stats["total"] = len(runs)

        # 确定删除目标
        if delete_all:
            targets = runs
            click.secho("\n⚠️ 危险操作：将删除项目所有运行！", fg="red", bold=True)
        elif run_ids or run_names:
            targets = [
                run for run in runs
                if run.id in (run_ids or []) or run.name in (run_names or [])
            ]
            print(f"\n找到 {len(targets)} 个指定运行")
        else:
            targets = [run for run in runs if run.state not in preserve_states]
            print(f"\n找到 {len(targets)} 个非正常状态运行")

        stats["candidates"] = len(targets)

        if not targets:
            print("没有符合条件的运行")
            return stats

        # 打印预览
        print("\n待删除运行示例：")
        for run in targets[:3]:
            state = click.style(run.state, fg="green" if run.state == "finished" else "red")
            print(f" • {run.id} | {run.name} | 状态：{state}")
        if len(targets) > 3:
            print(f" ...（共 {len(targets)} 条）")

        # 安全确认
        if dry_run:
            click.secho("\n模拟运行模式：不会实际删除", fg="yellow")
            return stats

        if delete_all:
            msg = click.style("确认要删除所有运行吗？此操作不可逆！", fg="red", bold=True)
        else:
            msg = f"确认要删除 {len(targets)} 个运行吗？"

        if not click.confirm(msg, default=False):
            print("操作已取消")
            return stats

        # 执行删除
        print("\n删除进度：")
        for i, run in enumerate(targets, 1):
            try:
                run.delete()
                stats["deleted"] += 1
                print(click.style(f"  [{i}/{len(targets)}] 已删除 {run.id}", fg="green"))
            except Exception as e:
                stats["failed"] += 1
                print(click.style(f"  [{i}/{len(targets)}] 删除失败 {run.id}: {str(e)}", fg="red"))

        return stats

    except wandb.errors.CommError as e:
        raise ConnectionError(f"网络错误: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"操作失败: {str(e)}")


def get_all_artifacts_from_project(project_path, max_runs=None, run_id=None):
    """获取WandB项目或指定Run的所有Artifact

    Args:
        project_path (str): 项目路径，格式为 "entity/project"
        max_runs (int, optional): 最大获取Run数量（仅当未指定run_id时生效）
        run_id (str, optional): 指定要查询的Run ID

    Returns:
        list: 包含所有Artifact对象的列表
    """
    api = wandb.Api()
    all_artifacts = []
    seen_artifacts = set()  # 用于去重

    try:
        if run_id:
            # 处理单个Run的情况
            run = api.run(f"{project_path}/{run_id}")
            artifacts = run.logged_artifacts()

            for artifact in artifacts:
                artifact_id = f"{artifact.name}:{artifact.version}"
                if artifact_id not in seen_artifacts:
                    all_artifacts.append(artifact)
                    seen_artifacts.add(artifact_id)

            print(f"Found {len(all_artifacts)} artifacts in run {run_id}")
        else:
            # 处理整个项目的情况
            runs = api.runs(project_path, per_page=500)
            run_iterator = tqdm(runs[:max_runs] if max_runs else runs,
                                desc=f"Scanning {project_path}")

            for run in run_iterator:
                try:
                    artifacts = run.logged_artifacts()
                    for artifact in artifacts:
                        artifact_id = f"{artifact.name}:{artifact.version}"
                        if artifact_id not in seen_artifacts:
                            all_artifacts.append(artifact)
                            seen_artifacts.add(artifact_id)
                except Exception as run_error:
                    print(f"Error processing run {run.id}: {str(run_error)}")

    except Exception as e:
        print(f"Error: {str(e)}")
        return []

    return all_artifacts


def upload_model_dataset(
        artifact_dir: str,
        artifact_name: str,
        artifact_type: str) -> None:
    run_id = f'yms_upload_{artifact_type}_' + get_current_time('%y%m%d_%H%M%S')
    run = wandb.init(project='upload_model_dataset', name=artifact_name, id=run_id)
    artifact = wandb.Artifact(artifact_name, artifact_type)
    artifact.add_dir(artifact_dir)
    run.log_artifact(artifact)
    run.finish()


def download_model_dataset(
        download_name: str,
        run_name: str,
        artifact_type: str,
        download_dir: str = None,
        entity: str = 'YNA-DeepLearning'
) -> str:
    run_id = f'yms_download_{artifact_type}_' + get_current_time('%y%m%d_%H%M%S')
    run = wandb.init(project='download_model_dataset', name=run_name, id=run_id)
    artifact = run.use_artifact(entity + '/upload_model_dataset/' + download_name, type=artifact_type)
    artifact_dir = artifact.download(root=download_dir)
    return artifact_dir
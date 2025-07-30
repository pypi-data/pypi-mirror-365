import os
import re
from base.git import git_util
from base.log import log_util
from base.p4 import p4_util
from base.time_stamp import time_stamp_util
from module.p4 import p4_manager
from module.repo import repo_manager
from typing import Union, Dict, List, Callable


class PreCompile:
    '''
    完成编译前的一切准备操作:
    '''
    
    def __init__(self, p4_config: Dict, repo_info: List[Dict], feature_branch: Dict,
                 target_time_stamp: Union[int, float, str],
                 time_stamp_exclude_dirs: List[str], time_stamp_exclude_extensions: List[str], fallback_branch: Dict[str, str],
                 diff_ninja_log_path: str, delete_client: bool):
        self._logger = log_util.BccacheLogger(name="PreCompile")
        self._p4_config = p4_config
        self._repo_info = repo_info # repo 结构参考 product_config.json
        self._feature_branch = feature_branch # 用户实际修改的 branch, 即用户开发分支
        self._target_time_stamp = target_time_stamp # 希望修改的时间戳
        self._time_stamp_exclude_dirs = time_stamp_exclude_dirs # 需要忽略的改戳目录
        self._time_stamp_exclude_extensions = time_stamp_exclude_extensions # 需要忽略的改戳后缀名
        self._p4 = p4_util.P4Client(self._p4_config) 
        self._time_stamp_util = time_stamp_util.TimeStampUtil(target_time=self._target_time_stamp, exclude_dirs=self._time_stamp_exclude_dirs,
                                                              exclude_extensions=self._time_stamp_exclude_extensions)
        self._p4_manager = p4_manager.P4Manager(self._p4)
        self._p4_label_regex = self._p4_config["LABEL_REGEX"] # 从 p4 label 中提取 commitid 的正则表达式
        
        self._diff_ninja_log_path = diff_ninja_log_path
        self._delete_client = delete_client # 判断 p4 sync 后是否需要删除 client, 由配置文件导入
        
        # 当出现 cherry-pick 冲突失败时, 调用 checkout fallback_branch
        # fallback_branch 格式为: {"aha": "xxx", "iron": "xxx"}
        self._fallback_branch = fallback_branch
        
        
    def _init_repo(self):
        '''
        初始化 repo_manager
        '''
        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                repo_url = repo_config["url"]
                local_path = repo_config["local_path"]
                repo_config["repo_manager"] = repo_manager.RepoManager(local_path=local_path, repo_url=repo_url)
                repo_config["fallback_branch"] = self._fallback_branch[repo_name]
                
    
    def _get_commit_id_from_label(self, latest_label: str) -> Dict:
        '''
        从最近一次提交的 label 中提取 commit_id
        '''
        pattern = self._p4_label_regex
        return {name: id for name, id in re.findall(pattern, latest_label)}
    
    def run(self):
        '''
        运行入口函数
        '''        
        self._init_repo()
        # 获取基底的 commit_id
        with self._p4 as p4_client:
            latest_label = p4_client.get_latest_label()            
            base_commit_id = self._get_commit_id_from_label(latest_label=latest_label)
        
        
        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                # 切换基底 commit_id
                repo_config["repo_manager"].CheckoutRepo(branch=base_commit_id[repo_name], 
                                                         git_clean_excludes=repo_config["git_clean_excludes"])
                # 改代码时间戳
                self._time_stamp_util.process_directory(root_dir=repo_config["local_path"])
                
                # 从用户的 feature 分支获取用户新增的 commitId
                git_operator = git_util.GitOperator(repo_path=repo_config["local_path"])
                feature_commit_id = git_operator.get_commits_lists(target_branch=base_commit_id[repo_name], feature_branch=self._feature_branch[repo_name])
                for commit_id in feature_commit_id:
                    # 如果 cherry-pick 失败, 可能是出现了冲突, 直接无脑调用 checkout fallback_branch
                    if git_operator._run_command(command_args=["cherry-pick", commit_id]) is None:
                        fallback_branch = repo_config["fallback_branch"]
                        git_operator.checkout_branch(branch=fallback_branch)
                        
        
        
        # 执行 p4 拉缓存操作
        self._p4_manager.run_ci_check_task(self._diff_ninja_log_path, self._delete_client)
        self._logger.info(f"拉取缓存结束, 可以执行编译了")
        
import os
import sys
from base.file import file_util
from base.log import log_util
from base.ninja import ninja_util
from base.tos import tos_util
from base.p4 import p4_util
from business import postcompile_plugin
from business import precompile_plugin
from module.config import product_config
from module.p4 import p4_manager 
from business import compilecachesubmit_plugin
from typing import Union, Dict, List, Callable

class BlazeCache:
    '''
    BlazeCache 最顶层入口类, 封装了底层所有操作
    service 层封装 API 可以直接调用该类
    '''
    
    # 保存所有 product 对应的 product_config.json 存储的 tos 路径
    _PRODUCT_CONFIG_PATH = {
        "lark": "product_config/lark/product_config.json"
    }
    
    def __init__(self, product_name: str, build_dir: str, local_repo_dir: Dict,
                 os_type: str, task_type: str, 
                 branch_type: str, machine_id: str, ninja_exe_path: str,
                 mr_target_branch: str, feature_branch: Dict, p4_client: str, fallback_branch: Dict[str, str]):
        self._build_dir = build_dir # 本地代码仓目录
        self._product_name = product_name.lower() # 产品名, 如 lark
        self._os_type = os_type.lower() # 当前运行的操作系统
        self._task_type = task_type.lower() # 当前的任务类型, 一共有两类任务: ci_check_task、cache_generator_task, 对应 product_config.json
        self._branch_type = branch_type.lower() # 分支类型, 一共有两类: main、release
        self._machine_id = machine_id # 机器 id 标识
        
        self._product_config = self._get_product_config()
        
        
        # 格式化 os_type
        if self._os_type.startswith("win"):
            self._os_type = "Windows"
        elif self._os_type.startswith('darwin'):
            self._os_type = 'Darwin'
        elif self._os_type.startswith('linux'):
            self._os_type = 'Linux'
        self._p4_config = self._product_config.get_p4_config(task_type=self._task_type, branch_type=self._branch_type,
                                                             os_name=self._os_type).to_dict()
        self._p4_config["WORKDIR"] = os.path.join(self._build_dir, self._p4_config["WORKDIR"])
        
        
        # 判断是否在 sync 后需要删除 client
        self._delete_client = self._p4_config["DELETE_CLIENT"]
        
        self._p4_config["P4CLIENT"] = p4_client
        
        self._repo_config = self._product_config.repo_info.repos
        
        # 希望修改的时间戳, 从配置文件获取
        self._target_time_stamp = self._product_config.target_time_stamp
        # 在改戳时需要忽略的目录, 从配置文件获取
        self._time_stamp_exclude_dirs = self._product_config.time_stamp_exclude_dirs
        self._time_stamp_exclude_extensions = self._product_config.time_stamp_exclude_extensions
        
        self._ninja_exe_path = ninja_exe_path # ninja 的可执行程序路径
        
        self._mr_target_branch = mr_target_branch # 目标合入分支, 这个参数目前仅用于区分 .diff_ninja_log 在 tos 的存储路径
        # 目标合入的 Commit_Id {"aha": xxx, "iron": xxx}, 该参数用于切换分支(CI检查任务用于切换检测分支, 测速任务用于切换编译缓存分支)
        self._feature_branch = feature_branch 
        
        self._ninja_log_path = os.path.join(self._p4_config["WORKDIR"], ".ninja_log") # .ninja_log 文件路径
        self._logger = log_util.BccacheLogger(name="BlazeCache")
        
        self._local_repo_dir = local_repo_dir # 本地代码仓路径 {"aha": xxx, "iron": xxx}
        
        # 当出现 cherry-pick 冲突失败时, 调用 checkout fallback_branch
        # fallback_branch 格式为: {"aha": "xxx", "iron": "xxx"}
        self._fallback_branch = fallback_branch
        
    def _get_product_config(self):
        base_dir = ""
        if sys.platform.startswith("win"):
            # Windows: %AppData% 对应用户应用数据目录
            base_dir = os.path.expandvars("%AppData%/")
        elif sys.platform.startswith("darwin"):
            # macOS: ~/Library/Application Support/
            base_dir = os.path.expanduser("~/Library/Application Support/")
        elif sys.platform.startswith("linux"):
            # Linux: ~/.config/（注意：正确路径是 ~/.config 而非 ~/./config，两者等价但前者更规范）
            base_dir = os.path.expanduser("~/.config/")
        else:
            # 其他未知系统，默认使用当前目录
            base_dir = os.path.abspath("./") 
        local_product_config_path = os.path.join(base_dir, f"BlazeCache_tmp/product_config/{self._product_name.lower()}/product_config.json")
        
        # product_config 本地若不存在, 则从 tos 中获取
        if not os.path.exists(local_product_config_path):
            file_util.FileUtil.make_directory_exists(os.path.dirname(local_product_config_path))
            remote_product_config_path = self._PRODUCT_CONFIG_PATH[self._product_name]
            tos_util.BlazeCacheTos.download_file(local_file_path=local_product_config_path, remote_file_path=remote_product_config_path)
        
        return product_config.ProductConfig(config_path=local_product_config_path)
        
        
    def create_diff_ninja_log(self):
        '''
        调用 PostCompile 封装的 create_diff_ninja_log 接口
        '''
        diff_ninja_log_id_file_key = tos_util.BlazeCacheTos.get_diff_ninja_log_id_file_key(product_name=self._product_name,
                                                                                           os_type=self._os_type,
                                                                                           job_type=self._task_type,
                                                                                           branch_type=self._mr_target_branch,
                                                                                           machine_id=self._machine_id)
        # 获取上一次生成 .diff_ninja_log 的 id
        id = 0
        if tos_util.BlazeCacheTos.check_remote_file_exist(remote_file_path=diff_ninja_log_id_file_key):
            id = int(tos_util.BlazeCacheTos.get_object(remote_file_path=diff_ninja_log_id_file_key).decode("utf-8"))
        
        # id 值加一, 创建新的 .diff_ninja_log 文件并上传
        id += 1
        
        diff_ninja_log_file_key = tos_util.BlazeCacheTos.get_diff_ninja_log_file_key(product_name=self._product_name,
                                                                                     os_type=self._os_type,
                                                                                     job_type=self._task_type,
                                                                                     branch_type=self._mr_target_branch,
                                                                                     machine_id=self._machine_id,
                                                                                     id=str(id))
        print(self._p4_config["WORKDIR"])
        postcompile_plugin.PostCompile.create_diff_ninja_log(ninja_log_path=self._ninja_log_path, build_dir=self._p4_config["WORKDIR"],
                                                             ninja_exe_path=self._ninja_exe_path, diff_ninja_log_file_key=diff_ninja_log_file_key)
        
        # 最后更新 TOS 上 .diff_ninja_log 的 id 值
        tos_util.BlazeCacheTos.upload_object(content=str(id), remote_file_path=diff_ninja_log_id_file_key)
    
    
    def get_diff_ninja_log(self):
        '''
        获取 .diff_ninja_log, 如果本地没有, 就去 tos 下载
        '''
        diff_ninja_log_id_file_key = tos_util.BlazeCacheTos.get_diff_ninja_log_id_file_key(product_name=self._product_name,
                                                                                           os_type=self._os_type,
                                                                                           job_type=self._task_type,
                                                                                           branch_type=self._mr_target_branch,
                                                                                           machine_id=self._machine_id)
        if not tos_util.BlazeCacheTos.check_remote_file_exist(remote_file_path=diff_ninja_log_id_file_key):
            self._logger.warning(f"{diff_ninja_log_id_file_key} 不存在, 请检查 diff_ninja_log_id")
            return False
        
        id = tos_util.BlazeCacheTos.get_object(remote_file_path=diff_ninja_log_id_file_key).decode("utf-8")
        
        diff_ninja_log_file_key = tos_util.BlazeCacheTos.get_diff_ninja_log_file_key(product_name=self._product_name,
                                                                                     os_type=self._os_type,
                                                                                     job_type=self._task_type,
                                                                                     branch_type=self._mr_target_branch,
                                                                                     machine_id=self._machine_id,
                                                                                     id=id)
        
        base_dir = ""
        if sys.platform.startswith("win"):
            # Windows: %AppData% 对应用户应用数据目录
            base_dir = os.path.expandvars("%AppData%/")
        elif sys.platform.startswith("darwin"):
            # macOS: ~/Library/Application Support/
            base_dir = os.path.expanduser("~/Library/Application Support/")
        elif sys.platform.startswith("linux"):
            # Linux: ~/.config/（注意：正确路径是 ~/.config 而非 ~/./config，两者等价但前者更规范）
            base_dir = os.path.expanduser("~/.config/")
        else:
            # 其他未知系统，默认使用当前目录
            base_dir = os.path.abspath("./")
        local_diff_ninja_log_path = os.path.join(base_dir, f"BlazeCache_tmp/{diff_ninja_log_file_key}")
        # 如果本地存在 .diff_ninja_log 文件, 不需要从 tos 下载
        if os.path.exists(local_diff_ninja_log_path):
            return local_diff_ninja_log_path
        
        file_util.FileUtil.make_directory_exists(dirname=os.path.dirname(local_diff_ninja_log_path))
        if postcompile_plugin.PostCompile.get_diff_ninja_log(local_diff_ninja_log_path=local_diff_ninja_log_path, diff_ninja_log_file_key=diff_ninja_log_file_key):
            return local_diff_ninja_log_path
        return None
    
    def run_precompile_plugin(self):
        '''
        运行 precompile_plugin 入口函数
        '''
        for repo_dict in self._repo_config:
            for repo_name, repo_config in repo_dict.items():
                repo_config["local_path"] = self._local_repo_dir[repo_name]
                
        diff_ninja_log_path = self.get_diff_ninja_log()
        
        precompile = precompile_plugin.PreCompile(p4_config=self._p4_config, repo_info=self._repo_config,
                                                  feature_branch=self._feature_branch, delete_client=self._delete_client,
                                                  target_time_stamp=self._target_time_stamp, time_stamp_exclude_dirs=self._time_stamp_exclude_dirs,
                                                  time_stamp_exclude_extensions=self._time_stamp_exclude_extensions,fallback_branch=self._fallback_branch,
                                                  diff_ninja_log_path=diff_ninja_log_path)
        
        precompile.run()
        # 执行完以后, 向 .ninja_log 中插入 tag, 标记下一次编译的开始
        ninja = ninja_util.NinjaUtil(build_dir=self._p4_config["WORKDIR"], executable=self._ninja_exe_path)
        ninja.insert_flag_to_ninja_log(self._ninja_log_path)

    
    
    def run_compile_cache_submit_plugin(self, 
                                     build_command: str, 
                                     build_workdir: str, 
                                     build_executor: Callable[[str], bool],
                                     p4_ignore_url: str) -> bool:                                                                
        '''
        运行 compile_cache_submit_plugin 入口函数
        Args:
            build_command (str): 需要执行的、完整的编译命令字符串    
            build_workdir (str): 执行编译命令时需要进入的工作目录。
            build_executor (Callable[[str], bool]): 一个用于执行命令的函数。
                                                    它接收一个命令字符串作为参数，返回一个布尔值表示成功或失败。
            p4_ignore_url (str): .p4ignore 文件的下载 URL。   
        '''
        try:
            # 准备插件所需的 repo_info。
            for repo_dict in self._repo_config:
                for repo_name, repo_config in repo_dict.items():
                    repo_config["local_path"] = self._local_repo_dir[repo_name]
            
            compile_plugin = compilecachesubmit_plugin.CompileCacheSubmit(
                repo_info=self._repo_config,
                mr_target_commit_id=self._mr_target_commit_id,
                build_command=build_command,
                build_workdir=build_workdir,
                build_executor=build_executor,
                p4_config=self._p4_config
            )
            if not compile_plugin.run_build_phase():
                self._logger.error("因编译阶段失败，工作流终止。")
                return False
            
            self.create_diff_ninja_log()
            diff_log_path = self.get_diff_ninja_log()
            self._logger.info(f"流程成功完成。差异日志路径: {diff_log_path}")
            if not diff_log_path:
                self._logger.error("因生成或获取差异日志失败，工作流终止。")
                return False
            
            if not compile_plugin.run_submit_phase(diff_ninja_log_path=diff_log_path, p4_ignore_url=p4_ignore_url):
                self._logger.error("因缓存提交阶段失败，工作流终止。")
                return False

            self._logger.info("缓存生成与提交全部成功完成！")
            return True
        
        except Exception as e:
            # 捕获任何未预料的异常，确保流程不会崩溃。
            self._logger.error(f"执行 '编译并生成差异日志' 流程时发生未知异常: {e}", exc_info=True)
            return False
    
    
    
        
    def run_postcompile_plugin(self):
        '''
        执行完编译后, 生成并获取 .diff_ninja_log
        '''
        self.create_diff_ninja_log()
        return self.get_diff_ninja_log()
        # 执行完以后, 向 .ninja_log 中插入 tag, 标记下一次编译的开始
        ninja = ninja_util.NinjaUtil(build_dir=self._p4_config["WORKDIR"], executable=self._ninja_exe_path)
        ninja.insert_flag_to_ninja_log(self._ninja_log_path)

         
        
if __name__ == "__main__":
    blaze_cache = BlazeCache(product_name="lark", build_dir="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64",
                             os_type="dawin", task_type="ci_check_task", branch_type="main",
                             machine_id="1234", ninja_exe_path="/Users/bytedance/Desktop/lark/depot_tools/ninja",
                             mr_target_branch="m131")
    # blaze_cache.create_diff_ninja_log()
    blaze_cache._logger.info(blaze_cache.get_diff_ninja_log())
        
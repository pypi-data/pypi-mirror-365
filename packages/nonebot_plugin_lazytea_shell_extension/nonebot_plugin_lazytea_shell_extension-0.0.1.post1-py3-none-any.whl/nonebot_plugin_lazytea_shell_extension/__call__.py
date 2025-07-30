from nonebot_plugin_lazytea.sdk import SDK_nb
from nonebot import logger
from .config import _config, Config


@SDK_nb.Server.register_handler("nonebot_plugin_lazytea_shell_extension")
async def handle_change(new_config: Config):
    """配置热重载支持"""
    _config.enable_tea_perm = new_config.enable_tea_perm
    _config.tea_perm_allowance = new_config.tea_perm_allowance
    logger.success("已成功重载配置文件, 无需手动重启")

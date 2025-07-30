from nonebot import get_plugin_config
from pydantic import BaseModel, Field
from typing import Set


class Config(BaseModel):
    enable_tea_perm: bool = Field(
        default=True, description="是否启用LazyTea的命令式权限管理")
    tea_perm_allowance: Set[str] = Field(
        default_factory=set, description="允许谁使用命令管理权限")


_config = get_plugin_config(Config)
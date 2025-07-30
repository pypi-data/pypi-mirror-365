from .config import _config, Config
import asyncio
from arclet.alconna import Alconna, Args, CommandMeta, AllParam
from typing import List, Dict, Any, Optional, Tuple

from nonebot import logger, require
from nonebot.matcher import Matcher, matchers, current_bot, current_event
from nonebot.adapters import Bot, Event
from nonebot.message import _check_matcher
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_lazytea")
from nonebot_plugin_alconna import AlconnaMatch, Match, on_alconna, AlconnaMatcher, command_manager  # noqa
from nonebot_plugin_lazytea.utils.roster.model import MatcherInfo, RuleData  # noqa
from nonebot_plugin_lazytea.ipc.func_call import get_matchers, sync_matchers  # noqa
from nonebot_plugin_lazytea import _icon_path  # noqa

__plugin_meta__ = PluginMetadata(
    name="LazyTea命令拓展",
    description="允许通过命令管理LazyTea",
    usage=(
        "/tea status [指令] - 查看指令状态\n"
        "/tea on [指令] - 开启指令\n"
        "/tea off [指令] - 关闭指令\n"
        "/tea wl add/rm user/group [ID] [指令] - 管理白名单\n"
        "/tea bl add/rm user/group [ID] [指令] - 管理黑名单"
    ),
    type="application",
    homepage="https://github.com/hlfzsi/nonebot_plugin_lazytea_shell_extension",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_lazytea", "nonebot_plugin_alconna"),
    extra={
        "author": "hlfzsi",
        "version": "0.0.1",
        "icon_abspath": _icon_path,
        "ui_support": True
    }
)

_perm_lock = asyncio.Lock()


async def find_matched_matchers(bot: Bot, event: Event, command: str) -> List[type[Matcher]]:
    matched_list: List[type[Matcher]] = []
    processed_matchers: set[type[Matcher]] = set()

    for alc in command_manager.get_commands():
        try:
            parse_result = alc.parse(command)
            if parse_result.matched:
                if matcher_ref := alc.meta.extra.get("matcher"):
                    if matcher_class := matcher_ref():
                        if matcher_class not in processed_matchers:
                            logger.debug(
                                f"命令 '{command}' [通过 Alconna 解析] 成功匹配到 Matcher: "
                                f"{matcher_class.plugin_name}:{matcher_class.module_name}"
                            )
                            matched_list.append(matcher_class)
                            processed_matchers.add(matcher_class)
        except Exception as e:
            logger.trace(f"Alconna 解析命令 '{command}' 时出错: {e}")

    try:
        ConcreteMessage = event.get_message().__class__
        new_message = ConcreteMessage(command)
        update_fields = {"message": new_message,
                         "raw_message": str(new_message)}
        new_event = event.model_copy(update=update_fields)
    except Exception:
        return matched_list

    for priority in sorted(matchers.keys()):
        for matcher_class in matchers[priority]:
            if matcher_class in processed_matchers or issubclass(matcher_class, AlconnaMatcher):
                continue

            state: Dict[Any, Any] = {}
            bot_token = current_bot.set(bot)
            event_token = current_event.set(new_event)
            is_match = False
            try:
                is_match = await _check_matcher(
                    Matcher=matcher_class, bot=bot, event=new_event, state=state,
                    stack=None, dependency_cache={}
                )
            except Exception as e:
                logger.trace(
                    f"模拟检查 Matcher '{matcher_class.plugin_name}:{matcher_class.module_name}' 时出错: {e}")
            finally:
                current_bot.reset(bot_token)
                current_event.reset(event_token)

            if is_match:
                logger.debug(
                    f"命令 '{command}' [通过模拟检查] 成功匹配到 Matcher: "
                    f"{matcher_class.plugin_name}:{matcher_class.module_name}"
                )
                if matcher_class not in processed_matchers:
                    matched_list.append(matcher_class)
                    processed_matchers.add(matcher_class)

    return matched_list


async def get_target_matcher_info(bot: Bot, event: Event, command_str: str) -> Tuple[Optional[MatcherInfo], Optional[str]]:
    if not command_str:
        return None, "目标指令不能为空！"

    found_matchers = await find_matched_matchers(bot, event, command_str)

    if not found_matchers:
        return None, f"未找到任何可以处理指令 '{command_str}' 的处理器。"

    if len(found_matchers) > 1:
        names = "、".join(
            [f"{m.plugin_name or '未知'}:{m.module_name or '未知'}" for m in found_matchers])
        logger.warning(f"指令 '{command_str}' 匹配到多个处理器: {names}。将默认操作第一个。")

    target_matcher_class = found_matchers[0]
    plugin_name = target_matcher_class.plugin_name

    if not plugin_name:
        return None, "错误：无法确定目标指令所属的插件，因为它没有名称。"

    try:
        rule_data = RuleData.extract_rule(target_matcher_class())
    except Exception as e:
        return None, f"提取指令规则时出错: {e}"

    rule_hash = hash(rule_data)

    model = await get_matchers()
    bot_plugins = model.bots.get(bot.self_id)
    if not bot_plugins:
        return None, "错误：在权限模型中未找到当前 Bot 的数据。"

    plugin_matchers = bot_plugins.plugins.get(plugin_name)
    if not plugin_matchers:
        return None, f"错误：在权限模型中未找到插件 '{plugin_name}' 的数据。"

    target_matcher_info = plugin_matchers.rule_mapping.get(rule_hash)
    if not target_matcher_info:
        return None, "错误：在已存储的权限模型中找不到该具体指令。请尝试重启或同步UI。"

    return target_matcher_info, None


def format_matcher_info(info: MatcherInfo) -> str:
    """将 MatcherInfo 对象格式化为字符串"""
    status = "🟢 开启" if info.is_on else "🔴 关闭"

    def format_list(items):
        if not items:
            return "    无"
        return "\n".join(f"  - {item}" for item in items)

    return (
        f"指令状态: {status}\n"
        "──────────────────\n"
        "白名单用户:\n"
        f"{format_list(info.permission['white_list']['user'])}\n"
        "白名单群组:\n"
        f"{format_list(info.permission['white_list']['group'])}\n"
        "黑名单用户:\n"
        f"{format_list(info.permission['ban_list']['user'])}\n"
        "黑名单群组:\n"
        f"{format_list(info.permission['ban_list']['group'])}"
    )


async def update_model_and_reply(matcher: Matcher, message: str):
    model = await get_matchers()
    await sync_matchers(model.model_dump_json())
    await matcher.send(message)

tea_simple_cmd = on_alconna(
    Alconna(
        "/tea",
        Args["action", ["status", "on", "off"]]["target_cmd", AllParam],
        meta=CommandMeta(description="LazyTea 指令状态管理")
    ),
)

tea_list_cmd = on_alconna(
    Alconna(
        "/tea",
        Args["list_type", ["wl", "bl"]]["op", ["add", "rm"]]["scope",
                                                             ["user", "group"]]["id", str]["target_cmd", AllParam],
        meta=CommandMeta(description="LazyTea 指令名单管理")
    ),
)


@tea_simple_cmd.handle()
async def handle_tea_simple(
    matcher: AlconnaMatcher,
    bot: Bot,
    event: Event,
    action: Match[str] = AlconnaMatch("action"),
    target_cmd: Match[tuple] = AlconnaMatch("target_cmd")
):
    logger.debug("进入tea命令处理流程")
    if event.get_user_id() not in _config.tea_perm_allowance or not _config.enable_tea_perm:
        logger.debug("用户权限不足")
        return
    logger.debug(f"用户 {event.get_user_id()} 使用命令管理权限 (simple cmd)")

    async with _perm_lock:
        action_str = action.result
        target_cmd_tuple = target_cmd.result or ()
        target_cmd_str = " ".join(map(str, target_cmd_tuple)).strip()

        info, error_msg = await get_target_matcher_info(bot, event, target_cmd_str)
        if error_msg:
            await matcher.finish(error_msg)
        assert info is not None

        if action_str == "status":
            await matcher.send(f"查询成功！指令 '{target_cmd_str}' 的当前权限信息如下：\n{format_matcher_info(info)}")
            return

        if action_str == "on":
            if info.is_on:
                await matcher.finish(f"操作失败：指令 '{target_cmd_str}' 已经是「开启」状态了。")
            info.is_on = True
            await update_model_and_reply(matcher, f"操作成功！已将指令 '{target_cmd_str}' 的状态设置为「开启」。")
            return

        if action_str == "off":
            if not info.is_on:
                await matcher.finish(f"操作失败：指令 '{target_cmd_str}' 已经是「关闭」状态了。")
            info.is_on = False
            await update_model_and_reply(matcher, f"操作成功！已将指令 '{target_cmd_str}' 的状态设置为「关闭」。")
            return


@tea_list_cmd.handle()
async def handle_tea_list(
    matcher: AlconnaMatcher,
    bot: Bot,
    event: Event,
    list_type: Match[str] = AlconnaMatch("list_type"),
    op: Match[str] = AlconnaMatch("op"),
    scope: Match[str] = AlconnaMatch("scope"),
    target_id_match: Match[str] = AlconnaMatch("id"),
    target_cmd: Match[tuple] = AlconnaMatch("target_cmd")
):
    if event.get_user_id() not in _config.tea_perm_allowance or not _config.enable_tea_perm:
        return
    logger.debug(f"用户 {event.get_user_id()} 使用命令管理权限 (list cmd)")

    async with _perm_lock:
        list_type_str = list_type.result
        op_str = op.result
        scope_str = scope.result
        target_id = target_id_match.result
        target_cmd_tuple = target_cmd.result or ()
        target_cmd_str = " ".join(map(str, target_cmd_tuple)).strip()

        info, error_msg = await get_target_matcher_info(bot, event, target_cmd_str)
        if error_msg:
            await matcher.finish(error_msg)
        assert info is not None

        perm_list_name = "white_list" if list_type_str == "wl" else "ban_list"
        scope_cn = {"user": "用户", "group": "群组"}[scope_str]
        list_cn = {"wl": "白名单", "bl": "黑名单"}[list_type_str]

        perm_set = set(info.permission[perm_list_name][scope_str])

        if op_str == "add":
            if target_id in perm_set:
                await matcher.finish(f"操作失败：{scope_cn} {target_id} 已存在于{list_cn}中。")
            perm_set.add(target_id)
            reply_msg = f"操作成功！已将 {scope_cn} {target_id} 添加到指令 '{target_cmd_str}' 的{list_cn}。"
        else:  # op == "rm"
            if target_id not in perm_set:
                await matcher.finish(f"操作失败：{scope_cn} {target_id} 不在指令 '{target_cmd_str}' 的{list_cn}中。")
            perm_set.remove(target_id)
            reply_msg = f"操作成功！已将 {scope_cn} {target_id} 从指令 '{target_cmd_str}' 的{list_cn}中移除。"

        info.permission[perm_list_name][scope_str] = frozenset(perm_set)

        await update_model_and_reply(matcher, reply_msg)

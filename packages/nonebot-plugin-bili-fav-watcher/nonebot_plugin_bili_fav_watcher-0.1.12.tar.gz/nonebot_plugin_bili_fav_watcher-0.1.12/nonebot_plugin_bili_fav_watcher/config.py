from nonebot import get_driver, get_plugin_config

from pydantic import BaseModel, Field

driver = get_driver()

config = driver.config


class ScopedConfig(BaseModel):
    command_priority: int = 50
    interval_between_runs: int = 60
    new_video_threshold: int = 120
    cache_cleanup_threshold: int = 180
    sleep_interval: int = 5

    sessdata: str = ""
    bili_jct: str = ""
    buvid3: str = ""
    dedeuserid: str = ""
    ac_time_value: str = ""


class Config(BaseModel):
    bili_fav_watcher: ScopedConfig = Field(default_factory=ScopedConfig)


plugin_config = get_plugin_config(Config)


BILI_FAV_WATCHER_PRIORITY: int = plugin_config.bili_fav_watcher.command_priority
INTERVAL_BETWEEN_RUNS: int = plugin_config.bili_fav_watcher.interval_between_runs  # 遍历间隔
NEW_VIDEO_THRESHOLD: int = plugin_config.bili_fav_watcher.new_video_threshold  # 判定阈值
CACHE_CLEANUP_THRESHOLD: int = plugin_config.bili_fav_watcher.cache_cleanup_threshold  # 清理阈值
SLEEP_INTERVAL: int = plugin_config.bili_fav_watcher.sleep_interval  # 等待时间

SESSDATA: str = plugin_config.bili_fav_watcher.sessdata  # B站SESSDATA
BILI_JCT: str = plugin_config.bili_fav_watcher.bili_jct
BUVID3: str = plugin_config.bili_fav_watcher.buvid3
DEDEUSERID: str = plugin_config.bili_fav_watcher.dedeuserid
AC_TIME_VALUE: str = plugin_config.bili_fav_watcher.ac_time_value

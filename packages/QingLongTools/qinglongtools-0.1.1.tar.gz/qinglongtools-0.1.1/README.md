# QLapi

QLapi 是一个用于青龙面板的 Python 异步 API 封装库。

## 安装

```bash
pip install QLapi
```

## 使用

```python
import asyncio
from QLapi.ql import ql_api
from QLapi.ql_env import qlenv
from QLapi.ql_config import qlconfig
# 导入其他您需要使用的异步类

async def main():
    # 实例化 ql_api，使用异步工厂方法 create
    # 请替换为您的实际面板信息
    ql = await ql_api.create(
        url="您的青龙面板IP",
        port=5700, # 您的面板端口
        client_id="您的client_id",
        client_secret="您的client_secret"
    )

    print("青龙面板连接成功！", ql.s.headers)

    # 示例：使用 qlenv 获取环境变量列表
    ql_env_instance = qlenv("您的青龙面板IP", 5700, "您的client_id", "您的client_secret")
    ql_env_instance.s = ql.s # 共享同一个 httpx.AsyncClient 实例
    envs = await ql_env_instance.list()
    print("环境变量列表:", envs)

    # 示例：使用 qlconfig 获取配置文件列表
    ql_config_instance = qlconfig("您的青龙面板IP", 5700, "您的client_id", "您的client_secret")
    ql_config_instance.s = ql.s # 共享同一个 httpx.AsyncClient 实例
    configs = await ql_config_instance.list()
    print("配置文件列表:", configs)

    # 确保在程序结束时关闭 httpx 客户端
    await ql.s.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

## 模块

- `ql.py`: 基础 API 认证和 HTTP 客户端。
- `ql_config.py`: 配置文件管理。
- `ql_dependence.py`: 依赖管理。
- `ql_env.py`: 环境变量管理。
- `ql_log.py`: 日志管理。
- `ql_script.py`: 脚本管理。
- `ql_system.py`: 系统信息和更新。
- `ql_task.py`: 定时任务管理。

## 贡献

欢迎贡献！请提交 Pull Request 或 Issues。

## 许可证

本项目使用 MIT 许可证。

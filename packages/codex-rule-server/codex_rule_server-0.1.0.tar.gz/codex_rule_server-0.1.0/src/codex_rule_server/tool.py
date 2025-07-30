import os
import shutil
import zipfile
import requests
import uuid
import json
import asyncio
from xml.etree import ElementTree as ET
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.types as types

# 配置常量
JFROG_METADATA_URL = "https://jfrog.pangutech.dev/artifactory/libs-release-local/com/venustech/taihe/pangu/ai-friendly/maven-metadata.xml"
JFROG_BASE_URL = "https://jfrog.pangutech.dev:443/artifactory/libs-release-local/com/venustech/taihe/pangu/ai-friendly"

# 创建MCP server实例
server = Server("ai-code-rules")


def fetch_latest_version():
    """获取最新版本号"""
    try:
        res = requests.get(JFROG_METADATA_URL, timeout=30)
        res.raise_for_status()
        xml_root = ET.fromstring(res.text)
        return xml_root.findtext(".//latest")
    except Exception as e:
        raise Exception(f"Failed to fetch latest version: {str(e)}")


def download_and_extract(version: str, target_dir: str):
    """下载并解压指定版本的ai-friendly"""
    try:
        url = f"{JFROG_BASE_URL}/{version}/ai-friendly-{version}.zip"
        zip_path = os.path.join(target_dir, f"ai-friendly-{version}.zip")

        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

        os.remove(zip_path)
    except Exception as e:
        raise Exception(f"Failed to download and extract: {str(e)}")


def detect_project_type(root_dir: str) -> str:
    """
    检测项目类型，返回详细的项目信息供大模型判断
    """
    project_info = {
        "files": [],
        "directories": [],
        "indicators": {
            "frontend": [],
            "backend": [],
            "other": []
        }
    }

    # 检查根目录下的文件和目录
    if os.path.exists(root_dir):
        for item in os.listdir(root_dir):
            item_path = os.path.join(root_dir, item)
            if os.path.isfile(item_path):
                project_info["files"].append(item)
            elif os.path.isdir(item_path):
                project_info["directories"].append(item)

    # 前端项目指标
    frontend_indicators = [
        'package.json', 'yarn.lock', 'package-lock.json',
        'vite.config.ts', 'vite.config.js',
        'webpack.config.js', 'webpack.config.ts',
        'vue.config.js', 'nuxt.config.js',
        'next.config.js', 'angular.json',
        'index.html', 'tsconfig.json',
        '.babelrc', 'babel.config.js'
    ]

    # 后端项目指标
    backend_indicators = [
        'pom.xml', 'build.gradle', 'gradle.properties',
        'requirements.txt', 'Pipfile', 'poetry.lock',
        'go.mod', 'Cargo.toml', 'composer.json',
        'Gemfile', 'Dockerfile', 'docker-compose.yml',
        'application.yml', 'application.properties'
    ]

    # 检查指标
    for file in project_info["files"]:
        if file in frontend_indicators:
            project_info["indicators"]["frontend"].append(file)
        elif file in backend_indicators:
            project_info["indicators"]["backend"].append(file)
        else:
            project_info["indicators"]["other"].append(file)

    # 检查常见目录结构
    frontend_dirs = ['src', 'public', 'dist', 'build', 'node_modules', 'assets', 'components']
    backend_dirs = ['src/main/java', 'src/main/resources', 'target', 'build', 'bin', 'lib']

    for dir_name in project_info["directories"]:
        if dir_name in frontend_dirs:
            project_info["indicators"]["frontend"].append(f"dir:{dir_name}")
        elif dir_name in backend_dirs or dir_name.startswith('src'):
            project_info["indicators"]["backend"].append(f"dir:{dir_name}")

    return json.dumps(project_info, indent=2)


def merge_md_files(md_files, header_file=None, output_file=None):
    """合并多个md文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as out:
            if header_file and os.path.exists(header_file):
                with open(header_file, 'r', encoding='utf-8') as f:
                    out.write(f.read() + "\n\n")

            for md in md_files:
                if os.path.exists(md):
                    with open(md, 'r', encoding='utf-8') as f:
                        out.write(f.read() + "\n\n")
    except Exception as e:
        raise Exception(f"Failed to merge md files: {str(e)}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="rule_builder",
            description="根据IDE类型和规则扩展在工程根目录生成对应工具或插件的规则文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "ide": {
                        "type": "string",
                        "description": "插件类型，包括trae、cursor、codex、lingma等",
                        "enum": ["trae", "cursor", "codex", "lingma"]
                    },
                    "rule_ext": {
                        "type": "string",
                        "description": "rack名称，可选参数",
                        "default": None
                    },
                    "root_dir": {
                        "type": "string",
                        "description": "工程根目录路径",
                        "default": "."
                    },
                    "project_type": {
                        "type": "string",
                        "description": "项目类型：frontend 或 backend。如果不指定，大模型自行去判断是前端还是后端项目，若判断失败则默认为后端",
                        "enum": ["frontend", "backend"],
                        "default": None
                    }
                },
                "required": ["ide"]
            }
        ),
        types.Tool(
            name="rule_cleaner",
            description="根据IDE类型清除工程根目录下.{ide}/rules目录",
            inputSchema={
                "type": "object",
                "properties": {
                    "ide": {
                        "type": "string",
                        "description": "插件类型，包括trae、cursor、codex、lingma等",
                        "enum": ["trae", "cursor", "codex", "lingma"]
                    },
                    "root_dir": {
                        "type": "string",
                        "description": "工程根目录路径",
                        "default": "."
                    }
                },
                "required": ["ide"]
            }
        ),
        types.Tool(
            name="generate_ai_spec",
            description="根据rack名称在对应pangu-store/pangu-rack-{rack}生成规范文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "rack": {
                        "type": "string",
                        "description": "rack名称"
                    },
                    "root_dir": {
                        "type": "string",
                        "description": "工程根目录路径",
                        "default": "."
                    }
                },
                "required": ["rack"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool calls.
    Tools can modify server state and notify the client of changes.
    """
    try:
        if name == "rule_builder":
            ide = arguments.get("ide")
            rule_ext = arguments.get("rule_ext")
            root_dir = arguments.get("root_dir", ".")
            project_type = arguments.get("project_type", "auto")

            # 验证参数
            if not ide:
                raise ValueError("ide parameter is required")

            if not os.path.exists(root_dir):
                raise ValueError(f"Root directory does not exist: {root_dir}")

            # 获取最新版本并下载
            version = fetch_latest_version()
            extract_dir = f"/tmp/ai-friendly-{uuid.uuid4().hex}"
            os.makedirs(extract_dir, exist_ok=True)

            try:
                download_and_extract(version, extract_dir)

                # 创建规则目录
                rule_dir = os.path.join(root_dir, f".{ide}", "rules")
                os.makedirs(rule_dir, exist_ok=True)

                # 头部文件
                ide_header = os.path.join(extract_dir, "llms", "ides", f"{ide}.md")
                rules_dir = os.path.join(extract_dir, "llms", "rules")

                is_frontend = project_type == "frontend"
                filenames = []
                if is_frontend:
                    filenames.append("frontend-standards.md")
                else:
                    filenames += [
                        "config-standards.md", "controller-standards.md", "core-standards.md",
                        "database-standards.md", "project-structure.md", "service-standards.md"
                    ]

                md_files = [os.path.join(rules_dir, f) for f in filenames]

                # 添加rack特定规则
                if rule_ext:
                    rack_dir = os.path.join(extract_dir, f"pangu-store/pangu-rack-{rule_ext}/llms/rules")
                    if os.path.exists(rack_dir):
                        for file in os.listdir(rack_dir):
                            if file.endswith(".md"):
                                md_files.append(os.path.join(rack_dir, file))

                # 确定输出文件名
                output_file = os.path.join(rule_dir, f"project_rules.mdc" if ide == "cursor" else "project_rules.md")

                # 合并文件
                merge_md_files(md_files, header_file=ide_header, output_file=output_file)

                return [types.TextContent(
                    type="text",
                    text=f"Successfully generated rules for {ide} in {output_file}. Project type detected as: {'frontend' if is_frontend else 'backend'}"
                )]

            finally:
                # 清理临时目录
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)

        elif name == "rule_cleaner":
            ide = arguments.get("ide")
            root_dir = arguments.get("root_dir", ".")

            if not ide:
                raise ValueError("ide parameter is required")

            rule_path = os.path.join(root_dir, f".{ide}", "rules")
            if os.path.exists(rule_path):
                shutil.rmtree(rule_path)
                return [types.TextContent(
                    type="text",
                    text=f"Successfully cleaned rules directory: {rule_path}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Rules directory does not exist: {rule_path}"
                )]

        elif name == "generate_ai_spec":
            rack = arguments.get("rack")
            root_dir = arguments.get("root_dir", ".")

            if not rack:
                raise ValueError("rack parameter is required")

            if not os.path.exists(root_dir):
                raise ValueError(f"Root directory does not exist: {root_dir}")

            # 获取最新版本并下载
            version = fetch_latest_version()
            extract_dir = f"/tmp/ai-spec-{uuid.uuid4().hex}"
            os.makedirs(extract_dir, exist_ok=True)

            try:
                download_and_extract(version, extract_dir)

                src_dir = os.path.join(extract_dir, "llms", "prompts")
                dest_dir = os.path.join(root_dir, f"pangu-store/pangu-rack-{rack}")
                os.makedirs(dest_dir, exist_ok=True)

                copied_files = []
                if os.path.exists(src_dir):
                    for file in os.listdir(src_dir):
                        if file.endswith(".md"):
                            src_file = os.path.join(src_dir, file)
                            dest_file = os.path.join(dest_dir, file)
                            shutil.copy(src_file, dest_file)
                            copied_files.append(file)

                return [types.TextContent(
                    type="text",
                    text=f"Successfully generated AI spec for rack '{rack}' in {dest_dir}. Copied files: {', '.join(copied_files)}"
                )]

            finally:
                # 清理临时目录
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ai-code-rules",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
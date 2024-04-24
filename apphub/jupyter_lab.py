import os
from pathlib import Path

import gradio as gr
from apphub.app import App, AppOption
from apphub.helper import generate_random_token


class JupyterLab(App):

    @property
    def key(self):
        return "jupyter_lab"

    @property
    def port(self):
        return 10000

    @property
    def op_port(self):
        return 10001

    @property
    def name(self):
        return "JupyterLab"

    class JupyterLabOption(AppOption):
        conda_env: str = "base"
        work_dir: str = "/home/featurize"
        token: str = ""
        query: str = ""

    cfg: JupyterLabOption

    def render_installation_page(self) -> "gr.Blocks":
        """这个方法定义了如何渲染安装页面，这个页面会展示给用户，让用户安装应用

        页面使用 Gradio 来渲染，所以这里只需要返回一个 Gradio 的 Blocks 对象即可
        """
        with gr.Blocks() as demo:
            # 首选可以渲染一些 Markdown 文本，用于介绍应用
            gr.Markdown(
                """# 安装 JupyterLab

Featurize 官方 JupyterLab 应用
"""
            )
            install_location = self.render_install_location(allow_work=True)
            conda_env = self.render_conda_env_selector()
            work_dir = gr.Textbox(
                value="/home/featurize",
                label="工作目录",
                info="JupyterLab 的工作目录，可以理解为左侧文件树的根目录",
            )
            self.render_installation_button(
                inputs=[install_location, conda_env, work_dir]
            )
            self.render_log()
        return demo

    def installation(self, install_location, conda_env, work_dir):
        self.cfg.token = generate_random_token()
        self.cfg.query = f"token={self.cfg.token}"
        super().installation(install_location, conda_env, work_dir)
        with self.conda_activate(conda_env):
            self.execute_command(f"pip install {(Path(__file__).parent.parent / "workspace-0.1.0.tar.gz").as_posix()}")
        self.app_installed()

    def start(self):
        """安装完成后，应用并不会立即开始运行，而是调用这个 start 函数。"""
        with self.conda_activate(self.cfg.conda_env):
            self.execute_command(
                f"""jupyter lab \
--ServerApp.token='{self.cfg.token}' \
--ip='0.0.0.0' \
--port={self.port} \
--no-browser \
--allow-root \
--ServerApp.allow_origin='*' \
--ServerApp.tornado_settings="{{'headers': {{'Content-Security-Policy': 'frame-ancestors self {os.environ["FEATURIZE_INSTANCE_SHORT_ID"]}.app.featurize.cn *.app.featurize.cn'}} }}"
""",
                daemon=True,
                cwd=self.cfg.work_dir,
            )
        self.app_started()

    def close(self):
        """关闭应用的逻辑"""
        super().close()

    def uninstall(self):
        """卸载应用会调用该方法"""
        super().uninstall()


def main():
    return JupyterLab()

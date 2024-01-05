import json
import os
import subprocess

import wx

# 获取当前工作目录工作目录
current_dir = os.getcwd()
# 拼接配置文件路径
config_path = os.path.join(current_dir, '_internal', 'config')


# 使用 wxpyhton 写一个带有一个文件选择框两个输入框的页面
def get_config(key):
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        conf = json.loads(content)
        return conf[key]
    except KeyError:
        return ''
    except FileNotFoundError:
        return ''


def set_config(key, val):
    # 读取配置文件
    try:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            conf = json.loads(content)
        except FileNotFoundError:
            conf = {}

        conf[key] = val

        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(str(json.dumps(conf, ensure_ascii=False)))

        return True
    except FileNotFoundError:
        return False


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='签名工具')
        max_width = 400
        # 设置窗口
        self.SetSize((max_width + 30, 350))
        # 设置窗口背景色
        self.SetBackgroundColour('white')

        # 创建apksigner选择框
        self.apksigner_chooser = wx.DirPickerCtrl(self, style=wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST,
                                                  size=(max_width, -1))

        # 监听apksigner_chooser选择完成
        self.apksigner_chooser.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_apksigner_chooser_changed)

        # 读取配置
        self.apksigner_chooser.SetPath(get_config('apksigner_path'))

        # 创建APK选择框
        self.apk_chooser = wx.FilePickerCtrl(self, style=wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST,
                                             wildcard="*.apk",
                                             size=(max_width, -1))

        # 创建签名文件选择框 后缀为*.jks
        self.sign_chooser = wx.FilePickerCtrl(self, style=wx.FLP_DEFAULT_STYLE | wx.FLP_FILE_MUST_EXIST,
                                              wildcard="*.jks",
                                              size=(max_width, -1))
        # 监听self.sign_chooser选择完成
        self.sign_chooser.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_sign_choose)

        self.sign_chooser.SetPath(get_config('sign_path'))

        s_w = int(max_width / 3) - 2
        # 创建签名密码输入框
        self.store_pwd = wx.TextCtrl(self, value="", size=(s_w, -1))
        if self.sign_chooser.GetPath() != "":
            self.store_pwd.SetValue(get_config(self.sign_chooser.GetPath() + 'store_p'))

        # 创建别名输入框
        self.alias_name = wx.TextCtrl(self, value="", size=(s_w, -1))
        if self.sign_chooser.GetPath() != "":
            self.alias_name.SetValue(get_config(self.sign_chooser.GetPath() + 'alias_n'))

        # 创建别名密码输入框
        self.alias_pwd = wx.TextCtrl(self, value="", size=(s_w, -1))
        if self.sign_chooser.GetPath() != "":
            self.alias_pwd.SetValue(get_config(self.sign_chooser.GetPath() + 'alias_p'))

        # 创建一个布局管理器
        layout = wx.BoxSizer(wx.VERTICAL)

        # 将文件选择框和输入框添加到布局管理器中
        layout.Add(wx.StaticText(self, label="选择apksigner路径"), 0, wx.ALL, 5)
        layout.Add(self.apksigner_chooser, 0, wx.ALL, 5)
        layout.Add(wx.StaticText(self, label="选择APK"), 0, wx.ALL, 5)
        layout.Add(self.apk_chooser, 0, wx.ALL, 5)
        layout.Add(wx.StaticText(self, label="选择签名文件"), 0, wx.ALL, 5)
        layout.Add(self.sign_chooser, 0, wx.ALL, 5)

        # 创建一个水平布局管理器
        h_layout = wx.BoxSizer(wx.HORIZONTAL)
        # 创建一个垂直布局管理器
        v_layout = wx.BoxSizer(wx.VERTICAL)
        v_layout.Add(wx.StaticText(self, label="StorePassword"), 0, wx.ALL, 5)
        v_layout.Add(self.store_pwd, 1, wx.ALL, 0)
        h_layout.Add(v_layout, 1, wx.ALL, 2)

        v_layout = wx.BoxSizer(wx.VERTICAL)
        v_layout.Add(wx.StaticText(self, label="KeyAlias"), 0, wx.ALL, 5)
        v_layout.Add(self.alias_name, 1, wx.ALL, 0)
        h_layout.Add(v_layout, 1, wx.ALL, 2)

        v_layout = wx.BoxSizer(wx.VERTICAL)
        v_layout.Add(wx.StaticText(self, label="KeyPassword"), 0, wx.ALL, 5)
        v_layout.Add(self.alias_pwd, 1, wx.ALL, 0)
        h_layout.Add(v_layout, 1, wx.ALL, 2)

        layout.Add(h_layout, 1, wx.ALL, 3)

        # 创建一个重新签名按钮
        sign_btn = wx.Button(self, label='重新签名')
        layout.Add(sign_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # 监听sign_btn点击
        sign_btn.Bind(wx.EVT_BUTTON, self.on_sign_btn_click)

        # 设置布局管理器
        self.SetSizer(layout)

    # 监听文件选择完成事件
    def on_apksigner_chooser_changed(self, event):
        # 持久化self.apksigner_chooser值
        apksigner_chooser_value = self.apksigner_chooser.GetPath()
        set_config('apksigner_path', apksigner_chooser_value)

    # 监听文件选择完成事件
    def on_sign_choose(self, event):
        # 获取选择的签名文件路径
        sign_path = self.sign_chooser.GetPath()
        set_config('sign_path', sign_path)

    #  监听重新签名按钮点击事件
    def on_sign_btn_click(self, event):
        # 跳转到指定路径
        apksigner_path = self.apksigner_chooser.GetPath()
        # 判断apksigner_path是否空字符串
        if apksigner_path == "":
            # 弹窗提示
            wx.MessageBox("请选择apksigner路径", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        os.chdir(apksigner_path)

        # 获取sign_chooser路径
        sign_path = self.sign_chooser.GetPath()
        # 获取选择的APK文件路径
        apk_path = self.apk_chooser.GetPath()
        # 获取APK所在的文件夹
        apk_folder = os.path.dirname(apk_path)
        # 获取APK文件名
        apk_name = os.path.basename(apk_path)
        # 拼接新的路径标记为singed
        signed_apk_path = os.path.join(apk_folder, "signed-" + apk_name)

        # 获取store_pwd值
        store_p = self.store_pwd.GetValue()
        # 获取alias_name值
        alias_n = self.alias_name.GetValue()
        # 获取alias_pwd值
        alias_p = self.alias_pwd.GetValue()

        result = subprocess.run(
            f"apksigner sign --ks {sign_path} --ks-key-alias {alias_n} --ks-pass pass:{store_p} --ks-pass pass:{alias_p} --out {signed_apk_path} {apk_path}",
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            # 保存签名密码和别名
            set_config(sign_path + 'store_p', store_p)
            set_config(sign_path + 'alias_n', alias_n)
            set_config(sign_path + 'alias_p', alias_n)
            wx.MessageBox("签名成功！", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("签名失败：\n" + result.stderr.decode('gbk'), "提示", wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

# smart_unpack

自动化 Electron-egg/Node/Electron 项目包解包和源码还原工具

## 功能特点

- 支持 `.asar`、`.zip`、`.tar(.gz)`、`.exe`（尝试提取 asar）的自动解包
- 支持目录输入（直接格式化代码）
- 解包后所有 js/ts/json/css/html 文件自动格式化，提升可读性
- 适用于 node、electron-egg、elecn-egg 构建包的源码还原/分析
- 结果统一输出到 `unpack_result/` 目录

## 使用方法

1. **安装依赖**

   请先安装 `asar`、`js-beautify`、`prettier`，可全局安装：

   ```bash
   npm install -g asar js-beautify prettier
   ```

2. **运行工具**

   ```bash
   python smart_unpack.py 你的包文件或目录
   ```

   - 支持 asar/zip/tar/exe/目录等多种输入格式
   - 结果自动输出到 `unpack_result`，不用担心覆盖源数据

3. **查看结果**

   - 所有源码已格式化处理，可直接用文本编辑器分析
   - `unpack_result/` 为解包总目录

## 支持的源码反混淆建议

如遇严重混淆/加密，可配合 [de4js](https://lelinhtinh.github.io/de4js/)、jsnice 等工具进一步还原。

## 免责声明

本脚本用于合法、学习和个人分析用途。请勿用于非法用途！

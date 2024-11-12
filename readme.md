# Realtime pressure feedback system

---

## Platform

Run in windows PC, and the project is programmed in Qt.

## Build

Build into .exe

```powershell
# Produce build directory and dist directory
# The app.exe is located inside the dist directory
# After building, **manually copy** the following directories into the dist directory to make the app.exe working
# conf, correction, font, img, log, Protocols, resource, translate
pyinstaller.exe --onefile main.py
```

## Packages

The hid package needs `hidapi` rather than `hid`.

## Develop diary

### 20241112

1. 改变了曲线反馈的延迟方式，现在只是延时，不进行滑窗平均；
2. 优化了界面布局，开始和结束按钮增加了（S）键提示；
3. 优化了操作逻辑，现在实验结束后，开始按钮和结束按钮的可用性自动切换了；
4. 优化了未选择反馈文件时的伪反馈线形状，现在是周期性的锯齿波形。

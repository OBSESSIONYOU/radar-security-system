# 合成演示数据

当前发布中的 28 张频谱风格图、演示事件和 CSV 均由 `scripts/generate_synthetic_demo.py` 的数学公式与固定随机种子 684001 生成，没有读取真实 ADC、人员记录或历史图片。

事件分数仅用于演示界面；未进行模型训练、推理速度测试或真实识别评估。Accuracy、拒识率等实测性能字段设为 null；真实采集数为 0。不要将演示图或分数作为论文、验收或实际安防性能的证据。

重建方式（在独立 Python 环境中安装 `requirements-demo.txt`）：

```powershell
python -m pip install -r requirements-demo.txt
python scripts/generate_synthetic_demo.py
```

来源清单及生成文件 SHA-256 见 `data/synthetic-provenance.json`。重新生成后应审查实际差异，再提交；扫描器仍检查数据文件和密钥。

替换前的旧发布版本已保存在维护者本机的 DPAPI 加密恢复副本中。此次使用正常 Git 提交替换当前文件，旧版本仍存在于 Git 历史及可能的平台缓存中；来源或公开授权未获确认，不应恢复为当前展示数据。

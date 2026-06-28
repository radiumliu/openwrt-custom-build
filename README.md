# OpenWrt Custom Build

基于 OpenWrt 24.10 的 x86_64 自定义固件。

## 变更

| 操作 | 包名 |
|------|------|
| ➕ 新增 | easytier, luci-app-homeproxy |
| ➖ 移除 | gost + luci-app-gost, luci-app-passwall2, cshark (云鲨) + luci-app-cshark |
| 🔧 默认 IP | 192.168.0.223/22 (从 192.168.0.1/22 改) |

其余包与原固件一致，包括：
- 双 WAN (PPPoE) + mwan3
- xray-core, sing-box, shadowsocks-rust, shadowsocksr-libev, naiveproxy, hysteria, tuic-client
- mosdns + chinadns-ng
- socat, ttyd, lucky, upnp, wol, qos, eqos, filemanager, advanced-reboot, vlmcsd
- collectd + rrdtool 统计
- 所有 x86_64 网卡驱动 (r8169, e1000e, igb, ixgbe, tg3, bnx2...)

## 使用

### 1. Fork 到你的 GitHub

创建一个 GitHub 仓库，把本目录内容 push 上去。

```bash
cd openwrt-custom-build
git init
git add .
git commit -m "Initial OpenWrt custom build config"
git remote add origin git@github.com:你的用户名/openwrt-custom-build.git
git push -u origin main
```

### 2. 触发构建

- push 到 main 分支会自动触发构建
- 也可以在 GitHub 页面上 **Actions → Build OpenWrt Custom Firmware → Run workflow** 手动触发

### 3. 下载固件

构建完成后（约 1-2 小时），在 Actions 页面的 Artifacts 区域下载：
- `openwrt-x86-64-custom` — 包含全部编译产物

### 4. 刷机

下载后解压，找到以下文件（用哪个取决于你的引导方式）：

| 文件 | 说明 |
|------|------|
| `generic-ext4-combined.img.gz` | **推荐** — 完整磁盘镜像，用 `dd` 或 BalenaEtcher 写入硬盘/SSD |
| `generic-ext4-rootfs.img.gz` | 根文件系统（不含引导），适合已有分区布局的升级 |

刷写：

```bash
# 解压
gunzip openwrt-*-generic-ext4-combined.img.gz

# 写入硬盘（确认 /dev/sdX 是目标盘！）
dd if=openwrt-*-generic-ext4-combined.img of=/dev/sda bs=4M status=progress

# 重启路由器，默认 IP: 192.168.0.223
```

> ⚠️ 刷机后需要重新配置双 WAN 的 PPPoE 账号密码和 mwan3 策略

## 文件说明

```
.github/workflows/build-openwrt.yml   # GitHub Actions 构建流程
feeds/feeds.conf.append                # 自定义 feeds（easytier + kenzok8）
config.seed                            # 构建配置（包选择）
files/etc/config/network               # 默认网络配置 (192.168.0.223/22)
```

## 注意事项

1. 首次构建约需 1-2 小时（下载源码 + 编译），后续由于缓存会快很多
2. 构建产物自带的 `sha256sums` 文件可用于验证文件完整性
3. 如需其他调整，修改 `config.seed` 后再 push 即可自动重新构建

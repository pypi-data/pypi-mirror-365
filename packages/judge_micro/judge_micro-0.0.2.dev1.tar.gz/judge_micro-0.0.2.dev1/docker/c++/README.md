# 配置驅動 OJ 微服務 (C++ 版本)

一個現代化的線上評測系統，基於 C++ 實現，支援純函數式介面，完全基於配置文件驅動，無需修改任何核心代碼。

## ✨ 特色

- 🚀 **零代碼修改**：harness.cpp 永遠不需要修改
- 🎯 **純函數式**：用戶函數無需處理全局變數
- 📝 **配置驅動**：只需修改 config.json 即可定義新題目
- ⚡ **自動編譯**：自動生成測試代碼並編譯執行
- 📊 **詳細報告**：包含性能測量、錯誤檢測、結果驗證
- 🔧 **靈活參數**：支援任意數量的函數參數和類型
- 💻 **現代 C++**：使用 C++17 標準，類型安全，RAII 管理
- 🛡️ **錯誤處理**：完善的異常處理和報告機制
- 🔍 **模板支持**：支援泛型函數和類型推導

## 🏗️ 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用戶代碼      │    │   配置文件      │    │   評測引擎      │
│   user.cpp      │    │   config.json   │    │   harness.cpp   │
│   solve()函數   │ -> │   solve_params  │ -> │   動態生成      │
│   純函數接口    │    │   types         │    │   編譯執行      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       v
                                              ┌─────────────────┐
                                              │   結果報告      │
                                              │   result.json   │
                                              │   性能統計      │
                                              │   錯誤檢測      │
                                              └─────────────────┘
```

## 🛠️ 環境需求

- **編譯器**: GCC 7+ 或 Clang 5+ (支援 C++17 標準)
- **函式庫**: nlohmann/json 函式庫
- **系統**: Linux/Unix 環境
- **工具**: Make 或 CMake (用於自動化)

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install g++ nlohmann-json3-dev make

# 或者使用包含的 single header 版本
# 不需要額外安裝，項目已包含 json.hpp
```

## 🚀 快速開始

### 方法一：使用演示腳本（推薦新手）

```bash
# 運行完整演示
./demo.sh
```

### 方法二：手動步驟

#### 步驟 1：編譯 harness

```bash
# 基本編譯
g++ -std=c++17 harness.cpp -o harness

# 或使用 Makefile（推薦）
make build
```

#### 步驟 2：創建配置文件

創建 `config.json`（支援語言版本參數）：

```json
{
  "solve_params": [
    {"name": "a", "type": "int", "input_value": 3},
    {"name": "b", "type": "int", "input_value": 4}
  ],
  "expected": {"a": 6, "b": 9},
  "function_type": "int",
  "cpp_standard": "c++20",
  "compiler_flags": "-Wall -Wextra -O2"
}
```

**新增支援的語言版本參數：**
- `cpp_standard`：指定 C++ 標準 (c++11, c++14, c++17, c++20, c++23)
- `compiler_flags`：自定義編譯器標誌

#### 測試語言版本

```bash
# 測試不同 C++ 標準
make test-cpp20   # 使用 C++20
make test-cpp23   # 使用 C++23

# 使用自定義配置
make test-config CONFIG_FILE=config_cpp20.json
```

#### 步驟 3：實現用戶函數

創建 `user.cpp`：

```cpp
#include <iostream>
#include "solve.hpp"

int solve(int &a, int &b) {
    std::cout << "Hello from user.cpp!" << std::endl;
    std::cout << "Input: a=" << a << ", b=" << b << std::endl;
    a = a * 2;    // a: 3 -> 6
    b = b + 5;    // b: 4 -> 9
    std::cout << "Output: a=" << a << ", b=" << b << std::endl;
    return 0;     // 返回 0 表示成功
}
```

#### 步驟 4：運行評測

```bash
./harness config.json result.json
```

#### 步驟 5：查看結果

```bash
cat result.json
```

## 📋 配置文件詳解

### 基本配置結構

```json
{
  "solve_params": [
    {
      "name": "參數名稱",
      "type": "參數類型",
      "input_value": "初始值"
    }
  ],
  "expected": {
    "參數名": "期望值"
  },
  "function_type": "返回類型",
  "timeout_ms": 5000,
  "memory_limit_mb": 512
}
```

### 支援的數據類型

- **整數類型**: `int`, `long`, `long long`
- **浮點類型**: `float`, `double`
- **字符類型**: `char`, `string`
- **布爾類型**: `bool`
- **容器類型**: `vector<int>`, `vector<string>` 等
- **自定義類型**: 支援用戶定義的結構體

### 配置範例

#### 範例 1：基本數學運算
```json
{
  "solve_params": [
    {"name": "x", "type": "int", "input_value": 5},
    {"name": "y", "type": "int", "input_value": 3}
  ],
  "expected": {"x": 8, "y": 2},
  "function_type": "void"
}
```

對應的用戶函數：
```cpp
void solve(int &x, int &y) {
    x = x + y;  // 5 + 3 = 8
    y = x - y;  // 8 - 3 = 5, 但期望是 2，這會顯示錯誤
}
```

#### 範例 2：字符串處理
```json
{
  "solve_params": [
    {"name": "str", "type": "string", "input_value": "hello"},
    {"name": "len", "type": "int", "input_value": 0}
  ],
  "expected": {"str": "HELLO", "len": 5},
  "function_type": "bool"
}
```

對應的用戶函數：
```cpp
bool solve(std::string &str, int &len) {
    for (auto &c : str) {
        c = std::toupper(c);
    }
    len = str.length();
    return true;
}
```

#### 範例 3：容器操作
```json
{
  "solve_params": [
    {"name": "nums", "type": "vector<int>", "input_value": [1, 2, 3, 4, 5]},
    {"name": "sum", "type": "int", "input_value": 0}
  ],
  "expected": {"nums": [2, 4, 6, 8, 10], "sum": 30},
  "function_type": "void"
}
```

對應的用戶函數：
```cpp
void solve(std::vector<int> &nums, int &sum) {
    for (auto &num : nums) {
        num *= 2;
        sum += num;
    }
}
```

## 🔧 進階功能

### 性能測量

系統自動測量：
- **執行時間**: 毫秒級精度
- **CPU 時間**: 用戶態和系統態分別統計
- **內存使用**: 峰值記憶體使用量
- **編譯時間**: 編譯階段耗時

### 錯誤處理

支援多種錯誤檢測：
- **編譯錯誤**: 語法錯誤、型別錯誤等
- **運行時錯誤**: 分段錯誤、異常拋出等
- **邏輯錯誤**: 輸出與期望不符
- **超時錯誤**: 執行時間超過限制
- **內存錯誤**: 內存使用超過限制

### 結果輸出格式

```json
{
  "status": "SUCCESS|COMPILE_ERROR|RUNTIME_ERROR|TIMEOUT|WRONG_ANSWER",
  "stdout": "程序輸出",
  "stderr": "錯誤信息",
  "time_ms": 123.45,
  "cpu_utime": 0.1,
  "cpu_stime": 0.05,
  "maxrss_mb": 15.2,
  "compile_time_ms": 567.89,
  "expected": {"a": 6, "b": 9},
  "actual": {"a": 6, "b": 8},
  "match": false
}
```

## 🧪 範例題目

項目包含多個預設範例：

- **config_basic.json**: 基本數學運算
- **config_string.json**: 字符串處理
- **config_vector.json**: 容器操作
- **config_advanced.json**: 複雜數據結構
- **config_algorithm.json**: 演算法實現

每個範例都有對應的用戶代碼和期望結果。

## 🚧 使用限制

1. **函數簽名**: 用戶函數必須符合配置文件定義
2. **返回類型**: 目前支援基本類型的返回值
3. **參數類型**: 參數必須是引用類型以支援修改
4. **標頭檔**: 必須包含對應的 C++ 標準庫頭文件

## 🔍 故障排除

### 常見問題

1. **編譯失败**
   - 檢查 C++ 標準版本 (需要 C++17)
   - 確認包含正確的頭文件
   - 檢查函數簽名是否與配置匹配

2. **運行時錯誤**
   - 檢查數組邊界
   - 避免空指針解引用
   - 確保異常處理正確

3. **結果不匹配**
   - 檢查演算法邏輯
   - 確認數據類型轉換
   - 查看標準輸出調試信息

### 調試技巧

```cpp
// 使用標準輸出進行調試
std::cout << "Debug: x = " << x << std::endl;

// 使用斷言檢查條件
#include <cassert>
assert(x > 0);

// 異常處理
try {
    // 可能出錯的代碼
} catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << std::endl;
}
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 項目
2. 創建功能分支
3. 提交變更
4. 推送到分支
5. 創建 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 🔗 相關項目

- [C 語言版本](../c/README.md) - 原始 C 語言實現
- [Python 版本](../python/README.md) - Python 實現版本
- [線上評測系統](https://github.com/example/oj-system) - 完整的 OJ 系統

---

**配置驅動 OJ 微服務 C++ 版本** - 讓程式競賽更簡單、更優雅！ 🏆

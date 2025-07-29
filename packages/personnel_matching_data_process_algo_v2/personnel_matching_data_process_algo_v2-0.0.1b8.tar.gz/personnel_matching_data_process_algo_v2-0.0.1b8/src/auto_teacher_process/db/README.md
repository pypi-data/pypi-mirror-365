# 数据库处理模块 README

## 模块结构
```
db/
├── config/                                 # 配置文件目录
│   ├── db_config.yaml                      # 数据库连接配置
│   └── teacher_level.json                  # 教师级别配置
├── services/                               # 核心服务模块
│   ├── db_insert_dedup.py                  # 去重数据插入
│   ├── db_insert_famous_projects.py        # 知名项目插入
│   ├── db_insert_host_project.py           # 主持项目插入
│   ├── db_insert_html.py                   # HTML数据插入
│   ├── db_insert_infos.py                  # 基本信息插入
│   ├── db_insert_name.py                   # 姓名数据插入
│   ├── db_insert_relation.py               # 关系数据插入
│   ├── db_insert_teacher_level.py          # 教师级别插入
│   └── db_update_infos.py                  # 信息更新服务
├── test/                                   # 单元测试模块
│   ├── test_db_insert_dedup.py             # 去重插入测试
│   ├── test_db_insert_famous_projects.py   # 知名项目测试
│   ├── test_db_insert_host_project.py      # 主持项目测试
│   ├── test_db_insert_html.py              # HTML插入测试
│   ├── test_db_insert_infos.py             # 基本信息测试
│   ├── test_db_insert_name.py              # 姓名插入测试
│   ├── test_db_insert_relation.py          # 关系数据测试
│   ├── test_db_insert_teacher_level.py     # 教师级别测试
│   └── test_db_update_infos.py             # 信息更新测试
├── README.md                               # 本说明文档
├── es_operator.py                          # es数据库操作类
└── db_base.py                              # 数据库处理基类
```

## 配置说明
### config/db_config.yaml
```yaml
db:
  host: "localhost"     # 数据库主机
  port: 33046           # 数据库端口
  user: "root"          # 数据库用户名
  password: "password"  # 数据库密码
  database: "test"      # 数据库名称
  db_url: "mysql+pymysql://root:password@localhost/test" # 数据库连接URL
```

## 核心服务
### 基础功能类
`BaseDBProcessor` 提供以下基础能力：
- 数据库连接池管理
- 批量数据插入/更新/删除
- 数据查询
- 获取文件夹下所有文件路径
- 事务处理
- 错误重试机制
- 进度跟踪日志

### 服务模块规范
所有服务模块继承`BaseDBProcessor`并实现：
```python
class XxxProcessor(BaseDBProcessor):
    def process(self, input_data: dict) -> None:
        """核心处理逻辑"""
```

## 使用示例
```python
# 初始化姓名插入处理器
processor = NameInsertProcessor()

# 准备输入数据
input_data = {
    'province': '广东省',
    'file_dir': '/data/teachers/'
}

# 执行处理
processor.run(input_data)

# 查看日志输出处理进度
```

## 测试指南
运行单元测试：
```bash
# 在项目根目录执行
export PYTHONPATH=$(pwd)
pytest -v -s auto_teacher_process/db/test/
```

测试覆盖功能：
- 姓名数据插入
- 去重数据处理
- 知名项目插入
- 主持项目处理
- HTML数据解析
- 基本信息更新
- 教师级别处理
- 关系数据插入

## 开发规范
1. 新增服务模块需继承`BaseDBProcessor`
2. 实现`process()`方法处理核心逻辑
3. 使用`self.logger`记录处理进度
4. 批量操作使用`self.insert_db()`方法
5. 数据库连接配置统一管理
6. 新增服务需同步添加单元测试
7. 重要操作需添加事务支持
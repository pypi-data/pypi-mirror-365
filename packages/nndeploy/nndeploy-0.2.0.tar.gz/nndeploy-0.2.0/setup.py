import sys
from setuptools import setup, find_packages
import os
import shutil


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False

except ImportError:
    bdist_wheel = None


if sys.version_info < (3, 0):
    sys.exit("Sorry, Python < 3.0 is not supported")


def parse_requirements(fname='requirements.txt', with_version=True):
    """
    Parse the package dependencies listed in a file but strips specific
    versioning information.

    Args:
        fname (str): path to the file
        with_version (bool, default=False): if True include version specs

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    import re
    import sys
    from os.path import exists
    require_fpath = fname

    def parse_line(line):
        """Parse information from a line in a requirements text file."""
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            elif '@git+' in line:
                info['package'] = line
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip,
                                                     rest.split(';'))
                        info['platform_deps'] = platform_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get('platform_deps')
                    if platform_deps is not None:
                        parts.append(';' + platform_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


# 读取长描述
def read_long_description():
    """读取 README.md 文件作为长描述"""
    readme_path = "README.md"
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"警告：无法读取 {readme_path}: {e}")
    
    # 如果无法读取 README，使用默认描述
    return """
You can get everything in nndeploy github main page : [nndeploy](https://github.com/nndeploy/nndeploy)
"""


# def get_internal_so_path():
#     import importlib

#     suffixes = importlib.machinery.EXTENSION_SUFFIXES
#     loader = importlib.machinery.ExtensionFileLoader
#     lazy_loader = importlib.util.LazyLoader.factory(loader)
#     finder = importlib.machinery.FileFinder("nndeploy", (lazy_loader, suffixes))
#     spec = finder.find_spec("_nndeploy_internal")
#     pathname = spec.origin
#     assert os.path.isfile(pathname)
#     return os.path.basename(pathname)


# package_data = {"nndeploy": [get_internal_so_path()]}

def get_internal_so_path():
    import os
    import glob
    import platform
    import subprocess

    # 定义搜索路径
    search_path = "nndeploy"
    
    # 根据不同平台设置文件扩展名
    if platform.system() == "Windows":
        extensions = [".dll", ".pyd"]
    elif platform.system() == "Darwin":
        extensions = [".dylib", ".so"]
    else:  # Linux and others
        extensions = [".so"]  # 添加.so.*以匹配带版本号的动态库
        
    # 检查目录是否存在
    if not os.path.exists(search_path):
        raise FileNotFoundError(f"目录 {search_path} 不存在")
        
    # 查找所有动态库文件
    all_matches = []
    for ext in extensions:
        pattern = os.path.join(search_path, f"*{ext}*")  # 添加*以匹配带版本号的后缀
        matches = glob.glob(pattern)
        all_matches.extend(matches)
    
    if not all_matches:
        raise FileNotFoundError(f"在 {search_path} 目录下未找到动态库文件")
        
    # 打印找到的所有动态库文件
    print(f"在 {search_path} 目录下找到以下动态库文件:")
    for match in all_matches:
        print(f"  {os.path.basename(match)}")
        
    # 在Linux和macOS上建立动态库链接关系
    if platform.system() != "Windows":
        for lib_path in all_matches:
            try:
                # 使用ldd/otool查看依赖关系
                if platform.system() == "Darwin":
                    cmd = ["otool", "-L", lib_path]
                else:
                    cmd = ["ldd", lib_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                # print(f"\n{os.path.basename(lib_path)}的依赖关系:")
                # print(result.stdout)
                
                # 设置rpath
                if platform.system() == "Darwin":
                    subprocess.run(["install_name_tool", "-add_rpath", "@loader_path", lib_path])
                else:
                    subprocess.run(["patchelf", "--set-rpath", "$ORIGIN", lib_path])
            except Exception as e:
                print(f"警告: 处理{lib_path}时出错: {e}")
                
    # 返回所有动态库文件名列表
    return [os.path.basename(match) for match in all_matches]


def get_package_data():
    """获取需要打包的数据文件"""
    # 直接使用 get_internal_so_path() 返回的列表
    so_files = get_internal_so_path()
    
    # 确保返回一个字典，其值为一个简单的字符串列表
    package_data = {
        "nndeploy": so_files  # 这里 so_files 已经是一个字符串列表了
    }
    
    print(f"package_data: {package_data}")
    return package_data

# 基础依赖包
install_requires = [
    'cython',  # Cython编译
    'packaging',  # 包管理
    'setuptools',  # 安装工具
    'gitpython>=3.1.30',  # Git操作
    'aiofiles>=24.1.0',  # 异步文件操作
    'PyYAML>=5.3.1',  # YAML解析
    'pytest',  # 测试框架
    'jsonschema',  # JSON Schema验证
    'multiprocess',  # 多进程支持
    'numpy',  # 数值计算
    'opencv-python>=4.8.0',  # 图像处理
]

# 检测CUDA是否可用以及版本
def get_cuda_version():
    """检测系统中的CUDA版本"""
    try:
        # 方法1: 尝试通过nvidia-smi获取CUDA版本
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            # 从nvidia-smi输出中提取CUDA版本
            lines = result.stdout.split('\n')
            for line in lines:
                if 'CUDA Version:' in line:
                    version = line.split('CUDA Version:')[1].strip().split()[0]
                    # 移除小数点,例如 "11.8" -> "118"
                    version_str = version.replace('.','')
                    return version_str
    except:
        pass
    
    try:
        # 方法2: 尝试导入torch检测CUDA
        import torch
        if torch.cuda.is_available():
            # 获取CUDA版本,例如 "11.8" 
            version = torch.version.cuda
            if version:
                # 移除小数点,例如 "118"
                version_str = version.replace('.','')
                return version_str
    except ImportError:
        pass
    except Exception:
        pass
    
    try:
        # 方法3: 检查CUDA环境变量
        import os
        cuda_home = os.environ.get('CUDA_HOME') or os.environ.get('CUDA_PATH')
        if cuda_home and os.path.exists(cuda_home):
            # 尝试从路径中提取版本信息
            version_file = os.path.join(cuda_home, 'version.txt')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    content = f.read()
                    # 查找版本号模式
                    import re
                    match = re.search(r'CUDA Version (\d+\.\d+)', content)
                    if match:
                        version = match.group(1)
                        version_str = version.replace('.','')
                        return version_str
    except:
        pass
    
    return None

cuda_version = get_cuda_version()

# 根据CUDA版本添加对应的依赖包
if cuda_version:
    print(f"检测到CUDA版本: {cuda_version}")
    install_requires.extend([
        'torch>=2.0.0',  # PyTorch(GPU版本)
        'torchvision>=0.15.0',  # torchvision(GPU版本)
        'onnxruntime-gpu>=1.18.0',  # ONNX Runtime GPU版本
    ])
else:
    print("未检测到CUDA，使用CPU版本依赖")
    install_requires.extend([
        'torch>=2.0.0',  # PyTorch(CPU版本)
        'torchvision>=0.15.0',  # torchvision(CPU版本)
        'onnxruntime>=1.18.0',  # ONNX Runtime CPU版本
    ])

# 添加服务器相关依赖
server_requires = [
    'requests>=2.31.0',  # 请求库
    'fastapi>=0.104.0',  # Web框架
    'uvicorn>=0.24.0',  # ASGI服务器
    'websockets>=11.0',  # WebSocket支持
    'python-multipart>=0.0.6',  # 文件上传支持
    'pydantic>=2.0.0',  # 数据验证
]

install_requires.extend(server_requires)

print(f"最终依赖列表: {install_requires}")

# 执行拷贝，将../server目录拷贝到nndeploy/目录中
def copy_server_directory():
    """将../server目录拷贝到nndeploy/目录中"""
    source_dir = "../server"
    target_dir = "nndeploy/server"
    
    # 需要包含的文件和目录
    include_items = {"__pycache__", "frontend"}
    
    if os.path.exists(source_dir):
        # 如果目标目录存在，先删除
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 手动拷贝文件和目录
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            
            if os.path.isdir(source_path):
                # 如果是目录且在包含列表中
                if item in include_items:
                    shutil.copytree(source_path, target_path)
                    print(f"已拷贝目录: {item}")
                else:
                    print(f"跳过目录: {item}")
            else:
                # 如果是Python文件，直接拷贝
                if item.endswith('.py'):
                    shutil.copy2(source_path, target_path)
                    print(f"已拷贝Python文件: {item}")
                else:
                    print(f"跳过文件: {item}")
        
        # 在nndeploy/server目录下创建resources目录
        resources_dir = os.path.join(target_dir, "resources")
        os.makedirs(resources_dir, exist_ok=True)
        print(f"已创建resources目录: {resources_dir}")
        
        print(f"已成功将 {source_dir} 中的Python文件、__pycache__文件夹、frontend文件夹拷贝到 {target_dir}")
    else:
        print(f"源目录 {source_dir} 不存在")

# 执行拷贝操作
copy_server_directory()
setup(
    name="nndeploy",
    version="0.2.0",  # 修复版本号格式
    author="nndeploy team",
    author_email="595961667@qq.com",  # 添加邮箱
    description="Workflow-based Multi-platform AI Deployment Tool",  # 添加简短描述
    long_description=read_long_description(),  # 添加长描述
    long_description_content_type="text/markdown",  # 指定内容类型为 Markdown
    url="https://github.com/nndeploy/nndeploy",  # 添加项目URL
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    license='Apache License 2.0',
    python_requires=">=3.8",
    packages=find_packages(),
    package_dir={"nndeploy": "nndeploy"},
    # package_data=package_data,
    package_data=get_package_data(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'nndeploy-run-json=nndeploy.dag.run_json:main',
            'nndeploy-app=nndeploy.server.app:main',
        ],
    },
    # extras_require={
    #     "all": parse_requirements('../requirements.txt')
    # },
    cmdclass={"bdist_wheel": bdist_wheel},
    keywords="deep-learning, neural-network, model-deployment, inference, ai",
    project_urls={
        "Bug Reports": "https://github.com/nndeploy/nndeploy/issues",
        "Source": "https://github.com/nndeploy/nndeploy",
    },
)

"""Cross-platform wrapper for the antiword utility to extract text from MS Word documents."""
import os
import subprocess
import platform
import chardet
from .text_optimizer import optimize_text

ANTIWORD_SHARE = os.path.join(os.path.dirname(__file__), "antiword_share")

def get_antiword_binary():
    """Get the appropriate antiword binary path for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map platform.system() and platform.machine() to our binary directories
    if system == "windows":
        binary_dir = "win-amd64"
        binary_name = "antiword.exe"
    elif system == "linux":
        binary_dir = "linux-amd64"
        binary_name = "antiword"
    elif system == "darwin":
        if machine in ["arm64", "aarch64"]:
            binary_dir = "darwin-arm64"
        else:
            # macOS Intel (x86_64) - no dedicated binary available
            raise RuntimeError(
                f"不支持 macOS Intel (x86_64) 平台，请使用 ARM64 版本的 macOS"
            )
        binary_name = "antiword"
    else:
        raise RuntimeError(f"不支持的平台: {system} {machine}，目前仅支持 Windows、Linux 和 macOS ARM64")

    binary_path = os.path.join(os.path.dirname(__file__), "bin", binary_dir, binary_name)

    if not os.path.exists(binary_path):
        raise RuntimeError(
            f"找不到对应平台的 antiword 程序: {binary_path}，请检查安装是否完整"
        )

    return binary_path

def extract_text(doc_path, optimize_format=False):
    """Extract text from a Microsoft Word document using antiword.

    Args:
        doc_path (str): Path to the .doc file to extract text from.
        optimize_format (bool): Whether to optimize text formatting by merging
            lines without leading spaces. Defaults to False.

    Returns:
        str: The extracted text content from the document.

    Raises:
        FileNotFoundError: If the document file does not exist.
        ValueError: If the file is not a .doc format.
        RuntimeError: If the platform is not supported or binary is missing.
        subprocess.CalledProcessError: If antiword execution fails.
    """
    # 输入验证
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"文件不存在: {doc_path}")
    
    if not doc_path.lower().endswith('.doc'):
        raise ValueError("仅支持 .doc 格式文件，不支持 .docx 格式")
    
    antiword_binary = get_antiword_binary()
    env = os.environ.copy()
    env["ANTIWORDHOME"] = ANTIWORD_SHARE
    
    try:
        result = subprocess.run(
            [antiword_binary, doc_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=env
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "未知错误"
        raise RuntimeError(f"文档解析失败: {error_msg}")

    try:
        encoding = chardet.detect(result.stdout)['encoding'] or 'utf-8'
        text = result.stdout.decode(encoding, errors='replace')
    except Exception:
        text = result.stdout.decode('utf-8', errors='replace')
    
    if optimize_format:
        text = optimize_text(text)
    
    return text
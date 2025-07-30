
def read_file(file_path):
    """读取文件内容并返回"""
    with open(file_path, 'r') as f:
        return f.read()

def write_file(file_path, content):
    """将内容写入文件"""
    with open(file_path, 'w') as f:
        f.write(content)

def is_palindrome(s):
    """检查一个字符串是否是回文"""
    return s == s[::-1]

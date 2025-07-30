from .array import MyArray
import math

def add(arr1, arr2):
    """两个数组相加"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a + b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def subtract(arr1, arr2):
    """两个数组相减"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a - b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def multiply(arr1, arr2):
    """两个数组相乘"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a * b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def divide(arr1, arr2):
    """两个数组相除"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if arr1.shape != arr2.shape:
        raise ValueError("数组形状必须相同")
    
    result_data = [a / b for a, b in zip(arr1.data, arr2.data)]
    return MyArray(result_data)

def sum(arr):
    """计算数组元素的总和"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    return sum(arr.data)

def mean(arr):
    """计算数组元素的平均值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算平均值")
    
    return sum(arr.data) / arr.size

def min(arr):
    """计算数组的最小值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算最小值")
    
    return min(arr.data)

def max(arr):
    """计算数组的最大值"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算最大值")
    
    return max(arr.data)

def unique(arr):
    """返回数组中的唯一值（去重并排序）"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        return MyArray([])
    
    unique_data = sorted(set(arr.data))
    return MyArray(unique_data, dtype=arr.dtype)

def median(arr):
    """计算数组的中位数"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if arr.size == 0:
        raise ValueError("空数组无法计算中位数")
    
    sorted_data = sorted(arr.data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0
    else:
        return sorted_data[mid]
    
def dot(arr1, arr2):
    """计算两个数组的点积（矩阵乘法）"""
    if not isinstance(arr1, MyArray) or not isinstance(arr2, MyArray):
        raise TypeError("操作数必须是MyArray实例")
    
    if len(arr1.shape) != 2 or len(arr2.shape) != 2:
        raise ValueError("点积仅支持2D数组")
    
    rows1, cols1 = arr1.shape
    rows2, cols2 = arr2.shape
    
    if cols1 != rows2:
        raise ValueError(f"形状不兼容: {arr1.shape} 的列数与 {arr2.shape} 的行数不匹配")
    
    result_data = []
    for i in range(rows1):
        for j in range(cols2):
            sum_val = 0
            for k in range(cols1):
                sum_val += arr1.data[i * cols1 + k] * arr2.data[k * cols2 + j]
            result_data.append(sum_val)
    
    return MyArray(result_data, shape=(rows1, cols2))

def transpose(arr):
    """返回数组的转置"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    if len(arr.shape) == 1:
        # 1D数组转置仍为自身
        return MyArray(arr.data.copy(), shape=arr.shape)
    elif len(arr.shape) == 2:
        rows, cols = arr.shape
        transposed_data = []
        for j in range(cols):
            for i in range(rows):
                transposed_data.append(arr.data[i * cols + j])
        return MyArray(transposed_data, shape=(cols, rows))
    else:
        raise ValueError("仅支持1D和2D数组的转置")
    
def reshape(arr, new_shape):
    """重塑数组形状，新形状元素总数必须与原数组一致"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    new_size = 1
    for dim in new_shape:
        new_size *= dim
    
    if new_size != arr.size:
        raise ValueError(f"无法重塑为{new_shape}，元素总数不匹配（原{arr.size} vs 新{new_size}）")
    
    return MyArray(arr.data.copy(), shape=new_shape)

def variance(arr, ddof=0):
    """计算方差（ddof=0为总体方差，ddof=1为样本方差）"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    if arr.size == 0:
        raise ValueError("空数组无法计算方差")
    
    avg = mean(arr)
    squared_diff = [(x - avg) **2 for x in arr.data]
    return sum(squared_diff) / (arr.size - ddof)

def std(arr, ddof=0):
    """计算标准差（方差的平方根）"""
    return math.sqrt(variance(arr, ddof=ddof))

def cumsum(arr):
    """返回累积和数组"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    if arr.size == 0:
        return MyArray([])
    
    cum_data = []
    current = 0
    for x in arr.data:
        current += x
        cum_data.append(current)
    return MyArray(cum_data, shape=arr.shape)

def cumprod(arr):
    """返回累积乘积数组"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    if arr.size == 0:
        return MyArray([])
    
    cum_data = []
    current = 1
    for x in arr.data:
        current *= x
        cum_data.append(current)
    return MyArray(cum_data, shape=arr.shape)

def sort(arr, ascending=True):
    """对数组排序（返回新数组）"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    
    sorted_data = sorted(arr.data, reverse=not ascending)
    return MyArray(sorted_data, shape=arr.shape)

def trace(arr):
    """返回方阵的迹（主对角线元素之和）"""
    if not isinstance(arr, MyArray):
        raise TypeError("参数必须是MyArray实例")
    if len(arr.shape) != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("迹仅适用于方阵（2D且行数=列数）")
    
    total = 0
    rows, cols = arr.shape
    for i in range(rows):
        total += arr.data[i * cols + i]
    return total
"""
协议基类定义
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from typing import List


@dataclass
class ProviderConfig:
    """供应商配置"""
    base_url: str
    api_key: str
    default_models: Dict[str, str] = field(default_factory=dict)
    supported_protocols: List[str] = field(default_factory=list)


class Protocol(ABC):
    """协议基类"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    @abstractmethod
    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        文本到文本转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
        """
        pass
    
    @abstractmethod
    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> str:
        """
        文本到图像转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            size: 图像尺寸
            quality: 图像质量
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的图像文件路径
        """
        raise NotImplementedError("此协议未实现文本到图像转换功能")
    
    def text_to_audio(self, prompt: str, model: Optional[str] = None,
                      voice: str = "default", speed: float = 1.0,
                      save_path: Optional[str] = None) -> str:
        """
        文本到音频转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            voice: 语音名称
            speed: 语速
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的音频文件路径
        """
        raise NotImplementedError("此协议未实现文本到音频转换功能")
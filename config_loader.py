#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件加载器
处理配置文件的读取和验证
"""

import configparser
import os
from pathlib import Path


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_file="config.ini"):
        """
        初始化配置加载器
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
                print(f"✅ 加载配置文件: {self.config_file}")
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
                self._create_default_config()
        else:
            print(f"⚠️  配置文件不存在，创建默认配置: {self.config_file}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config.add_section('Detection')
        self.config.set('Detection', 'confidence', '0.5')
        self.config.set('Detection', 'model_selection', '1')
        
        self.config.add_section('Mosaic')
        self.config.set('Mosaic', 'mosaic_size', '20')
        self.config.set('Mosaic', 'intensity', '5')
        
        self.config.add_section('Processing')
        self.config.set('Processing', 'max_resolution', '1920')
        self.config.set('Processing', 'frame_skip', '0')
        self.config.set('Processing', 'enable_multithreading', 'false')
        
        self.config.add_section('Output')
        self.config.set('Output', 'image_quality', '95')
        self.config.set('Output', 'video_codec', 'mp4v')
        self.config.set('Output', 'verbose', 'true')
        
        self.config.add_section('Advanced')
        self.config.set('Advanced', 'face_padding', '0.1')
        self.config.set('Advanced', 'min_face_size', '30')
        
        # 保存默认配置
        self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            print(f"✅ 配置已保存: {self.config_file}")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def get_detection_config(self):
        """获取检测配置"""
        return {
            'confidence': self.config.getfloat('Detection', 'confidence'),
            'model_selection': self.config.getint('Detection', 'model_selection')
        }
    
    def get_mosaic_config(self):
        """获取马赛克配置"""
        return {
            'mosaic_size': self.config.getint('Mosaic', 'mosaic_size'),
            'intensity': self.config.getint('Mosaic', 'intensity')
        }
    
    def get_processing_config(self):
        """获取处理配置"""
        return {
            'max_resolution': self.config.getint('Processing', 'max_resolution'),
            'frame_skip': self.config.getint('Processing', 'frame_skip'),
            'enable_multithreading': self.config.getboolean('Processing', 'enable_multithreading')
        }
    
    def get_output_config(self):
        """获取输出配置"""
        return {
            'image_quality': self.config.getint('Output', 'image_quality'),
            'video_codec': self.config.get('Output', 'video_codec'),
            'verbose': self.config.getboolean('Output', 'verbose')
        }
    
    def get_advanced_config(self):
        """获取高级配置"""
        return {
            'face_padding': self.config.getfloat('Advanced', 'face_padding'),
            'min_face_size': self.config.getint('Advanced', 'min_face_size')
        }
    
    def get_all_config(self):
        """获取所有配置"""
        return {
            'detection': self.get_detection_config(),
            'mosaic': self.get_mosaic_config(),
            'processing': self.get_processing_config(),
            'output': self.get_output_config(),
            'advanced': self.get_advanced_config()
        }
    
    def update_config(self, section, key, value):
        """更新配置项"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, key, str(value))
            self.save_config()
            print(f"✅ 配置已更新: [{section}] {key} = {value}")
            return True
        except Exception as e:
            print(f"❌ 配置更新失败: {e}")
            return False
    
    def reset_config(self):
        """重置为默认配置"""
        self.config.clear()
        self._create_default_config()
        print("🔄 配置已重置为默认值")


def main():
    """测试配置加载器"""
    print("🧪 测试配置加载器")
    
    # 创建配置加载器
    loader = ConfigLoader()
    
    # 显示所有配置
    config = loader.get_all_config()
    print("\n📋 当前配置:")
    
    for section_name, section_config in config.items():
        print(f"\n[{section_name.upper()}]")
        for key, value in section_config.items():
            print(f"  {key}: {value}")
    
    # 测试配置更新
    print("\n🔧 测试配置更新...")
    loader.update_config('Mosaic', 'mosaic_size', 25)
    
    # 验证更新
    mosaic_config = loader.get_mosaic_config()
    print(f"✅ 更新后马赛克大小: {mosaic_config['mosaic_size']}")


if __name__ == "__main__":
    main() 
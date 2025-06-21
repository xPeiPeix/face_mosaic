#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸自动打马赛克工具
基于MediaPipe实现高精度人脸检测和自动马赛克处理
支持图片和视频处理，保留原始音频
"""

import cv2
import mediapipe as mp
import numpy as np
import argparse
import os
import sys
import tempfile
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tqdm import tqdm
from pathlib import Path

# 音频处理支持
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    print("⚠️  警告: ffmpeg-python 未安装，视频处理将不保留音频")



class FaceMosaicProcessor:
    """人脸马赛克处理器"""
    
    def __init__(self, confidence=0.5, mosaic_size=20, preserve_audio=True):
        """
        初始化处理器
        
        Args:
            confidence (float): 人脸检测置信度阈值
            mosaic_size (int): 马赛克块大小
            preserve_audio (bool): 是否保留音频
        """
        self.confidence = confidence
        self.mosaic_size = mosaic_size
        self.preserve_audio = preserve_audio and FFMPEG_AVAILABLE
        
        # 初始化MediaPipe人脸检测
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=1,  # 0为短距离模型，1为长距离模型
            min_detection_confidence=confidence
        )
    
    def has_audio_track(self, video_path):
        """
        检查视频是否包含音频轨道
        
        Args:
            video_path (str): 视频文件路径
            
        Returns:
            bool: 是否包含音频
        """
        if not FFMPEG_AVAILABLE:
            return False
        
        try:
            probe = ffmpeg.probe(video_path)
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            return len(audio_streams) > 0
        except Exception:
            return False
    
    def merge_video_audio(self, video_path, audio_path, output_path):
        """
        合并视频和音频
        
        Args:
            video_path (str): 处理后的视频路径
            audio_path (str): 原始音频路径
            output_path (str): 输出文件路径
            
        Returns:
            bool: 合并是否成功
        """
        if not FFMPEG_AVAILABLE:
            return False
        
        try:
            # 使用ffmpeg合并视频和音频
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)
            
            out = ffmpeg.output(
                video_input, audio_input, output_path,
                vcodec='copy', acodec='copy',
                **{'avoid_negative_ts': 'make_zero'}
            )
            ffmpeg.run(out, quiet=True, overwrite_output=True)
            return True
        except Exception as e:
            print(f"⚠️  音频合并失败: {e}")
            return False
    
    def extract_audio(self, video_path, audio_path):
        """
        从视频中提取音频
        
        Args:
            video_path (str): 视频文件路径
            audio_path (str): 音频输出路径
            
        Returns:
            bool: 提取是否成功
        """
        if not FFMPEG_AVAILABLE:
            return False
        
        try:
            stream = ffmpeg.input(video_path)
            out = ffmpeg.output(stream, audio_path, acodec='copy')
            ffmpeg.run(out, quiet=True, overwrite_output=True)
            return True
        except Exception:
            return False
    
    def find_video_files(self, folder_path):
        """
        查找文件夹中的所有视频文件（排除已处理文件）
        
        Args:
            folder_path (str): 文件夹路径
            
        Returns:
            list: 视频文件路径列表
        """
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        video_files = []
        
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return video_files
        
        for file_path in folder.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in video_extensions and 
                not file_path.stem.endswith('_processed')):
                video_files.append(str(file_path))
        
        return sorted(video_files)
    
    def generate_output_path(self, input_path):
        """
        生成输出文件路径（添加_processed后缀）
        
        Args:
            input_path (str): 输入文件路径
            
        Returns:
            str: 输出文件路径
        """
        path = Path(input_path)
        output_name = f"{path.stem}_processed{path.suffix}"
        return str(path.parent / output_name)
    
    def create_thread_safe_processor(self):
        """
        创建线程安全的处理器实例（用于并发处理）
        
        Returns:
            FaceMosaicProcessor: 新的独立处理器实例
        """
        return FaceMosaicProcessor(
            confidence=self.confidence,
            mosaic_size=self.mosaic_size,
            preserve_audio=self.preserve_audio
        )
    
    def process_single_video_wrapper(self, input_path, progress_callback=None, processor=None):
        """
        单个视频处理包装器，用于并发处理（线程安全）
        
        Args:
            input_path (str): 输入视频路径
            progress_callback (callable): 进度回调函数
            processor (FaceMosaicProcessor): 独立的处理器实例（用于线程安全）
            
        Returns:
            dict: 处理结果信息
        """
        # 如果没有提供独立处理器，使用当前实例（单线程模式）
        if processor is None:
            processor = self
            
        result = {
            'input_path': input_path,
            'output_path': None,
            'success': False,
            'error': None,
            'start_time': time.time(),
            'end_time': None,
            'processed_frames': 0,
            'detected_faces': 0
        }
        
        try:
            output_path = processor.generate_output_path(input_path)
            
            # 检查是否已存在输出文件
            if os.path.exists(output_path):
                result['success'] = True
                result['output_path'] = output_path
                result['error'] = "已跳过：文件已存在"
                result['end_time'] = time.time()
                return result
            
            # 使用独立处理器处理视频
            success = processor.process_video(input_path, output_path)
            
            result['success'] = success
            result['output_path'] = output_path if success else None
            result['end_time'] = time.time()
            
            if progress_callback:
                progress_callback(result)
                
        except Exception as e:
            result['error'] = str(e)
            result['end_time'] = time.time()
        
        return result
    
    def process_video_batch(self, folder_path, max_workers=4):
        """
        批量处理视频文件夹
        
        Args:
            folder_path (str): 输入文件夹路径
            max_workers (int): 最大并发工作线程数
            
        Returns:
            dict: 批量处理结果统计
        """
        print(f"🔍 扫描视频文件: {folder_path}")
        video_files = self.find_video_files(folder_path)
        
        if not video_files:
            print(f"❌ 未找到视频文件: {folder_path}")
            return {'success': False, 'message': '未找到视频文件'}
        
        print(f"📁 找到 {len(video_files)} 个视频文件")
        
        # 统计信息
        stats = {
            'total_files': len(video_files),
            'processed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'start_time': time.time(),
            'end_time': None,
            'results': []
        }
        
        # 进度锁
        progress_lock = Lock()
        
        def update_progress(result):
            with progress_lock:
                stats['results'].append(result)
                if result['success']:
                    if "已跳过" in str(result.get('error', '')):
                        stats['skipped_files'] += 1
                    else:
                        stats['processed_files'] += 1
                else:
                    stats['failed_files'] += 1
        
        print(f"🚀 开始批量处理，并发数: {max_workers}")
        print(f"🔧 线程安全模式：每个线程使用独立的MediaPipe检测器")
        
        # 为每个线程创建独立处理器的包装函数
        def process_with_independent_processor(video_path):
            # 创建线程独立的处理器实例
            thread_processor = self.create_thread_safe_processor()
            return self.process_single_video_wrapper(video_path, update_progress, thread_processor)
        
        # 使用ThreadPoolExecutor进行并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务，每个任务使用独立的处理器
            future_to_video = {
                executor.submit(process_with_independent_processor, video_path): video_path
                for video_path in video_files
            }
            
            # 使用主进度条监控整体进度
            with tqdm(total=len(video_files), desc="批量处理进度") as pbar:
                for future in as_completed(future_to_video):
                    video_path = future_to_video[future]
                    try:
                        result = future.result()
                        pbar.update(1)
                        
                        # 更新进度条描述
                        pbar.set_postfix({
                            "成功": stats['processed_files'],
                            "跳过": stats['skipped_files'], 
                            "失败": stats['failed_files']
                        })
                        
                    except Exception as e:
                        print(f"❌ 处理 {video_path} 时出错: {e}")
                        stats['failed_files'] += 1
                        pbar.update(1)
        
        stats['end_time'] = time.time()
        total_time = stats['end_time'] - stats['start_time']
        
        # 输出统计报告
        print("\n" + "="*60)
        print("📊 批量处理完成统计")
        print("="*60)
        print(f"📁 总文件数: {stats['total_files']}")
        print(f"✅ 成功处理: {stats['processed_files']}")
        print(f"⏭️  跳过文件: {stats['skipped_files']}")
        print(f"❌ 失败文件: {stats['failed_files']}")
        print(f"⏱️  总用时: {total_time:.2f} 秒")
        print(f"⚡ 平均速度: {stats['total_files']/total_time:.2f} 文件/秒")
        print("="*60)
        
        # 显示失败文件详情
        if stats['failed_files'] > 0:
            print("\n❌ 失败文件详情:")
            for result in stats['results']:
                if not result['success'] and "已跳过" not in str(result.get('error', '')):
                    print(f"  - {result['input_path']}: {result['error']}")
        
        return stats
    
    def apply_mosaic(self, image, x, y, w, h):
        """
        对指定区域应用马赛克效果
        
        Args:
            image: 输入图像
            x, y, w, h: 马赛克区域坐标和尺寸
            
        Returns:
            处理后的图像
        """
        # 确保坐标在图像范围内
        x, y = max(0, x), max(0, y)
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        if w <= 0 or h <= 0:
            return image
        
        # 提取要处理的区域
        roi = image[y:y+h, x:x+w]
        
        # 缩小再放大实现马赛克效果
        small_roi = cv2.resize(roi, (w//self.mosaic_size, h//self.mosaic_size), 
                              interpolation=cv2.INTER_LINEAR)
        mosaic_roi = cv2.resize(small_roi, (w, h), 
                               interpolation=cv2.INTER_NEAREST)
        
        # 将马赛克区域放回原图
        image[y:y+h, x:x+w] = mosaic_roi
        
        return image
    
    def detect_and_mosaic_faces(self, image):
        """
        检测人脸并应用马赛克
        
        Args:
            image: 输入图像
            
        Returns:
            tuple: (处理后的图像, 检测到的人脸数量)
        """
        # 转换颜色空间用于检测
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        face_count = 0
        
        if results.detections:
            h, w, _ = image.shape
            
            for detection in results.detections:
                # 获取边界框
                bbox = detection.location_data.relative_bounding_box
                
                # 转换为像素坐标
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                box_w = int(bbox.width * w)
                box_h = int(bbox.height * h)
                
                # 应用马赛克
                image = self.apply_mosaic(image, x, y, box_w, box_h)
                face_count += 1
        
        return image, face_count
    
    def process_image(self, input_path, output_path):
        """
        处理单张图片
        
        Args:
            input_path (str): 输入图片路径
            output_path (str): 输出图片路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 读取图像
            image = cv2.imread(input_path)
            if image is None:
                print(f"❌ 无法读取图像: {input_path}")
                return False
            
            # 检测并处理人脸
            processed_image, face_count = self.detect_and_mosaic_faces(image)
            
            # 保存结果
            cv2.imwrite(output_path, processed_image)
            print(f"✅ 处理完成: {input_path} -> {output_path} (检测到 {face_count} 张人脸)")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理图像时出错: {e}")
            return False
    
    def process_video(self, input_path, output_path):
        """
        处理视频文件，支持音频保留
              
        Args:
            input_path (str): 输入视频路径
            output_path (str): 输出视频路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 检查音频并准备临时文件
            has_audio = self.preserve_audio and self.has_audio_track(input_path)
            temp_dir = None
            temp_video_path = output_path
            temp_audio_path = None
            
            if has_audio:
                # 创建临时目录
                temp_dir = tempfile.mkdtemp(prefix="face_mosaic_")
                temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
                temp_audio_path = os.path.join(temp_dir, "temp_audio.aac")
                
                print(f"🎵 检测到音频轨道，将保留原始音频")
                # 提取音频
                if not self.extract_audio(input_path, temp_audio_path):
                    print(f"⚠️  音频提取失败，将仅处理视频")
                    has_audio = False
                    temp_video_path = output_path
            
            # 打开视频文件
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                print(f"❌ 无法打开视频: {input_path}")
                return False
            
            # 获取视频属性
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 设置视频编写器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
            
            print(f"🎬 开始处理视频: {input_path}")
            print(f"📊 视频信息: {width}x{height}, {fps}FPS, {total_frames}帧")
            
            processed_frames = 0
            total_faces = 0
            
            # 使用进度条处理视频
            with tqdm(total=total_frames, desc="处理视频帧") as pbar:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 处理当前帧
                    processed_frame, face_count = self.detect_and_mosaic_faces(frame)
                    total_faces += face_count
                    
                    # 写入输出视频
                    out.write(processed_frame)
                    processed_frames += 1
                    
                    # 更新进度条
                    pbar.update(1)
                    pbar.set_postfix({"检测人脸": total_faces})
            
            # 释放视频资源
            cap.release()
            out.release()
            
            # 合并音频（如果需要）
            if has_audio and temp_audio_path and os.path.exists(temp_audio_path):
                print(f"🔗 正在合并音频...")
                if self.merge_video_audio(temp_video_path, temp_audio_path, output_path):
                    print(f"✅ 音频合并成功")
                else:
                    print(f"⚠️  音频合并失败，复制纯视频文件")
                    shutil.copy2(temp_video_path, output_path)
            
            # 清理临时文件
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            print(f"✅ 视频处理完成: {output_path}")
            print(f"📈 统计信息: 处理 {processed_frames} 帧，检测到 {total_faces} 个人脸")
            if has_audio:
                print(f"🎵 音频已保留")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理视频时出错: {e}")
            # 清理临时文件
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False
    
    def process_directory(self, input_dir, output_dir):
        """
        批量处理目录中的图片
        
        Args:
            input_dir (str): 输入目录路径
            output_dir (str): 输出目录路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            
            if not input_path.exists():
                print(f"❌ 输入目录不存在: {input_dir}")
                return False
            
            # 创建输出目录
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 支持的图片格式
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            
            # 获取所有图片文件
            image_files = [f for f in input_path.iterdir() 
                          if f.suffix.lower() in image_extensions]
            
            if not image_files:
                print(f"❌ 在目录中未找到支持的图片文件: {input_dir}")
                return False
            
            print(f"📁 开始批量处理: 找到 {len(image_files)} 个图片文件")
            
            success_count = 0
            
            # 使用进度条批量处理
            for image_file in tqdm(image_files, desc="批量处理"):
                output_file = output_path / image_file.name
                if self.process_image(str(image_file), str(output_file)):
                    success_count += 1
            
            print(f"✅ 批量处理完成: 成功处理 {success_count}/{len(image_files)} 个文件")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 批量处理时出错: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="人脸自动打马赛克工具")
    
    # 基础参数
    parser.add_argument("--input", help="输入文件或目录路径")
    parser.add_argument("--output", help="输出文件或目录路径")
    parser.add_argument("--mosaic-size", type=int, default=20, help="马赛克块大小 (默认: 20)")
    parser.add_argument("--confidence", type=float, default=0.5, help="人脸检测置信度 (默认: 0.5)")
    parser.add_argument("--no-audio", action="store_true", help="不保留音频（仅输出视频）")
    
    # 批量处理参数
    parser.add_argument("--batch-folder", help="批量处理文件夹路径，处理文件夹内所有视频")
    parser.add_argument("--max-workers", type=int, default=4, help="最大并发处理数 (默认: 4)")
    
    args = parser.parse_args()
    
    # 参数验证
    if args.batch_folder:
        # 批量处理模式
        if not os.path.exists(args.batch_folder):
            print(f"❌ 批量处理文件夹不存在: {args.batch_folder}")
            sys.exit(1)
        if not os.path.isdir(args.batch_folder):
            print(f"❌ 批量处理路径不是文件夹: {args.batch_folder}")
            sys.exit(1)
    else:
        # 单文件处理模式
        if not args.input or not args.output:
            print("❌ 单文件模式需要指定 --input 和 --output 参数")
            sys.exit(1)
        if not os.path.exists(args.input):
            print(f"❌ 输入路径不存在: {args.input}")
            sys.exit(1)
    
    if args.confidence < 0 or args.confidence > 1:
        print("❌ 置信度必须在 0-1 之间")
        sys.exit(1)
    
    if args.mosaic_size < 1:
        print("❌ 马赛克大小必须大于 0")
        sys.exit(1)
    
    if args.max_workers < 1:
        print("❌ 最大并发数必须大于 0")
        sys.exit(1)
    
    # 创建处理器
    processor = FaceMosaicProcessor(
        confidence=args.confidence,
        mosaic_size=args.mosaic_size,
        preserve_audio=not args.no_audio
    )
    
    print("🚀 人脸自动打马赛克工具启动")
    print(f"⚙️  配置: 置信度={args.confidence}, 马赛克大小={args.mosaic_size}")
    
    try:
        if args.batch_folder:
            # 批量处理模式
            print(f"📁 批量处理模式: {args.batch_folder}")
            print(f"🔄 并发处理数: {args.max_workers}")
            
            stats = processor.process_video_batch(args.batch_folder, args.max_workers)
            
            if stats.get('total_files', 0) > 0:
                print("🎉 批量处理完成！")
            else:
                print("❌ 批量处理失败")
                sys.exit(1)
        else:
            # 单文件处理模式
            input_path = Path(args.input)
            
            if input_path.is_file():
                # 单文件处理
                if input_path.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}:
                    # 视频文件
                    success = processor.process_video(args.input, args.output)
                else:
                    # 图片文件
                    success = processor.process_image(args.input, args.output)
            
            elif input_path.is_dir():
                # 目录批量处理
                success = processor.process_directory(args.input, args.output)
            
            else:
                print(f"❌ 不支持的输入类型: {args.input}")
                success = False
            
            if success:
                print("🎉 处理完成！")
            else:
                print("❌ 处理失败")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  用户中断处理")
    except Exception as e:
        print(f"❌ 程序出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
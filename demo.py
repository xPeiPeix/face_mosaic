#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸马赛克工具演示脚本
快速测试摄像头实时处理功能
"""

import cv2
from face_mosaic import FaceMosaicProcessor


def real_time_demo():
    """实时摄像头演示"""
    print("🎥 启动实时人脸马赛克演示")
    print("按 'q' 键退出，按 's' 键截图保存")
    
    # 初始化处理器
    processor = FaceMosaicProcessor(confidence=0.5, mosaic_size=15)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    screenshot_count = 0
    
    try:
        while True:
            # 读取帧
            ret, frame = cap.read()
            if not ret:
                print("❌ 无法读取摄像头画面")
                break
            
            # 处理人脸
            processed_frame, face_count = processor.detect_and_mosaic_faces(frame)
            
            # 显示信息
            info_text = f"Faces: {face_count} | Press 'q' to quit, 's' to save"
            cv2.putText(processed_frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示画面
            cv2.imshow('Real-time Face Mosaic Demo', processed_frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                screenshot_count += 1
                filename = f"screenshot_{screenshot_count:03d}.jpg"
                cv2.imwrite(filename, processed_frame)
                print(f"📸 截图已保存: {filename}")
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    
    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()
        print("👋 演示结束")


def batch_demo():
    """批量处理演示"""
    import os
    from pathlib import Path
    
    print("📁 批量处理演示")
    
    # 创建示例目录
    demo_dir = Path("demo_images")
    output_dir = Path("demo_output")
    
    if not demo_dir.exists():
        print(f"❌ 演示目录不存在: {demo_dir}")
        print("请在 demo_images 目录中放入一些图片文件进行测试")
        return
    
    # 初始化处理器
    processor = FaceMosaicProcessor(confidence=0.6, mosaic_size=25)
    
    # 批量处理
    success = processor.process_directory(str(demo_dir), str(output_dir))
    
    if success:
        print(f"✅ 批量处理完成，结果保存在: {output_dir}")
    else:
        print("❌ 批量处理失败")


def main():
    """主函数"""
    print("🚀 人脸马赛克工具演示")
    print("1. 实时摄像头演示")  
    print("2. 批量处理演示")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请选择演示模式 (0-2): ").strip()
            
            if choice == '1':
                real_time_demo()
            elif choice == '2':
                batch_demo()
            elif choice == '0':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 0-2")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 出错了: {e}")


if __name__ == "__main__":
    main() 
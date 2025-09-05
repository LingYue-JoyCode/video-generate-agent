#!/usr/bin/env python3
"""
测试新的异步任务管理功能
"""
import asyncio
import json
from utils.task_manager import task_manager

async def test_task_manager():
    """测试任务管理器功能"""
    print("🧪 开始测试异步任务管理器...")
    
    # 创建测试场景数据
    test_scenes = [
        {"sd_prompt": "A beautiful landscape with mountains and lakes"},
        {"sd_prompt": "A futuristic city at sunset"},
        {"sd_prompt": "A magical forest with glowing trees"}
    ]
    
    # 提交图片生成任务
    print("📝 提交图片生成任务...")
    task_id = await task_manager.submit_image_generation_task(test_scenes)
    print(f"✅ 任务已提交，ID: {task_id}")
    
    # 监控任务状态
    print("🔍 开始监控任务状态...")
    while True:
        task = task_manager.get_task(task_id)
        if task:
            print(f"📊 任务状态: {task.status.value}, 进度: {task.progress:.1f}%")
            
            if task.status.value == "completed":
                print("🎉 任务完成！")
                print(f"📋 结果: {json.dumps(task.result, ensure_ascii=False, indent=2)}")
                break
            elif task.status.value == "failed":
                print(f"❌ 任务失败: {task.error_message}")
                break
        
        # 等待2秒再查询
        await asyncio.sleep(2)
    
    # 测试视频合成任务
    print("\n🎬 提交视频合成任务...")
    video_task_id = await task_manager.submit_video_composition_task()
    print(f"✅ 视频任务已提交，ID: {video_task_id}")
    
    # 监控视频任务
    print("🔍 开始监控视频任务状态...")
    while True:
        task = task_manager.get_task(video_task_id)
        if task:
            print(f"📊 视频任务状态: {task.status.value}, 进度: {task.progress:.1f}%")
            
            if task.status.value == "completed":
                print("🎉 视频任务完成！")
                print(f"📋 结果: {json.dumps(task.result, ensure_ascii=False, indent=2)}")
                break
            elif task.status.value == "failed":
                print(f"❌ 视频任务失败: {task.error_message}")
                break
        
        await asyncio.sleep(3)
    
    # 显示所有任务状态
    print("\n📋 所有任务状态:")
    all_tasks = task_manager.get_all_tasks_status()
    for task in all_tasks:
        print(f"- {task['task_id']}: {task['status']} ({task['progress']:.1f}%)")


if __name__ == "__main__":
    asyncio.run(test_task_manager())

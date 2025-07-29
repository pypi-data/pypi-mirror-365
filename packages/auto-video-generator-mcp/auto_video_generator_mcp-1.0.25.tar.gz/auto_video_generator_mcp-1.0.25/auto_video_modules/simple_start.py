#!/usr/bin/env python3
"""
简化的MCP服务器启动脚本 - 避免复杂依赖
"""
import sys
import os

def main():
    print("启动自动视频生成MCP服务器 v3.0...")
    print("服务器包含以下功能:")
    print("- 核心视频生成功能")
    print("- 配置获取工具")
    print("\n使用 get_all_available_tools 查看所有可用工具")
    print("服务器将以SSE方式运行")
    print("访问地址: http://localhost:8000/sse")
    
    try:
        # 延迟导入，避免启动时的依赖问题
        print("正在加载核心模块...")
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("auto-video-generator", log_level="INFO")
        
        print("正在注册工具...")
        
        try:
            from auto_video_modules.mcp_tools import (
                generate_auto_video_mcp, generate_auto_video_sync, generate_auto_video_async,
                get_task_status, list_all_tasks, cancel_task, get_system_status,
                get_available_voice_options, validate_input_parameters, get_generation_estimate
            )
            mcp.tool()(generate_auto_video_mcp)
            mcp.tool()(generate_auto_video_sync)
            mcp.tool()(generate_auto_video_async)
            mcp.tool()(get_task_status)
            mcp.tool()(list_all_tasks)
            mcp.tool()(cancel_task)
            mcp.tool()(get_system_status)
            mcp.tool()(get_available_voice_options)
            mcp.tool()(validate_input_parameters)
            mcp.tool()(get_generation_estimate)
            print("✓ 核心工具注册完成")
        except Exception as e:
            print(f"⚠ 警告: 核心工具加载失败: {e}")
        
        try:
            from auto_video_modules.mcp_tools import generate_srt_from_whisper_mcp, clip_video_by_srt_mcp
            mcp.tool()(generate_srt_from_whisper_mcp)
            mcp.tool()(clip_video_by_srt_mcp)
            print("✓ Whisper工具注册完成")
        except Exception as e:
            print(f"⚠ 警告: Whisper工具加载失败: {e}")
        
        try:
            from auto_video_modules.ffmpeg_utils import check_gpu_acceleration
            mcp.tool()(check_gpu_acceleration)
            print("✓ GPU加速工具注册完成")
        except Exception as e:
            print(f"⚠ 警告: GPU加速工具加载失败: {e}")
        
        try:
            from auto_video_modules.motion_detection_utils import detect_video_motion, optimize_video_motion_params
            mcp.tool()(detect_video_motion)
            mcp.tool()(optimize_video_motion_params)
            print("✓ 运动检测工具注册完成")
        except Exception as e:
            print(f"⚠ 警告: 运动检测工具加载失败: {e}")
        
        try:
            from auto_video_modules.gpu_optimization_utils import get_system_performance_info, optimize_video_processing, benchmark_gpu_performance
            mcp.tool()(get_system_performance_info)
            mcp.tool()(optimize_video_processing)
            mcp.tool()(benchmark_gpu_performance)
            print("✓ GPU优化工具注册完成")
        except Exception as e:
            print(f"⚠ 警告: GPU优化工具加载失败: {e}")
        
        print("所有工具加载完成！")
        print("服务器启动中...")
        mcp.run(transport='sse')
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
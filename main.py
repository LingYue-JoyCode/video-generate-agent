# 导入日志监控库logfire
import logfire
import asyncio

# 导入主控制器
from agents.main_agent import start_video_generation

# 配置logfire日志监控
logfire.configure()
# 对pydantic_ai进行监控
logfire.instrument_pydantic_ai()


async def main():
    """
    主函数 - AI视频生成系统入口
    """
    print("🎬 欢迎使用AI视频生成系统!")
    print("=" * 50)
    
    # 示例大纲 - 用户可以修改这个大纲
    sample_outline = """
    翠花是一个孤儿，生活在一个a镇中，她被一个普通人家收养。
    但是她的父母却经常欺负他，她有一个姐姐，对她也很苛刻，什么事儿都让翠花来做。
    并且还姐姐做了什么坏事还让翠花背锅。

    但突然有一天，小镇中的年轻富少遇见了翠花，惊奇的发现翠花竟然和她已故的妹妹有着惊人的相似之处。
    在富少的调查下，发现翠花其实是他的亲妹妹。
    他也了解了翠花的处境，以及她在养父母家中所遭受的虐待。

    翠花的逆袭之路由此开始。
    """
    
    # 用户配置区域
    print("📝 当前使用的故事大纲:")
    print("-" * 30)
    print(sample_outline)
    print("-" * 30)
    
    # 配置生成参数
    start_chapter = 1  # 开始章节
    end_chapter = 1    # 结束章节（可以设置为3来生成所有章节）
    
    print("🎯 生成设置:")
    print(f"   开始章节: 第{start_chapter}章")
    print(f"   结束章节: 第{end_chapter}章")
    print("=" * 50)
    
    # 启动AI视频生成
    result = await start_video_generation(
        outline=sample_outline,
        start_chapter=start_chapter,
        end_chapter=end_chapter,
        requirement="情节跌宕起伏，要体现出复仇的爽感，要有甜宠剧的风格和逆袭剧的风格，这个剧情的受众群体是女性，请结合这些要素进行生成。"
    )
    
    print("\n" + "=" * 50)
    print("📋 生成结果:")
    print(result)
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

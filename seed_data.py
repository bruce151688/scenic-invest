"""种子数据脚本 - 预填充示例景区二消产品"""
import sys
sys.path.insert(0, "backend")

from database import SessionLocal, init_db
from models import Product, ProductImage, ProductVideo, Category, Source
from auth import hash_password
from models import User, UserRole

def seed():
    init_db()
    db = SessionLocal()

    # 检查是否已有数据
    if db.query(Product).count() > 0:
        print("已有产品数据，跳过种子数据")
        db.close()
        return

    # 创建示例产品
    products_data = [
        {
            "title": "悬崖网红秋千 - 景区高空体验项目",
            "description": """产品概述：建在悬崖边的高空秋千，将游客荡出悬崖边缘，体验极致刺激。

技术参数：
- 秋千高度：5-15米可定制
- 承载人数：1-4人/次
- 安全认证：CE/ISO9001
- 占地面积：约30㎡

投资分析：
- 设备投资：15-30万
- 日均接待：200-500人次
- 票价建议：30-60元/人
- 回本周期：3-6个月
- 年利润预估：50-150万

适合场景：山岳景区、峡谷景区、主题乐园，
是当前景区引流利器，短视频传播效果好。""",
            "category_id": 2,  # 户外探险
            "invest_range": "15-50万",
            "price_range": "30-60元/人",
            "contact_info": {
                "phone": "13888880001",
                "wechat": "cliff_swing888",
                "email": "sales@cliffswing.cn",
                "website": "https://www.cliffswing.cn"
            },
            "location": {"province": "浙江", "city": "温州", "scenic_name": "雁荡山景区"},
            "tags": ["悬崖秋千", "网红打卡", "高空体验", "短视频爆款", "回本快"],
            "source_url": "https://www.cliffswing.cn/products/cliff-swing"
        },
        {
            "title": "沉浸式光影互动体验馆 - 全息投影科技项目",
            "description": """产品概述：利用全息投影、动作捕捉、互动感应等技术，
打造沉浸式光影互动体验空间，适合景区室内/半室内场地。

项目内容：
- 互动投影地面/墙面
- 全息剧场（裸眼3D）
- 光影互动绘画
- 沉浸式光影隧道
- AR互动拍照

投资分析：
- 设备投资：50-200万（视面积和内容而定）
- 日均接待：500-2000人次
- 票价建议：50-120元/人
- 回本周期：8-18个月
- 年利润预估：200-500万
- 内容更新频率：建议每年更新30%

优势：不受天气影响，全年运营，适合各类景区。""",
            "category_id": 1,  # 科技互动
            "invest_range": "50-200万",
            "price_range": "50-120元/人",
            "contact_info": {
                "phone": "13999990002",
                "wechat": "immersive_light",
                "email": "info@immersivelight.cn",
                "website": "https://www.immersivelight.cn"
            },
            "location": {"province": "广东", "city": "深圳", "scenic_name": "适用于各类景区"},
            "tags": ["全息投影", "沉浸式体验", "科技互动", "室内项目", "全年运营"],
            "source_url": "https://www.immersivelight.cn/cases"
        },
        {
            "title": "彩虹滑道/七彩滑道 - 亲子网红游乐设施",
            "description": """产品概述：色彩鲜艳的多人滑道项目，
适合亲子家庭和年轻人群，是近年景区最火爆的二消项目之一。

技术参数：
- 滑道长度：50-200米
- 滑道数量：3-8条可选
- 材质：HDPE/玻璃钢
- 占地面积：500-2000㎡
- 使用寿命：5-8年

投资分析：
- 设备投资：20-80万
- 日均接待：300-1000人次
- 票价建议：20-50元/人
- 回本周期：3-8个月
- 年利润预估：80-300万

适合场景：坡度地形、山坡、草原景区，
色彩鲜艳适合拍照传播。""",
            "category_id": 4,  # 亲子游乐
            "invest_range": "20-80万",
            "price_range": "20-50元/人",
            "contact_info": {
                "phone": "13777770003",
                "wechat": "rainbow_slide",
                "email": "rainbow@slidepark.cn"
            },
            "location": {"province": "河南", "city": "郑州", "scenic_name": "适用于各类景区"},
            "tags": ["彩虹滑道", "亲子项目", "网红设施", "投资门槛低", "回本快"],
            "source_url": "https://example.com/rainbow-slide"
        },
        {
            "title": "星空泡泡屋/透明帐篷 - 景区特色住宿",
            "description": """产品概述：全透明PVC材质泡泡屋，让游客躺在床上看星空，
是景区高端住宿的网红产品。

规格参数：
- 直径：3-6米可选
- 材质：抗UV透明PVC
- 配置：空调/地暖/独立卫浴
- 抗风等级：8级
- 使用寿命：3-5年

投资分析：
- 单间投资：3-8万
- 建议配置：10-30间
- 房价：300-1500元/晚
- 入住率：60-85%
- 回本周期：6-12个月
- 年利润预估：50-200万

适合场景：山顶、草原、湖边、花海景区，
特别适合观星、日出、云海等自然景观区域。""",
            "category_id": 8,  # 星空帐篷
            "invest_range": "30-200万",
            "price_range": "300-1500元/晚",
            "contact_info": {
                "phone": "13666660004",
                "wechat": "bubble_house",
                "email": "info@bubblehouse.cn",
                "website": "https://www.bubblehouse.cn"
            },
            "location": {"province": "云南", "city": "丽江", "scenic_name": "玉龙雪山景区"},
            "tags": ["泡泡屋", "星空帐篷", "特色住宿", "网红民宿", "高端体验"],
            "source_url": "https://www.bubblehouse.cn/products"
        },
        {
            "title": "丛林穿越/树上探险 - 户外运动项目",
            "description": """产品概述：在树林间搭建的空中探险项目，
包含绳网、独木桥、滑索、攀爬等关卡，
适合团建、亲子、户外运动爱好者。

项目特点：
- 关卡数量：15-60关可选
- 难度等级：初级/中级/高级/专业
- 安全标准：EN15567欧盟标准
- 占地面积：500-5000㎡
- 容纳人数：50-200人同时体验

投资分析：
- 设备投资：30-150万
- 日均接待：200-600人次
- 票价建议：60-150元/人
- 回本周期：6-15个月
- 年利润预估：100-400万

适合场景：森林景区、山地景区、度假村。""",
            "category_id": 2,
            "invest_range": "30-150万",
            "price_range": "60-150元/人",
            "contact_info": {
                "phone": "13555550005",
                "wechat": "tree_adventure",
                "email": "sales@treeadventure.cn"
            },
            "location": {"province": "四川", "city": "成都", "scenic_name": "青城山景区"},
            "tags": ["丛林穿越", "户外探险", "团建项目", "亲子互动", "树上项目"],
            "source_url": "https://example.com/tree-adventure"
        },
        {
            "title": "玻璃水滑道 - 高空玻璃漂流项目",
            "description": """产品概述：建在山体上的玻璃滑道，
结合漂流和玻璃栈道特点，
游客乘坐皮筏从高处滑下，360°全透明视野。

技术参数：
- 长度：500-3000米
- 落差：30-200米
- 材质：三层夹胶钢化玻璃
- 承载量：500-2000人/小时
- 使用寿命：20年以上

投资分析：
- 设备投资：200-1000万
- 日均接待：1000-5000人次
- 票价建议：80-180元/人
- 回本周期：8-18个月
- 年利润预估：500-2000万

优势：一次投入长期收益，且玻璃滑道本身就是景观。""",
            "category_id": 3,  # 水上项目
            "invest_range": "200-1000万",
            "price_range": "80-180元/人",
            "contact_info": {
                "phone": "13444440006",
                "wechat": "glass_slide",
                "email": "info@glassslide.cn",
                "website": "https://www.glassslide.cn"
            },
            "location": {"province": "湖南", "city": "张家界", "scenic_name": "张家界景区"},
            "tags": ["玻璃水滑道", "高空漂流", "大型投资", "地标项目", "高回报"],
            "source_url": "https://www.glassslide.cn/projects"
        },
        {
            "title": "无动力亲子乐园 - 自然教育游乐场",
            "description": """产品概述：不使用电力驱动的游乐设施集合，
包括攀爬网、滑梯、秋千、沙池、蹦床、
平衡木、迷宫等，强调自然探索和体能发展。

设施清单：
- 大型组合滑梯
- 攀爬网/绳塔
- 多人秋千
- 蹦床/蹦极
- 沙池/泥坑
- 树屋/木屋
- 迷宫/探索区

投资分析：
- 设备投资：30-120万
- 占地面积：1000-10000㎡
- 日均接待：300-2000人次
- 票价建议：30-80元/人
- 回本周期：4-10个月
- 年利润预估：60-300万

优势：维护成本低、安全性高、复购率强。""",
            "category_id": 4,
            "invest_range": "30-120万",
            "price_range": "30-80元/人",
            "contact_info": {
                "phone": "13333330007",
                "wechat": "nature_play",
                "email": "hello@natureplay.cn"
            },
            "location": {"province": "北京", "city": "北京", "scenic_name": "适用于各类景区"},
            "tags": ["无动力乐园", "亲子", "自然教育", "低维护", "安全"],
            "source_url": "https://example.com/nature-play"
        },
        {
            "title": "实景水秀/光影水舞秀 - 夜间演艺项目",
            "description": """产品概述：结合音乐喷泉、水幕投影、激光、
灯光、火焰特效的大型夜间水秀演出，
是景区夜间经济的核心产品。

演出参数：
- 演出时长：15-45分钟
- 水幕尺寸：30-200米宽
- 喷泉高度：最高80米
- 投影设备：激光投影/工程投影
- 观众容量：1000-20000人

投资分析：
- 建设投资：300-3000万
- 运营成本：每场2000-10000元
- 票价建议：80-280元/人
- 日均场次：1-3场
- 回本周期：12-24个月
- 年利润预估：500-3000万

适合场景：湖滨景区、古镇景区、主题公园，
可大幅延长游客停留时间和过夜率。""",
            "category_id": 25,  # 光影水秀
            "invest_range": "300-3000万",
            "price_range": "80-280元/人",
            "contact_info": {
                "phone": "13222220008",
                "wechat": "water_show",
                "email": "info@watershow.cn",
                "website": "https://www.watershow.cn"
            },
            "location": {"province": "浙江", "city": "杭州", "scenic_name": "西湖景区"},
            "tags": ["水秀", "光影秀", "夜间经济", "大型演艺", "沉浸式"],
            "source_url": "https://www.watershow.cn/cases"
        },
    ]

    for data in products_data:
        product = Product(
            title=data["title"],
            description=data["description"],
            category_id=data["category_id"],
            invest_range=data["invest_range"],
            price_range=data["price_range"],
            contact_info=data["contact_info"],
            location=data["location"],
            tags=data["tags"],
            source_url=data.get("source_url", ""),
            status="active",
        )
        db.add(product)

    db.commit()
    print(f"已创建 {len(products_data)} 个示例产品")

    # 添加示例抓取源
    sources = [
        {"name": "中国游乐设备网", "url": "https://www.zgyle.com/product/", "notes": "游乐设备行业门户"},
        {"name": "B站-景区游乐项目搜索", "url": "https://search.bilibili.com/all?keyword=景区游乐项目投资", "notes": "B站视频搜索"},
        {"name": "淘宝-景区设备供应商", "url": "https://s.taobao.com/search?q=景区游乐设备", "notes": "淘宝供应商搜索"},
        {"name": "微信公众号搜索", "url": "https://weixin.sogou.com/weixin?type=2&query=景区二消项目", "notes": "通过搜狗搜索微信公众号文章"},
        {"name": "小红书-景区种草", "url": "https://www.xiaohongshu.com/search_result?keyword=景区游乐项目", "notes": "小红书搜索景区项目种草笔记"},
        {"name": "抖音-景区项目短视频", "url": "https://www.douyin.com/search/景区游乐项目", "notes": "抖音短视频搜索"},
    ]

    for src_data in sources:
        source = Source(**src_data)
        db.add(source)

    db.commit()
    print(f"已添加 {len(sources)} 个抓取源")

    db.close()
    print("种子数据初始化完成！")


if __name__ == "__main__":
    seed()

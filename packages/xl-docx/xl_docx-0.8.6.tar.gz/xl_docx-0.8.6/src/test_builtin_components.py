#!/usr/bin/env python3
"""
测试内置组件库功能
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from xl_docx import Sheet
from xl_docx.components import get_builtin_components, get_component_content

def test_builtin_components():
    """测试内置组件库功能"""
    print("=== 测试内置组件库 ===")
    
    # 1. 测试获取内置组件列表
    print("\n1. 获取内置组件列表:")
    components = get_builtin_components()
    for name, path in components.items():
        print(f"  - {name}: {path}")
    
    # 2. 测试获取组件内容
    print("\n2. 测试获取组件内容:")
    for component_name in components.keys():
        content = get_component_content(component_name)
        if content:
            print(f"  - {component_name}: 内容长度 {len(content)} 字符")
        else:
            print(f"  - {component_name}: 获取失败")
    
    # 3. 测试Sheet对象的内置组件功能
    print("\n3. 测试Sheet对象的内置组件功能:")
    
    # 创建测试模板
    test_template = """
    <w:document mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14"
  xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink"
  xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d"
  xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex"
  xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex"
  xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex"
  xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex"
  xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex"
  xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex"
  xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex"
  xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex"
  xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex"
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  xmlns:oel="http://schemas.microsoft.com/office/2019/extlst"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  xmlns:v="urn:schemas-microsoft-com:vml"
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:w10="urn:schemas-microsoft-com:office:word"
  xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
  xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"
  xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml"
  xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex"
  xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid"
  xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du"
  xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash"
  xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock"
  xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex"
  xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
  xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
  xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
  xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
  xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
  xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
  xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
  <w:body>
    <page-break/>
  </w:body>
</w:document>
    """
    
    try:
        # 创建Sheet对象（不设置component_folder）
        sheet = Sheet("assets/h.docx")  # 使用现有的Word文件作为模板
        
        # 渲染模板
        result = sheet.render_template(test_template, {})
        print(result)
        
        print("  模板渲染成功！")
        print(f"  结果长度: {len(result)} 字符")
        print("  结果预览:")
        print("  " + result[:200] + "..." if len(result) > 200 else "  " + result)
        
    except Exception as e:
        raise e
        print(f"  渲染失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_builtin_components() 
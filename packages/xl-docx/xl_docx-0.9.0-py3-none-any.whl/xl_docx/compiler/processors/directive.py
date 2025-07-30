from xl_docx.compiler.processors.base import BaseProcessor
import re


class DirectiveProcessor(BaseProcessor):
    """处理Vue指令相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    V_IF_PATTERN = r'''
        <([^>]*)                     # 标签名和属性
        \s+v-if="([^"]*)"           # v-if指令
        ([^>]*)>                     # 剩余属性
    '''
    
    V_FOR_PATTERN = r'''
        <([^>]*)                     # 标签名和属性
        \s+v-for="([^"]*)"          # v-for指令
        ([^>]*)>                     # 剩余属性
    '''
    
    # Jinja2模板模式
    JINJA_IF_PATTERN = r'''
        {%\s*if\s+                   # 开始if标签
        ([^%]+)                      # 条件表达式
        \s*%}                        # 结束标签
        (.*?)                        # 内容（非贪婪匹配）
        {%\s*endif\s*%}              # 结束if标签
    '''
    
    JINJA_FOR_PATTERN = r'''
        {%\s*for\s+                  # 开始for标签
        ([^%]+)                      # 循环表达式
        \s*%}                        # 结束标签
        (.*?)                        # 内容（非贪婪匹配）
        {%\s*endfor\s*%}             # 结束for标签
    '''
    
    # 标签匹配模式
    TAG_WITH_ATTRS_PATTERN = r'''
        <([^\s>]+)                   # 标签名
        ([^>]*)>                     # 属性
        (.*)                         # 内容
        </\1>                        # 结束标签
    '''
    
    @classmethod
    def compile(cls, xml: str) -> str:
        xml = cls._process_v_if(xml)
        xml = cls._process_v_for(xml)
        return xml
        
    @classmethod
    def _process_v_if(cls, xml: str) -> str:
        def process_if(match):
            tag_name, condition, remaining_attrs = match.groups()
            # 构建结束标签的正则表达式
            close_tag_pattern = f'</\s*{tag_name}\s*>'
            close_match = re.search(close_tag_pattern, xml[match.end():])
            if close_match:
                # 提取开始标签和结束标签之间的内容
                content_between = xml[match.end():match.end() + close_match.start()]
                return f'{{% if {condition} %}}<{tag_name}{remaining_attrs}>{content_between}</{tag_name}>{{% endif %}}'
            return match.group(0)
            
        result = cls._process_tag(xml, cls.V_IF_PATTERN, process_if)
        return result

    @classmethod
    def _process_v_for(cls, xml: str) -> str:
        def process_for(match):
            tag_name, loop_expr, remaining_attrs = match.groups()
            # 解析循环表达式：item in items
            item, items = loop_expr.split(' in ')
            item = item.strip()
            items = items.strip()
            
            # 构建结束标签的正则表达式
            close_tag_pattern = f'</\s*{tag_name}\s*>'
            close_match = re.search(close_tag_pattern, xml[match.end():])
            if close_match:
                # 提取开始标签和结束标签之间的内容
                content_between = xml[match.end():match.end() + close_match.start()]
                return f'{{% for {item} in {items} %}}<{tag_name}{remaining_attrs}>{content_between}</{tag_name}>{{% endfor %}}'
            return match.group(0)
            
        return cls._process_tag(xml, cls.V_FOR_PATTERN, process_for)

    @classmethod
    def decompile2222222222222222222222(cls, xml: str) -> str:
        """将Jinja2模板转换回Vue指令"""
        xml = cls._decompile_v_if(xml)
        xml = cls._decompile_v_for(xml)
        return xml

    @classmethod
    def _decompile_v_if(cls, xml: str) -> str:
        def process_if(match):
            condition, tag_content = match.groups()
            # 提取标签名和属性
            tag_match = re.match(cls.TAG_WITH_ATTRS_PATTERN, tag_content, flags=re.VERBOSE)
            if tag_match:
                tag_name, attrs, content = tag_match.groups()
                return f'<{tag_name} v-if="{condition}"{attrs}>{content}</{tag_name}>'
            return match.group(0)

        return cls._process_tag(xml, cls.JINJA_IF_PATTERN, process_if)

    @classmethod
    def _decompile_v_for(cls, xml: str) -> str:
        def process_for(match):
            loop_expr, tag_content = match.groups()
            # 提取标签名和属性
            tag_match = re.match(cls.TAG_WITH_ATTRS_PATTERN, tag_content, flags=re.VERBOSE)
            if tag_match:
                tag_name, attrs, content = tag_match.groups()
                # 解析循环表达式
                item, items = loop_expr.split(' in ')
                return f'<{tag_name} v-for="{item.strip()} in {items.strip()}"{attrs}>{content}</{tag_name}>'
            return match.group(0)

        return cls._process_tag(xml, cls.JINJA_FOR_PATTERN, process_for)
